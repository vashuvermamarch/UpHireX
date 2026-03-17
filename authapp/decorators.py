from functools import wraps
from rest_framework import permissions, status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.exceptions import AuthenticationFailed
from uphirex.utils import api_response


# ═══════════════════════════════════════════════════════
# DRF PERMISSION CLASSES
# ═══════════════════════════════════════════════════════

class IsAuthenticated(permissions.BasePermission):
    """Ensure user is authenticated via JWT."""

    def has_permission(self, request, view):
        return request.user and request.user.is_authenticated


class IsAdmin(permissions.BasePermission):
    """Only admin role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'admin'
        )


class IsHR(permissions.BasePermission):
    """Only HR role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'hr'
        )


class IsJobSeeker(permissions.BasePermission):
    """Only job_seeker role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role == 'job_seeker'
        )


class IsHROrAdmin(permissions.BasePermission):
    """HR or Admin role."""

    def has_permission(self, request, view):
        return (
            request.user
            and request.user.is_authenticated
            and request.user.role in ('hr', 'admin')
        )


class IsOwnerOrAdmin(permissions.BasePermission):
    """Object owner OR admin can access."""

    def has_object_permission(self, request, view, obj):
        if request.user.role == 'admin':
            return True
        # Check common ownership patterns
        if hasattr(obj, 'user') and obj.user == request.user:
            return True
        if hasattr(obj, 'user_id') and obj.user_id == request.user.id:
            return True
        if hasattr(obj, 'posted_by') and obj.posted_by == request.user:
            return True
        if hasattr(obj, 'sender') and obj.sender == request.user:
            return True
        return obj == request.user


class IsOwner(permissions.BasePermission):
    """Only the resource owner."""

    def has_object_permission(self, request, view, obj):
        if hasattr(obj, 'user'):
            return obj.user == request.user
        if hasattr(obj, 'posted_by'):
            return obj.posted_by == request.user
        return obj == request.user


# ═══════════════════════════════════════════════════════
# FUNCTION DECORATOR: require_role
# ═══════════════════════════════════════════════════════

def require_role(allowed_roles):
    """
    Decorator for function-based or ViewSet action methods.

    Usage:
        @require_role(["hr", "admin"])
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request_or_self, *args, **kwargs):
            # Handle both ViewSet methods (self, request) and plain views (request)
            if hasattr(request_or_self, 'request'):
                request = request_or_self.request
            elif hasattr(request_or_self, 'user'):
                request = request_or_self
            else:
                request = args[0] if args else request_or_self

            if not request.user or not request.user.is_authenticated:
                return api_response(
                    False, "Authentication required.",
                    status_code=status.HTTP_401_UNAUTHORIZED,
                )

            if request.user.role not in allowed_roles:
                return api_response(
                    False,
                    f"Access denied. Required role(s): {', '.join(allowed_roles)}",
                    status_code=status.HTTP_403_FORBIDDEN,
                )

            return view_func(request_or_self, *args, **kwargs)
        return wrapper
    return decorator


def login_required(view_func):
    """Decorator that checks JWT authentication."""
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        auth = JWTAuthentication()
        try:
            user_auth_tuple = auth.authenticate(request)
            if user_auth_tuple is not None:
                request.user, _ = user_auth_tuple
                return view_func(request, *args, **kwargs)
        except AuthenticationFailed:
            pass
        return api_response(
            False, "Login required to access this resource.",
            status_code=status.HTTP_401_UNAUTHORIZED,
        )
    return wrapper
