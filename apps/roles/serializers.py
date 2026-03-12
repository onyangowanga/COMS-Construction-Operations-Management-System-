"""
API Serializers for Role-Based Access Control

This module provides serializers for Role, Permission, and UserRole models.
"""

from rest_framework import serializers
from apps.roles.models import Role, Permission, UserRole


class PermissionSerializer(serializers.ModelSerializer):
    """
    Serializer for Permission model.
    """
    
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    role_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Permission
        fields = [
            'id',
            'code',
            'name',
            'description',
            'category',
            'category_display',
            'is_active',
            'role_count',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class PermissionSummarySerializer(serializers.ModelSerializer):
    """
    Simplified Permission serializer for nested representations.
    """
    
    class Meta:
        model = Permission
        fields = ['id', 'code', 'name', 'category']


class RoleSerializer(serializers.ModelSerializer):
    """
    Serializer for Role model.
    """
    
    permissions = PermissionSummarySerializer(many=True, read_only=True)
    permission_ids = serializers.ListField(
        child=serializers.UUIDField(),
        write_only=True,
        required=False,
        help_text="List of permission IDs to assign to this role"
    )
    permission_count = serializers.IntegerField(read_only=True)
    user_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Role
        fields = [
            'id',
            'code',
            'name',
            'description',
            'is_system_role',
            'is_active',
            'permissions',
            'permission_ids',
            'permission_count',
            'user_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def create(self, validated_data):
        """Create role and assign permissions."""
        permission_ids = validated_data.pop('permission_ids', [])
        role = Role.objects.create(**validated_data)
        
        if permission_ids:
            permissions = Permission.objects.filter(id__in=permission_ids)
            role.permissions.set(permissions)
        
        return role
    
    def update(self, instance, validated_data):
        """Update role and permissions."""
        permission_ids = validated_data.pop('permission_ids', None)
        
        # Update basic fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        # Update permissions if provided
        if permission_ids is not None:
            permissions = Permission.objects.filter(id__in=permission_ids)
            instance.permissions.set(permissions)
        
        return instance


class RoleSummarySerializer(serializers.ModelSerializer):
    """
    Simplified Role serializer for nested representations.
    """
    
    class Meta:
        model = Role
        fields = ['id', 'code', 'name']


class UserRoleSerializer(serializers.ModelSerializer):
    """
    Serializer for UserRole model.
    """
    
    role_details = RoleSummarySerializer(source='role', read_only=True)
    user_details = serializers.SerializerMethodField()
    organization_name = serializers.CharField(source='organization.name', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    assigned_by_name = serializers.SerializerMethodField()
    is_expired = serializers.BooleanField(read_only=True)
    is_valid = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = UserRole
        fields = [
            'id',
            'user',
            'user_details',
            'role',
            'role_details',
            'organization',
            'organization_name',
            'project',
            'project_name',
            'is_active',
            'assigned_by',
            'assigned_by_name',
            'assigned_at',
            'expires_at',
            'is_expired',
            'is_valid',
            'notes'
        ]
        read_only_fields = ['id', 'assigned_at']
    
    def get_user_details(self, obj):
        """Get user information."""
        return {
            'id': obj.user.id,
            'username': obj.user.username,
            'email': obj.user.email,
            'full_name': obj.user.get_full_name()
        }
    
    def get_assigned_by_name(self, obj):
        """Get assigned_by user name."""
        if obj.assigned_by:
            return obj.assigned_by.get_full_name() or obj.assigned_by.username
        return None


class AssignRoleSerializer(serializers.Serializer):
    """
    Serializer for assigning a role to a user.
    """
    
    user_id = serializers.IntegerField(help_text="ID of the user to assign the role to")
    role_code = serializers.CharField(help_text="Code of the role to assign")
    organization_id = serializers.UUIDField(required=False, allow_null=True, help_text="Organization context")
    project_id = serializers.UUIDField(required=False, allow_null=True, help_text="Project context")
    expires_at = serializers.DateTimeField(required=False, allow_null=True, help_text="Expiration date")
    notes = serializers.CharField(required=False, allow_blank=True, help_text="Additional notes")


class RemoveRoleSerializer(serializers.Serializer):
    """
    Serializer for removing a role from a user.
    """
    
    user_id = serializers.IntegerField(help_text="ID of the user to remove the role from")
    role_code = serializers.CharField(help_text="Code of the role to remove")
    organization_id = serializers.UUIDField(required=False, allow_null=True, help_text="Organization context")
    project_id = serializers.UUIDField(required=False, allow_null=True, help_text="Project context")


class CheckPermissionSerializer(serializers.Serializer):
    """
    Serializer for checking user permissions.
    """
    
    user_id = serializers.IntegerField(help_text="ID of the user to check")
    permission_code = serializers.CharField(help_text="Permission code to check")
    organization_id = serializers.UUIDField(required=False, allow_null=True, help_text="Organization context")
    project_id = serializers.UUIDField(required=False, allow_null=True, help_text="Project context")


class UserPermissionsSerializer(serializers.Serializer):
    """
    Serializer for retrieving user permissions.
    """
    
    user_id = serializers.IntegerField(help_text="ID of the user")
    organization_id = serializers.UUIDField(required=False, allow_null=True, help_text="Organization context")
    project_id = serializers.UUIDField(required=False, allow_null=True, help_text="Project context")
