from rest_framework import serializers
from .models import User, RefreshToken, SessionAudit, Admin


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'password', 'displayName',
            'phone', 'role', 'profile_photo_url', 'bio',
        )
        read_only_fields = ('id',)

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            displayName=validated_data.get('displayName', ''),
            phone=validated_data.get('phone', ''),
            role=validated_data.get('role', User.Role.JOB_SEEKER),
            profile_photo_url=validated_data.get('profile_photo_url', ''),
            bio=validated_data.get('bio', ''),
        )
        return user


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'id', 'username', 'email', 'displayName', 'profile_photo_url', 'profile_photo',
            'bio', 'role', 'is_active', 'email_verified', 'phone',
            'phone_verified', 'two_factor_enabled', 'last_login',
            'organization_id', 'created_at', 'updated_at',
        )
        read_only_fields = (
            'id', 'is_active', 'email_verified', 'phone_verified',
            'last_login', 'created_at', 'updated_at',
        )


class UserUpdateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=False, min_length=8)

    class Meta:
        model = User
        fields = (
            'displayName', 'profile_photo_url', 'profile_photo', 'bio', 'phone', 'password',
        )

    def update(self, instance, validated_data):
        password = validated_data.pop('password', None)
        if password:
            instance.set_password(password)
        return super().update(instance, validated_data)


class RefreshTokenSerializer(serializers.ModelSerializer):
    class Meta:
        model = RefreshToken
        fields = ('id', 'token_hash', 'expires_at', 'created_at', 'ip_address', 'is_revoked')
        read_only_fields = ('id', 'created_at')


class SessionAuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = SessionAudit
        fields = ('id', 'user', 'login_at', 'logout_at', 'ip_address', 'location', 'success')
        read_only_fields = ('id', 'login_at')


class AdminSerializer(serializers.ModelSerializer):
    class Meta:
        model = Admin
        fields = ('user', 'activated_by', 'activated_at', 'permissions')
        read_only_fields = ('activated_at',)
