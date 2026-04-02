"""
Authentication Permissions
Django REST Framework permission classes for COMS.
"""
from rest_framework import permissions

from .auth_selectors import ProjectAccessSelectors
from .models import SystemRole


class IsSuperAdmin(permissions.BasePermission):
    """
    Permission check for Super Admin users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_super_admin()
        )


class IsContractor(permissions.BasePermission):
    """
    Permission check for Contractor users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.system_role == SystemRole.CONTRACTOR
        )


class IsVerified(permissions.BasePermission):
    """
    Permission check for verified users.
    """
    
    def has_permission(self, request, view):
        return (
            request.user and
            request.user.is_authenticated and
            request.user.is_verified
        )


class IsAccountActive(permissions.BasePermission):
    """
    Permission check for active, non-locked accounts.
    """
    
    message = "Your account is currently locked. Please try again later or contact support."
    
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        
        if not request.user.is_active:
            self.message = "Your account has been deactivated. Please contact support."
            return False
        
        if request.user.is_account_locked():
            return False
        
        return True


class IsProjectMember(permissions.BasePermission):
    """
    Permission check for project members.
    User must have active access to the project.
    """
    
    message = "You are not a member of this project."
    
    def has_object_permission(self, request, view, obj):
        # Super admins have access to everything
        if request.user.is_super_admin():
            return True
        
        # Get the project from the object
        project = getattr(obj, 'project', obj)
        
        # Check if user has active access to this project
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access is not None


class CanEditProject(permissions.BasePermission):
    """
    Permission check for project editing.
    User must have can_edit permission on the project.
    """
    
    message = "You do not have permission to edit this project."
    
    def has_object_permission(self, request, view, obj):
        # Super admins can edit everything
        if request.user.is_super_admin():
            return True
        
        # Read-only methods are allowed for all project members
        if request.method in permissions.SAFE_METHODS:
            return IsProjectMember().has_object_permission(request, view, obj)
        
        # Get the project from the object
        project = getattr(obj, 'project', obj)
        
        # Check if user has edit permission
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access and access.can_edit


class CanManageBudget(permissions.BasePermission):
    """
    Permission check for budget management.
    User must have can_manage_budget permission on the project.
    """
    
    message = "You do not have permission to manage the budget for this project."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        # Read-only allowed for project members
        if request.method in permissions.SAFE_METHODS:
            return IsProjectMember().has_object_permission(request, view, obj)
        
        project = getattr(obj, 'project', obj)
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access and access.can_manage_budget


class CanManageWorkers(permissions.BasePermission):
    """
    Permission check for worker management.
    User must have can_manage_workers permission on the project.
    """
    
    message = "You do not have permission to manage workers for this project."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        if request.method in permissions.SAFE_METHODS:
            return IsProjectMember().has_object_permission(request, view, obj)
        
        project = getattr(obj, 'project', obj)
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access and access.can_manage_workers


class CanApproveDocuments(permissions.BasePermission):
    """
    Permission check for document approval.
    User must have can_approve_documents permission on the project.
    """
    
    message = "You do not have permission to approve documents for this project."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        project = getattr(obj, 'project', obj)
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access and access.can_approve_documents


class CanViewFinancials(permissions.BasePermission):
    """
    Permission check for viewing financial data.
    User must have can_view_financials permission on the project.
    """
    
    message = "You do not have permission to view financial data for this project."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        project = getattr(obj, 'project', obj)
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return access and access.can_view_financials


class IsOrganizationMember(permissions.BasePermission):
    """
    Permission check for organization members.
    User must belong to the organization.
    """
    
    message = "You are not a member of this organization."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        # Get the organization from the object
        organization = getattr(obj, 'organization', obj)
        
        return (
            request.user.organization and
            request.user.organization == organization
        )


class IsOrganizationOwner(permissions.BasePermission):
    """
    Permission check for organization owners.
    User must be the owner of the organization.
    """
    
    message = "You are not the owner of this organization."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        organization = getattr(obj, 'organization', obj)
        
        return organization.owner == request.user


class ReadOnly(permissions.BasePermission):
    """
    Permission that only allows read-only methods (GET, HEAD, OPTIONS).
    """
    
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS


# Composite permissions for common use cases

class ProjectManagerPermission(permissions.BasePermission):
    """
    Permission for project managers (Owner or Manager role).
    """
    
    message = "You must be a project manager to perform this action."
    
    def has_object_permission(self, request, view, obj):
        if request.user.is_super_admin():
            return True
        
        from .models import ProjectRole
        
        project = getattr(obj, 'project', obj)
        access = ProjectAccessSelectors.get_user_project_access(
            user=request.user,
            project=project
        )
        
        return (
            access and
            access.project_role in [ProjectRole.OWNER, ProjectRole.MANAGER]
        )


class ProjectMemberOrReadOnly(permissions.BasePermission):
    """
    Permission that allows project members to edit,
    but read-only access for non-members.
    """
    
    def has_object_permission(self, request, view, obj):
        # Read permissions for anyone
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions only for project members
        return IsProjectMember().has_object_permission(request, view, obj)
