"""
Role-Based Access Control Services

This module provides services for managing roles, permissions, and user roles.
"""

from django.utils import timezone
from django.db import transaction
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta

from apps.roles.models import Role, Permission, UserRole
from apps.roles.selectors import RoleSelector, PermissionSelector, UserRoleSelector


class RoleService:
    """
    Service for managing roles and their permissions.
    """
    
    @staticmethod
    def create_role(
        code: str,
        name: str,
        description: str = '',
        permission_codes: Optional[List[str]] = None,
        is_system_role: bool = False
    ) -> Role:
        """
        Create a new role.
        
        Args:
            code: Unique role code
            name: Display name
            description: Role description
            permission_codes: List of permission codes to assign
            is_system_role: Whether this is a system role
            
        Returns:
            Created Role instance
        """
        role = Role.objects.create(
            code=code,
            name=name,
            description=description,
            is_system_role=is_system_role
        )
        
        if permission_codes:
            permissions = PermissionSelector.get_permissions_by_codes(permission_codes)
            role.permissions.add(*permissions)
        
        return role
    
    @staticmethod
    def update_role(
        role: Role,
        name: Optional[str] = None,
        description: Optional[str] = None,
        permission_codes: Optional[List[str]] = None
    ) -> Role:
        """
        Update a role.
        
        Args:
            role: Role instance to update
            name: New name
            description: New description
            permission_codes: New list of permission codes (replaces existing)
            
        Returns:
            Updated Role instance
        """
        if name:
            role.name = name
        
        if description is not None:
            role.description = description
        
        if permission_codes is not None:
            permissions = PermissionSelector.get_permissions_by_codes(permission_codes)
            role.permissions.set(permissions)
        
        role.save()
        return role
    
    @staticmethod
    def delete_role(role: Role) -> bool:
        """
        Delete a role (only custom roles, not system roles).
        
        Args:
            role: Role instance to delete
            
        Returns:
            Boolean indicating success
        """
        if role.is_system_role:
            raise ValueError("Cannot delete system roles")
        
        role.delete()
        return True
    
    @staticmethod
    def add_permission_to_role(role: Role, permission_code: str) -> Role:
        """
        Add a permission to a role.
        
        Args:
            role: Role instance
            permission_code: Permission code to add
            
        Returns:
            Updated Role instance
        """
        permission = PermissionSelector.get_permission_by_code(permission_code)
        if permission:
            role.permissions.add(permission)
        return role
    
    @staticmethod
    def remove_permission_from_role(role: Role, permission_code: str) -> Role:
        """
        Remove a permission from a role.
        
        Args:
            role: Role instance
            permission_code: Permission code to remove
            
        Returns:
            Updated Role instance
        """
        permission = PermissionSelector.get_permission_by_code(permission_code)
        if permission:
            role.permissions.remove(permission)
        return role


class PermissionService:
    """
    Service for managing permissions.
    """
    
    @staticmethod
    def create_permission(
        code: str,
        name: str,
        category: str,
        description: str = ''
    ) -> Permission:
        """
        Create a new permission.
        
        Args:
            code: Unique permission code
            name: Display name
            category: Permission category
            description: Permission description
            
        Returns:
            Created Permission instance
        """
        return Permission.objects.create(
            code=code,
            name=name,
            category=category,
            description=description
        )
    
    @staticmethod
    def update_permission(
        permission: Permission,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Permission:
        """
        Update a permission.
        
        Args:
            permission: Permission instance to update
            name: New name
            description: New description
            
        Returns:
            Updated Permission instance
        """
        if name:
            permission.name = name
        
        if description is not None:
            permission.description = description
        
        permission.save()
        return permission


class UserRoleService:
    """
    Service for managing user role assignments.
    """
    
    @staticmethod
    @transaction.atomic
    def assign_role(
        user,
        role_code: str,
        organization=None,
        project=None,
        assigned_by=None,
        expires_at: Optional[datetime] = None,
        notes: str = ''
    ) -> UserRole:
        """
        Assign a role to a user.
        
        Args:
            user: User instance
            role_code: Role code to assign
            organization: Organization context (optional)
            project: Project context (optional)
            assigned_by: User who is assigning the role
            expires_at: Expiration datetime (optional)
            notes: Additional notes
            
        Returns:
            Created or updated UserRole instance
        """
        role = RoleSelector.get_role_by_code(role_code)
        if not role:
            raise ValueError(f"Role with code '{role_code}' not found")
        
        # Check if assignment already exists
        existing = UserRole.objects.filter(
            user=user,
            role=role,
            organization=organization,
            project=project
        ).first()
        
        if existing:
            # Reactivate if it exists
            existing.is_active = True
            existing.assigned_by = assigned_by
            existing.assigned_at = timezone.now()
            existing.expires_at = expires_at
            existing.notes = notes
            existing.save()
            return existing
        
        # Create new assignment
        user_role = UserRole.objects.create(
            user=user,
            role=role,
            organization=organization,
            project=project,
            assigned_by=assigned_by,
            expires_at=expires_at,
            notes=notes
        )
        
        return user_role
    
    @staticmethod
    @transaction.atomic
    def remove_role(
        user,
        role_code: str,
        organization=None,
        project=None
    ) -> bool:
        """
        Remove a role from a user.
        
        Args:
            user: User instance
            role_code: Role code to remove
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating success
        """
        role = RoleSelector.get_role_by_code(role_code)
        if not role:
            return False
        
        user_roles = UserRole.objects.filter(
            user=user,
            role=role,
            organization=organization,
            project=project,
            is_active=True
        )
        
        user_roles.update(is_active=False)
        return True
    
    @staticmethod
    def check_permission(
        user,
        permission_code: str,
        organization=None,
        project=None
    ) -> bool:
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
        return UserRoleSelector.has_permission(
            user=user,
            permission_code=permission_code,
            organization=organization,
            project=project
        )
    
    @staticmethod
    def check_any_permission(
        user,
        permission_codes: List[str],
        organization=None,
        project=None
    ) -> bool:
        """
        Check if a user has any of the specified permissions.
        
        Args:
            user: User instance
            permission_codes: List of permission codes
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has any permission
        """
        return UserRoleSelector.has_any_permission(
            user=user,
            permission_codes=permission_codes,
            organization=organization,
            project=project
        )
    
    @staticmethod
    def check_all_permissions(
        user,
        permission_codes: List[str],
        organization=None,
        project=None
    ) -> bool:
        """
        Check if a user has all of the specified permissions.
        
        Args:
            user: User instance
            permission_codes: List of permission codes
            organization: Organization context
            project: Project context
            
        Returns:
            Boolean indicating if user has all permissions
        """
        return UserRoleSelector.has_all_permissions(
            user=user,
            permission_codes=permission_codes,
            organization=organization,
            project=project
        )
    
    @staticmethod
    def get_user_permissions(user, organization=None, project=None) -> List[str]:
        """
        Get all permission codes for a user.
        
        Args:
            user: User instance
            organization: Organization context
            project: Project context
            
        Returns:
            List of permission codes
        """
        permissions = UserRoleSelector.get_user_permissions(
            user=user,
            organization=organization,
            project=project
        )
        return list(permissions.values_list('code', flat=True))
    
    @staticmethod
    def get_user_roles(user, organization=None, project=None) -> List[Dict[str, Any]]:
        """
        Get all roles for a user with details.
        
        Args:
            user: User instance
            organization: Organization context
            project: Project context
            
        Returns:
            List of role dictionaries
        """
        user_roles = UserRoleSelector.get_user_roles(
            user=user,
            organization=organization,
            project=project,
            is_active=True,
            include_expired=False
        )
        
        roles = []
        for ur in user_roles:
            roles.append({
                'role_code': ur.role.code,
                'role_name': ur.role.name,
                'organization': ur.organization.name if ur.organization else None,
                'project': ur.project.name if ur.project else None,
                'assigned_at': ur.assigned_at,
                'expires_at': ur.expires_at,
            })
        
        return roles
    
    @staticmethod
    @transaction.atomic
    def bulk_assign_permissions_to_role(role_code: str, permission_codes: List[str]) -> Role:
        """
        Assign multiple permissions to a role at once.
        
        Args:
            role_code: Role code
            permission_codes: List of permission codes
            
        Returns:
            Updated Role instance
        """
        role = RoleSelector.get_role_by_code(role_code)
        if not role:
            raise ValueError(f"Role with code '{role_code}' not found")
        
        permissions = PermissionSelector.get_permissions_by_codes(permission_codes)
        role.permissions.add(*permissions)
        
        return role
    
    @staticmethod
    def cleanup_expired_roles():
        """
        Deactivate all expired role assignments.
        
        Returns:
            Number of deactivated roles
        """
        expired_roles = UserRole.objects.filter(
            is_active=True,
            expires_at__lte=timezone.now()
        )
        
        count = expired_roles.count()
        expired_roles.update(is_active=False)
        
        return count


# Permission decorators and utilities
def require_permission(permission_code: str, organization_field: str = None, project_field: str = None):
    """
    Decorator to require a specific permission for a view or API endpoint.
    
    Args:
        permission_code: Required permission code
        organization_field: Field name to get organization from (e.g., 'organization', 'project.organization')
        project_field: Field name to get project from (e.g., 'project')
        
    Example:
        @require_permission('approve_variations', organization_field='organization')
        def approve_variation(request, variation_id):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from django.core.exceptions import PermissionDenied
            
            request = args[0] if args else kwargs.get('request')
            if not request or not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            # Get context from request or kwargs
            organization = None
            project = None
            
            if organization_field:
                # Try to get from kwargs first
                organization = kwargs.get(organization_field)
                if not organization and hasattr(request, 'data'):
                    organization = request.data.get(organization_field)
            
            if project_field:
                project = kwargs.get(project_field)
                if not project and hasattr(request, 'data'):
                    project = request.data.get(project_field)
            
            # Check permission
            has_perm = UserRoleService.check_permission(
                user=request.user,
                permission_code=permission_code,
                organization=organization,
                project=project
            )
            
            if not has_perm:
                raise PermissionDenied(f"Permission '{permission_code}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator


def require_role(role_code: str, organization_field: str = None, project_field: str = None):
    """
    Decorator to require a specific role for a view or API endpoint.
    
    Args:
        role_code: Required role code
        organization_field: Field name to get organization from
        project_field: Field name to get project from
        
    Example:
        @require_role('project_manager', project_field='project')
        def manage_project(request, project_id):
            ...
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            from django.core.exceptions import PermissionDenied
            
            request = args[0] if args else kwargs.get('request')
            if not request or not request.user.is_authenticated:
                raise PermissionDenied("Authentication required")
            
            organization = None
            project = None
            
            if organization_field:
                organization = kwargs.get(organization_field)
            
            if project_field:
                project = kwargs.get(project_field)
            
            # Check role
            has_role = UserRoleSelector.has_role(
                user=request.user,
                role_code=role_code,
                organization=organization,
                project=project
            )
            
            if not has_role:
                raise PermissionDenied(f"Role '{role_code}' required")
            
            return func(*args, **kwargs)
        return wrapper
    return decorator
