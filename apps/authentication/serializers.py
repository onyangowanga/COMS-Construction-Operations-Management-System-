"""
Authentication Serializers
Input validation for authentication endpoints.
Follows service layer pattern - keeps validation logic here, business logic in services.
"""
from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError as DjangoValidationError

from .models import User, SystemRole, Organization
from .validators import (
    validate_email,
    validate_password_strength,
    validate_phone_number,
    validate_username,
)
from .auth_selectors import UserSelectors


class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login.
    Validates email and password.
    """
    email = serializers.EmailField(required=True)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_email(self, value):
        """Validate email format"""
        try:
            validate_email(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value.lower()
    
    def validate(self, attrs):
        """
        Validate credentials.
        Note: Actual authentication happens in the view using SecurityService.
        This just validates format.
        """
        return attrs


class RegisterSerializer(serializers.Serializer):
    """
    Serializer for user registration.
    Validates all required fields for creating a new user.
    """
    email = serializers.EmailField(required=True)
    username = serializers.CharField(required=True, max_length=150)
    password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    first_name = serializers.CharField(required=True, max_length=150)
    last_name = serializers.CharField(required=True, max_length=150)
    phone = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True, max_length=100)
    system_role = serializers.ChoiceField(
        choices=SystemRole.choices,
        default=SystemRole.CLIENT
    )
    organization_id = serializers.IntegerField(required=False, allow_null=True)
    
    def validate_email(self, value):
        """Validate email and check uniqueness"""
        try:
            validate_email(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        value = value.lower()
        
        # Check if email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("A user with this email already exists.")
        
        return value
    
    def validate_username(self, value):
        """Validate username and check uniqueness"""
        try:
            validate_username(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        # Check if username already exists
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("A user with this username already exists.")
        
        return value
    
    def validate_password(self, value):
        """Validate password strength"""
        try:
            validate_password_strength(value)
            # Also use Django's built-in validators
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate_phone(self, value):
        """Validate phone number"""
        if value:
            try:
                validate_phone_number(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        return attrs


class TokenRefreshSerializer(serializers.Serializer):
    """
    Serializer for token refresh.
    Note: Token is extracted from cookie, not request body.
    """
    pass  # Token comes from HTTP-only cookie


class ChangePasswordSerializer(serializers.Serializer):
    """
    Serializer for password change (authenticated users).
    """
    old_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate new password strength"""
        try:
            validate_password_strength(value)
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate(self, attrs):
        """Validate new password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords do not match."
            })
        
        return attrs


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile data.
    Returns user information after login.
    """
    system_role_display = serializers.CharField(source='get_system_role_display', read_only=True)
    organization_name = serializers.CharField(source='organization.name', read_only=True, allow_null=True)
    role = serializers.CharField(source='system_role', read_only=True)
    organization_label = serializers.CharField(source='organization.name', read_only=True, allow_null=True)
    is_locked = serializers.SerializerMethodField()
    permissions = serializers.SerializerMethodField()
    roles = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'first_name',
            'last_name',
            'phone',
            'job_title',
            'system_role',
            'system_role_display',
            'role',
            'organization',
            'organization_name',
            'organization_label',
            'profile_picture',
            'ui_theme',
            'ui_timezone',
            'ui_language',
            'ui_compact_mode',
            'is_verified',
            'is_active',
            'is_staff',
            'is_locked',
            'created_at',
            'last_login',
            'permissions',
            'roles',
        ]
        read_only_fields = fields

    def get_is_locked(self, obj):
        """Check if account is currently locked"""
        return obj.is_account_locked()

    def get_permissions(self, obj):
        """Return a flat list of all permission codes for this user."""
        if obj.is_superuser:
            # Superusers get all active permission codes
            try:
                from apps.roles.models import Permission
                return list(Permission.objects.filter(is_active=True).values_list('code', flat=True))
            except Exception:
                return []
        try:
            from apps.roles.roles_selectors import UserRoleSelector
            permissions = UserRoleSelector.get_user_permissions(obj)
            return list(permissions.values_list('code', flat=True))
        except Exception:
            return []

    def get_roles(self, obj):
        """Return a list of role summaries assigned to the user."""
        try:
            from apps.roles.roles_selectors import UserRoleSelector
            user_roles = UserRoleSelector.get_user_roles(user=obj, is_active=True)
            result = []
            for ur in user_roles:
                result.append({
                    'id': str(ur.id),
                    'role_code': ur.role.code,
                    'role_name': ur.role.name,
                    'organization': str(ur.organization_id) if ur.organization_id else None,
                    'organization_name': ur.organization.name if ur.organization else None,
                    'project': str(ur.project_id) if ur.project_id else None,
                    'project_name': ur.project.name if ur.project else None,
                    'assigned_at': ur.assigned_at.isoformat() if ur.assigned_at else None,
                    'expires_at': ur.expires_at.isoformat() if ur.expires_at else None,
                    'is_active': ur.is_active,
                })
            return result
        except Exception:
            return []


class UserUpdateSerializer(serializers.ModelSerializer):
    """
    Serializer for updating user profile.
    """
    phone = serializers.CharField(required=False, allow_blank=True)
    job_title = serializers.CharField(required=False, allow_blank=True)
    ui_theme = serializers.ChoiceField(choices=['light', 'dark', 'auto'], required=False)
    ui_timezone = serializers.CharField(required=False, allow_blank=False)
    ui_language = serializers.CharField(required=False, allow_blank=False)
    ui_compact_mode = serializers.BooleanField(required=False)
    
    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'phone',
            'job_title',
            'profile_picture',
            'ui_theme',
            'ui_timezone',
            'ui_language',
            'ui_compact_mode',
        ]
    
    def validate_phone(self, value):
        """Validate phone number"""
        if value:
            try:
                validate_phone_number(value)
            except DjangoValidationError as e:
                raise serializers.ValidationError(e.messages)
        return value


class PasswordResetRequestSerializer(serializers.Serializer):
    """
    Serializer for password reset request.
    """
    email = serializers.EmailField(required=True)
    
    def validate_email(self, value):
        """Validate email format"""
        try:
            validate_email(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        return value.lower()


class PasswordResetConfirmSerializer(serializers.Serializer):
    """
    Serializer for password reset confirmation.
    """
    token = serializers.CharField(required=True)
    new_password = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    new_password_confirm = serializers.CharField(
        required=True,
        write_only=True,
        style={'input_type': 'password'}
    )
    
    def validate_new_password(self, value):
        """Validate password strength"""
        try:
            validate_password_strength(value)
            validate_password(value)
        except DjangoValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return value
    
    def validate(self, attrs):
        """Validate password confirmation"""
        if attrs['new_password'] != attrs['new_password_confirm']:
            raise serializers.ValidationError({
                'new_password_confirm': "Passwords do not match."
            })
        
        return attrs
