"""
Role-Based Access Control Selectors

This module provides optimized query methods for roles, permissions, and user roles.
All queries are optimized with select_related and prefetch_related where appropriate.
"""

from django.db.models import Q, Prefetch, Count
from django.utils import timezone
from typing import Optional, List

from apps.roles.models import Role, Permission, UserRole


class RoleSelector:
    """
    Selector for querying Role records.
    
    Provides methods for retrieving roles with various filters and optimizations.
    """
    
    @staticmethod
    def get_all_roles(is_active: Optional[bool] = None):
        """
        Get all roles.
        
        Args:
            is_active: Filter by active status
            
        Returns:
            QuerySet of Role objects
        """
        queryset = Role.objects.prefetch_related('permissions').all()
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    @staticmethod
    def get_role_by_code(code: str):
        """
        Get a role by its code.
        
        Args:
            code: Role code (e.g., 'admin', 'project_manager')
            
        Returns:
            Role object or None
        """
        try:
            return Role.objects.prefetch_related('permissions').get(code=code, is_active=True)
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    def get_role_by_id(role_id: str):
        """
        Get a role by ID.
        
        Args:
            role_id: Role UUID
            
        Returns:
            Role object or None
        """
        try:
            return Role.objects.prefetch_related('permissions').get(id=role_id)
        except Role.DoesNotExist:
            return None
    
    @staticmethod
    def get_system_roles():
        """
        Get all system-defined roles.
        
        Returns:
            QuerySet of system Role objects
        """
        return Role.objects.filter(
            is_system_role=True,
            is_active=True
        ).prefetch_related('permissions').all()
    
    @staticmethod
    def get_roles_with_permission(permission_code: str):
        """
        Get all roles that have a specific permission.
        
        Args:
            permission_code: Permission code
            
        Returns:
            QuerySet of Role objects
        """
        return Role.objects.filter(
            permissions__code=permission_code,
            is_active=True
        ).prefetch_related('permissions').distinct()


class PermissionSelector:
    """
    Selector for querying Permission records.
    
    Provides methods for retrieving permissions with various filters.
    """
    
    @staticmethod
    def get_all_permissions(category: Optional[str] = None, is_active: Optional[bool] = None):
        """
        Get all permissions.
        
        Args:
            category: Filter by category
            is_active: Filter by active status
            
        Returns:
            QuerySet of Permission objects
        """
        queryset = Permission.objects.all()
        
        if category:
            queryset = queryset.filter(category=category)
        
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active)
        
        return queryset
    
    @staticmethod
    def get_permission_by_code(code: str):
        """
        Get a permission by its code.
        
        Args:
            code: Permission code
            
        Returns:
            Permission object or None
        """
        try:
            return Permission.objects.get(code=code, is_active=True)
        except Permission.DoesNotExist:
            return None
    
    @staticmethod
    def get_permissions_by_category(category: str):
        """
        Get all permissions in a category.
        
        Args:
            category: Permission category
            
        Returns:
            QuerySet of Permission objects
        """
        return Permission.objects.filter(
            category=category,
            is_active=True
        ).all()
    
    @staticmethod
    def get_permissions_by_codes(codes: List[str]):
        """
        Get permissions by a list of codes.
        
        Args:
            codes: List of permission codes
            
        Returns:
            QuerySet of Permission objects
        """
        return Permission.objects.filter(
            code__in=codes,
            is_active=True
        ).all()


class UserRoleSelector:
    """
    Selector for querying UserRole records.
    
    Provides methods for retrieving user roles and checking permissions.
    """
    
    @staticmethod
    def get_user_roles(
        user,
        organization=None,
        project=None,
        is_active: bool = True,
        include_expired: bool = False
    ):
        """
        Get all roles for a user.
        
        Args:
            user: User instance
            organization: Filter by organization
            project: Filter by project
            is_active: Filter by active status
            include_expired: Whether to include expired roles
            
        Returns:
            QuerySet of UserRole objects
        """
        queryset = UserRole.objects.filter(user=user).select_related(
            'role', 'organization', 'project', 'assigned_by'
        ).prefetch_related('role__permissions')
        
        if is_active:
            queryset = queryset.filter(is_active=True)
        
        if not include_expired:
            # Exclude expired roles
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        if organization:
            queryset = queryset.filter(
                Q(organization=organization) | Q(organization__isnull=True)
            )
        
        if project:
            queryset = queryset.filter(
                Q(project=project) | Q(project__isnull=True)
            )
        
        return queryset
    
    @staticmethod
    def get_user_permissions(user, organization=None, project=None):
        """
        Get all permissions for a user based on their roles.
        
        Args:
            user: User instance
            organization: Filter by organization context
            project: Filter by project context
            
        Returns:
            QuerySet of Permission objects (deduplicated)
        """
        # Get user's active, non-expired roles
        user_roles = UserRoleSelector.get_user_roles(
            user=user,
            organization=organization,
            project=project,
            is_active=True,
            include_expired=False
        )
        
        # Get all permissions from those roles
        permission_ids = set()
        for user_role in user_roles:
            permission_ids.update(
                user_role.role.permissions.filter(is_active=True).values_list('id', flat=True)
            )
        
        return Permission.objects.filter(id__in=permission_ids)
    
    @staticmethod
    def has_permission(user, permission_code: str, organization=None, project=None):
        """
        Check if a user has a specific permission.
        
        Args:
            user: User instance
            permission_code: Permission code to check
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has the permission
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        permissions = UserRoleSelector.get_user_permissions(
            user=user,
            organization=organization,
            project=project
        )
        
        return permissions.filter(code=permission_code).exists()
    
    @staticmethod
    def has_any_permission(user, permission_codes: List[str], organization=None, project=None):
        """
        Check if a user has any of the specified permissions.
        
        Args:
            user: User instance
            permission_codes: List of permission codes
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has any of the permissions
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        permissions = UserRoleSelector.get_user_permissions(
            user=user,
            organization=organization,
            project=project
        )
        
        return permissions.filter(code__in=permission_codes).exists()
    
    @staticmethod
    def has_all_permissions(user, permission_codes: List[str], organization=None, project=None):
        """
        Check if a user has all of the specified permissions.
        
        Args:
            user: User instance
            permission_codes: List of permission codes
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has all of the permissions
        """
        # Superusers have all permissions
        if user.is_superuser:
            return True
        
        permissions = UserRoleSelector.get_user_permissions(
            user=user,
            organization=organization,
            project=project
        )
        
        user_permission_codes = set(permissions.values_list('code', flat=True))
        required_codes = set(permission_codes)
        
        return required_codes.issubset(user_permission_codes)
    
    @staticmethod
    def has_role(user, role_code: str, organization=None, project=None):
        """
        Check if a user has a specific role.
        
        Args:
            user: User instance
            role_code: Role code to check
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has the role
        """
        user_roles = UserRoleSelector.get_user_roles(
            user=user,
            organization=organization,
            project=project,
            is_active=True,
            include_expired=False
        )
        
        return user_roles.filter(role__code=role_code).exists()
    
    @staticmethod
    def get_users_with_role(role_code: str, organization=None, project=None):
        """
        Get all users with a specific role.
        
        Args:
            role_code: Role code
            organization: Filter by organization
            project: Filter by project
            
        Returns:
            QuerySet of User objects
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        queryset = UserRole.objects.filter(
            role__code=role_code,
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        if organization:
            queryset = queryset.filter(
                Q(organization=organization) | Q(organization__isnull=True)
            )
        
        if project:
            queryset = queryset.filter(
                Q(project=project) | Q(project__isnull=True)
            )
        
        user_ids = queryset.values_list('user_id', flat=True).distinct()
        return User.objects.filter(id__in=user_ids)
    
    @staticmethod
    def get_users_with_permission(permission_code: str, organization=None, project=None):
        """
        Get all users with a specific permission.
        
        Args:
            permission_code: Permission code
            organization: Filter by organization
            project: Filter by project
            
        Returns:
            QuerySet of User objects
        """
        from django.contrib.auth import get_user_model
        User = get_user_model()
        
        queryset = UserRole.objects.filter(
            role__permissions__code=permission_code,
            is_active=True
        ).filter(
            Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
        )
        
        if organization:
            queryset = queryset.filter(
                Q(organization=organization) | Q(organization__isnull=True)
            )
        
        if project:
            queryset = queryset.filter(
                Q(project=project) | Q(project__isnull=True)
            )
        
        user_ids = queryset.values_list('user_id', flat=True).distinct()
        return User.objects.filter(id__in=user_ids)
