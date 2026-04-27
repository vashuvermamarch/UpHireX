import hashlib
import logging
from datetime import datetime, timezone, timedelta

import jwt
from django.conf import settings
from django.core.cache import cache
from django.utils import timezone as dj_timezone
from random import randint

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny

from uphirex.utils import api_response
from uphirex.email_utils import send_otp_email
from .models import User, RefreshToken, SessionAudit
from .serializers import UserRegistrationSerializer, UserSerializer, UserUpdateSerializer
from .custom_tokens import CustomRefreshToken
from .decorators import require_role, IsAdmin, IsHROrAdmin

logger = logging.getLogger(__name__)


def get_client_ip(request):
    x_forwarded = request.META.get('HTTP_X_FORWARDED_FOR')
    return x_forwarded.split(',')[0] if x_forwarded else request.META.get('REMOTE_ADDR')


class AuthViewSet(viewsets.GenericViewSet):
    """Authentication endpoints: signup, verify, login, logout, refresh."""

    serializer_class = UserRegistrationSerializer

    def get_permissions(self):
        if self.action in ['signup', 'verify_signup', 'login']:
            return [AllowAny()]
        return [IsAuthenticated()]

    # ── SIGNUP ────────────────────────────────────────
    @action(detail=False, methods=['post'])
    def signup(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not serializer.is_valid():
            return api_response(False, "Invalid data.", serializer.errors, status.HTTP_400_BAD_REQUEST)

        email = serializer.validated_data['email']
        username = serializer.validated_data['username']

        if User.objects.filter(email=email).exists():
            return api_response(False, "Email already exists.", status_code=status.HTTP_400_BAD_REQUEST)
        if User.objects.filter(username=username).exists():
            return api_response(False, "Username already exists.", status_code=status.HTTP_400_BAD_REQUEST)

        otp = str(randint(100000, 999999))
        cache.set(f'otp_signup_{email}', {"otp": otp, "data": serializer.validated_data}, timeout=300)

        # Send OTP via email
        send_otp_email(email, otp)

        return api_response(True, "OTP sent successfully.", {
            "email": email
        }, status.HTTP_200_OK)

    # ── VERIFY SIGNUP ─────────────────────────────────
    @action(detail=False, methods=['post'])
    def verify_signup(self, request):
        email = request.data.get("email")
        otp = request.data.get("otp")

        stored = cache.get(f'otp_signup_{email}')
        if not stored or stored["otp"] != otp:
            return api_response(False, "Invalid or expired OTP.", status_code=status.HTTP_400_BAD_REQUEST)

        serializer = UserRegistrationSerializer(data=stored["data"])
        if not serializer.is_valid():
            return api_response(False, "Error creating user.", serializer.errors, status.HTTP_400_BAD_REQUEST)

        user = serializer.save()
        user.email_verified = True

        # HR requires admin activation
        if user.role == User.Role.HR:
            user.is_active = False

        user.save()
        cache.delete(f'otp_signup_{email}')

        # Generate signup token
        signup_token = jwt.encode(
            {"user_id": str(user.id), "email": user.email, "role": user.role,
             "iat": datetime.now(timezone.utc)},
            settings.SECRET_KEY, algorithm="HS256",
        )

        return api_response(True, "Signup verified.", {
            "user": UserSerializer(user).data,
            "signup_token": signup_token,
        }, status.HTTP_201_CREATED)

    # ── LOGIN ─────────────────────────────────────────
    @action(detail=False, methods=['post'])
    def login(self, request):
        email = request.data.get("email")
        password = request.data.get("password")

        if not email or not password:
            return api_response(False, "Email and password required.", status_code=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return api_response(False, "User not found.", status_code=status.HTTP_404_NOT_FOUND)

        # Account lock check
        if user.account_locked_until and user.account_locked_until > dj_timezone.now():
            return api_response(False, "Account locked. Try again later.", status_code=status.HTTP_403_FORBIDDEN)

        if not user.check_password(password):
            user.failed_login_attempts += 1
            if user.failed_login_attempts >= 5:
                user.account_locked_until = dj_timezone.now() + timedelta(minutes=15)
            user.save(update_fields=['failed_login_attempts', 'account_locked_until'])

            SessionAudit.objects.create(
                user=user, ip_address=get_client_ip(request),
                user_agent=request.META.get('HTTP_USER_AGENT', ''), success=False,
            )
            return api_response(False, "Invalid password.", status_code=status.HTTP_400_BAD_REQUEST)

        if not user.email_verified:
            return api_response(False, "Email not verified.", status_code=status.HTTP_403_FORBIDDEN)

        if not user.is_active:
            return api_response(False, "Account not active. Please wait for admin activation.",
                                status_code=status.HTTP_403_FORBIDDEN)

        # Reset failed attempts
        user.failed_login_attempts = 0
        user.account_locked_until = None
        user.last_login = dj_timezone.now()
        user.save(update_fields=['failed_login_attempts', 'account_locked_until', 'last_login'])

        # Generate JWT
        refresh = CustomRefreshToken.for_user(user)
        token_str = str(refresh)
        token_hash = hashlib.sha256(token_str.encode()).hexdigest()

        RefreshToken.objects.create(
            user=user, token_hash=token_hash,
            expires_at=dj_timezone.now() + settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME'],
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''),
        )

        SessionAudit.objects.create(
            user=user, ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', ''), success=True,
        )

        return api_response(True, "Login successful.", {
            "user": UserSerializer(user).data,
            "refresh": token_str,
            "access": str(refresh.access_token),
        }, status.HTTP_200_OK)

    # ── LOGOUT ────────────────────────────────────────
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        refresh_token = request.data.get("refresh")
        if not refresh_token:
            return api_response(False, "Refresh token required.", status_code=status.HTTP_400_BAD_REQUEST)

        token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
        try:
            rt = RefreshToken.objects.get(user=request.user, token_hash=token_hash)
            rt.is_revoked = True
            rt.save(update_fields=['is_revoked'])
            return api_response(True, "Logged out successfully.", status_code=status.HTTP_200_OK)
        except RefreshToken.DoesNotExist:
            return api_response(False, "Invalid refresh token.", status_code=status.HTTP_400_BAD_REQUEST)

    # ── PROTECTED VIEW ────────────────────────────────
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def me(self, request):
        return api_response(True, "Authenticated user.", UserSerializer(request.user).data, status.HTTP_200_OK)

    # ── USER LOOKUP ───────────────────────────────────
    @action(detail=False, methods=['get'], url_path=r'user/(?P<user_id>[^/.]+)')
    def user_data(self, request, user_id=None):
        try:
            user = User.objects.get(id=user_id)
            return api_response(True, "User found.", UserSerializer(user).data, status.HTTP_200_OK)
        except (User.DoesNotExist, ValueError):
            return api_response(False, "User not found.", status_code=status.HTTP_404_NOT_FOUND)


class UserViewSet(viewsets.ModelViewSet):
    """Admin-only user management."""

    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsHROrAdmin]

    def get_queryset(self):
        return User.objects.select_related('organization_id').all()

    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = UserUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return api_response(True, "User updated.", UserSerializer(user).data, status.HTTP_200_OK)

    def destroy(self, request, *args, **kwargs):
        if request.user.role != 'admin':
            return api_response(False, "Only admin can delete users.", status_code=status.HTTP_403_FORBIDDEN)
        user = self.get_object()
        user.is_active = False
        user.save(update_fields=['is_active'])
        return api_response(True, "User deactivated.", status_code=status.HTTP_200_OK)
