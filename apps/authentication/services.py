"""
Authentication Services
Business logic for authentication operations.
Keeps models thin and logic centralized.
"""
from django.utils import timezone
from django.db import transaction

from .models import ProjectAccess, ProjectRole, User, Organization, AuditLog
from .constants import MAX_LOGIN_ATTEMPTS, ACCOUNT_LOCK_MINUTES


class PermissionService:
    """
    Handles permission assignment and management.
    Centralizes permission logic instead of embedding it in models.
    """
    
    # Role-based permission matrix
    ROLE_PERMISSIONS = {
        ProjectRole.OWNER: {
            'can_edit': True,
            'can_manage_budget': True,
            'can_manage_workers': True,
            'can_approve_documents': True,
            'can_view_financials': True,
        },
        ProjectRole.MANAGER: {
            'can_edit': True,
            'can_manage_budget': True,
            'can_manage_workers': True,
            'can_approve_documents': True,
            'can_view_financials': True,
        },
        ProjectRole.SITE_MANAGER: {
            'can_edit': True,
            'can_manage_budget': False,
            'can_manage_workers': True,
            'can_approve_documents': False,
            'can_view_financials': True,
        },
        ProjectRole.QS: {
            'can_edit': False,
            'can_manage_budget': True,
            'can_manage_workers': False,
            'can_approve_documents': True,
            'can_view_financials': True,
        },
        ProjectRole.ARCHITECT: {
            'can_edit': False,
            'can_manage_budget': False,
            'can_manage_workers': False,
            'can_approve_documents': True,
            'can_view_financials': False,
        },
        ProjectRole.FOREMAN: {
            'can_edit': False,
            'can_manage_budget': False,
            'can_manage_workers': True,
            'can_approve_documents': False,
            'can_view_financials': False,
        },
        ProjectRole.ENGINEER: {
            'can_edit': True,
            'can_manage_budget': False,
            'can_manage_workers': False,
            'can_approve_documents': True,
            'can_view_financials': False,
        },
        ProjectRole.SUPERVISOR: {
            'can_edit': False,
            'can_manage_budget': False,
            'can_manage_workers': True,
            'can_approve_documents': False,
            'can_view_financials': False,
        },
        ProjectRole.VIEWER: {
            'can_edit': False,
            'can_manage_budget': False,
            'can_manage_workers': False,
            'can_approve_documents': False,
            'can_view_financials': False,
        },
    }
    
    @classmethod
    def assign_default_permissions(cls, project_access):
        """
        Assigns default permissions based on project role.
        Can be overridden manually after assignment.
        
        Args:
            project_access: ProjectAccess instance
        
        Returns:
            Updated ProjectAccess instance
        """
        permissions = cls.ROLE_PERMISSIONS.get(project_access.project_role, {})
        
        for permission, value in permissions.items():
            setattr(project_access, permission, value)
        
        return project_access
    
    @classmethod
    def update_permissions(cls, project_access, **permissions):
        """
        Update specific permissions for a project access.
        
        Args:
            project_access: ProjectAccess instance
            **permissions: Permission flags to update
        
        Returns:
            Updated ProjectAccess instance
        """
        valid_permissions = [
            'can_edit',
            'can_manage_budget',
            'can_manage_workers',
            'can_approve_documents',
            'can_view_financials'
        ]
        
        for key, value in permissions.items():
            if key in valid_permissions:
                setattr(project_access, key, value)
        
        project_access.save()
        return project_access
    
    @classmethod
    def has_permission(cls, project_access, permission_name):
        """
        Check if a project access has a specific permission.
        
        Args:
            project_access: ProjectAccess instance
            permission_name: Name of permission to check
        
        Returns:
            Boolean indicating if permission is granted
        """
        return getattr(project_access, permission_name, False)


class ProjectAccessService:
    """
    Handles project access assignment and management.
    """
    
    @classmethod
    @transaction.atomic
    def grant_access(cls, user, project, project_role, assigned_by=None, notes=''):
        """
        Grant a user access to a project with a specific role.
        
        Args:
            user: User instance
            project: Project instance
            project_role: ProjectRole choice
            assigned_by: User who is granting access (optional)
            notes: Additional notes about the access grant
        
        Returns:
            ProjectAccess instance
        """
        # Check if access already exists
        existing_access = ProjectAccess.objects.filter(
            user=user,
            project=project
        ).first()
        
        if existing_access:
            # Reactivate if deactivated
            if not existing_access.is_active:
                existing_access.is_active = True
                existing_access.removed_at = None
            
            existing_access.project_role = project_role
            existing_access.assigned_by = assigned_by
            existing_access.notes = notes
            
            # Reassign permissions
            PermissionService.assign_default_permissions(existing_access)
            existing_access.save()
            
            return existing_access
        
        # Create new access
        project_access = ProjectAccess(
            user=user,
            project=project,
            project_role=project_role,
            assigned_by=assigned_by,
            notes=notes
        )
        
        # Assign default permissions
        PermissionService.assign_default_permissions(project_access)
        project_access.save()
        
        return project_access
    
    @classmethod
    @transaction.atomic
    def revoke_access(cls, user, project):
        """
        Revoke a user's access to a project.
        
        Args:
            user: User instance
            project: Project instance
        
        Returns:
            Boolean indicating success
        """
        try:
            access = ProjectAccess.objects.get(user=user, project=project, is_active=True)
            access.deactivate()
            return True
        except ProjectAccess.DoesNotExist:
            return False
    
    @classmethod
    def get_user_projects(cls, user, is_active=True):
        """
        Get all projects a user has access to.
        
        Args:
            user: User instance
            is_active: Filter by active status
        
        Returns:
            QuerySet of Project instances
        """
        from apps.projects.models import Project
        
        if user.is_super_admin():
            return Project.objects.all()
        
        return Project.objects.filter(
            members__user=user,
            members__is_active=is_active
        ).distinct()
    
    @classmethod
    def get_project_members(cls, project, is_active=True):
        """
        Get all members who have access to a project.
        
        Args:
            project: Project instance
            is_active: Filter by active status
        
        Returns:
            QuerySet of ProjectAccess instances
        """
        return ProjectAccess.objects.filter(
            project=project,
            is_active=is_active
        ).select_related('user', 'assigned_by')


class SecurityService:
    """
    Handles security-related operations like login attempts, account locking, etc.
    """
    
    @classmethod
    def record_failed_login(cls, user):
        """
        Record a failed login attempt and lock account if threshold exceeded.
        
        Args:
            user: User instance
        
        Returns:
            Boolean indicating if account is now locked
        """
        user.failed_login_attempts += 1
        
        # Lock account after MAX_LOGIN_ATTEMPTS failed attempts for ACCOUNT_LOCK_MINUTES
        if user.failed_login_attempts >= MAX_LOGIN_ATTEMPTS:
            user.locked_until = timezone.now() + timezone.timedelta(minutes=ACCOUNT_LOCK_MINUTES)
            user.save()
            return True
        
        user.save()
        return False
    
    @classmethod
    def reset_failed_attempts(cls, user):
        """
        Reset failed login attempts after successful login.
        
        Args:
            user: User instance
        """
        user.failed_login_attempts = 0
        user.locked_until = None
        user.save()
    
    @classmethod
    def is_account_locked(cls, user):
        """
        Check if account is currently locked.
        
        Args:
            user: User instance
        
        Returns:
            Boolean indicating lock status
        """
        if user.locked_until and user.locked_until > timezone.now():
            return True
        
        # Auto-unlock if time has passed
        if user.locked_until and user.locked_until <= timezone.now():
            user.locked_until = None
            user.failed_login_attempts = 0
            user.save()
        
        return False
    
    @classmethod
    def update_last_login_ip(cls, user, ip_address):
        """
        Update user's last login IP address.
        
        Args:
            user: User instance
            ip_address: IP address string
        """
        user.last_login_ip = ip_address
        user.save(update_fields=['last_login_ip'])


class OrganizationService:
    """
    Handles organization-related operations.
    """
    
    @classmethod
    @transaction.atomic
    def create_organization(cls, name, owner, org_type='contractor', **kwargs):
        """
        Create a new organization.
        
        Args:
            name: Organization name
            owner: User instance who owns the organization
            org_type: Type of organization
            **kwargs: Additional organization fields
        
        Returns:
            Organization instance
        """
        org = Organization.objects.create(
            name=name,
            owner=owner,
            org_type=org_type,
            **kwargs
        )
        
        # Auto-assign owner to organization
        owner.organization = org
        owner.save()
        
        return org
    
    @classmethod
    def add_member(cls, organization, user):
        """
        Add a user to an organization.
        
        Args:
            organization: Organization instance
            user: User instance
        """
        user.organization = organization
        user.save()
    
    @classmethod
    def remove_member(cls, user):
        """
        Remove a user from their organization.
        
        Args:
            user: User instance
        """
        user.organization = None
        user.save()
    
    @classmethod
    def get_organization_members(cls, organization):
        """
        Get all members of an organization.
        
        Args:
            organization: Organization instance
        
        Returns:
            QuerySet of User instances
        """
        return User.objects.filter(organization=organization, is_active=True)
