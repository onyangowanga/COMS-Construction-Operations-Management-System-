"""
Authentication Selectors
Read-only database queries for authentication data.
Selectors are optimized for fetching data efficiently.
"""
from django.db.models import Q, Prefetch, Count
from django.utils import timezone

from .models import User, ProjectAccess, AuditLog, Organization, SystemRole, ProjectRole


class UserSelectors:
    """
    Selectors for User model queries.
    """
    
    @staticmethod
    def get_by_id(user_id):
        """Get user by ID with organization."""
        return User.objects.select_related('organization').filter(id=user_id).first()
    
    @staticmethod
    def get_by_email(email):
        """Get user by email."""
        return User.objects.select_related('organization').filter(email=email).first()
    
    @staticmethod
    def get_by_username(username):
        """Get user by username."""
        return User.objects.select_related('organization').filter(username=username).first()
    
    @staticmethod
    def get_active_users():
        """Get all active users."""
        return User.objects.filter(is_active=True).select_related('organization')
    
    @staticmethod
    def get_by_system_role(system_role):
        """Get users by system role."""
        return User.objects.filter(
            system_role=system_role,
            is_active=True
        ).select_related('organization')
    
    @staticmethod
    def get_contractors():
        """Get all contractor users."""
        return User.objects.filter(
            system_role=SystemRole.CONTRACTOR,
            is_active=True
        ).select_related('organization')
    
    @staticmethod
    def get_clients():
        """Get all client users."""
        return User.objects.filter(
            system_role=SystemRole.CLIENT,
            is_active=True
        ).select_related('organization')
    
    @staticmethod
    def get_verified_users():
        """Get all verified users."""
        return User.objects.filter(
            is_verified=True,
            is_active=True
        ).select_related('organization')
    
    @staticmethod
    def search_users(query):
        """
        Search users by username, email, first name, or last name.
        
        Args:
            query: Search string
        
        Returns:
            QuerySet of matching users
        """
        return User.objects.filter(
            Q(username__icontains=query) |
            Q(email__icontains=query) |
            Q(first_name__icontains=query) |
            Q(last_name__icontains=query)
        ).select_related('organization')


class ProjectAccessSelectors:
    """
    Selectors for ProjectAccess model queries.
    """
    
    @staticmethod
    def get_user_project_access(user, project):
        """Get specific project access for a user."""
        return ProjectAccess.objects.filter(
            user=user,
            project=project,
            is_active=True
        ).select_related('user', 'project', 'assigned_by').first()
    
    @staticmethod
    def get_user_projects(user, is_active=True):
        """Get all project accesses for a user."""
        return ProjectAccess.objects.filter(
            user=user,
            is_active=is_active
        ).select_related('project', 'assigned_by').order_by('-assigned_at')
    
    @staticmethod
    def get_project_members(project, is_active=True):
        """Get all members of a project."""
        return ProjectAccess.objects.filter(
            project=project,
            is_active=is_active
        ).select_related('user', 'user__organization', 'assigned_by').order_by('project_role')
    
    @staticmethod
    def get_by_project_role(project, project_role):
        """Get users with specific role on a project."""
        return ProjectAccess.objects.filter(
            project=project,
            project_role=project_role,
            is_active=True
        ).select_related('user', 'user__organization')
    
    @staticmethod
    def get_project_managers(project):
        """Get project managers for a project."""
        return ProjectAccess.objects.filter(
            project=project,
            project_role__in=[ProjectRole.OWNER, ProjectRole.MANAGER],
            is_active=True
        ).select_related('user', 'user__organization')
    
    @staticmethod
    def get_users_with_permission(project, permission_name):
        """
        Get users who have a specific permission on a project.
        
        Args:
            project: Project instance
            permission_name: Name of permission (e.g., 'can_edit')
        
        Returns:
            QuerySet of ProjectAccess instances
        """
        filter_kwargs = {
            'project': project,
            'is_active': True,
            permission_name: True
        }
        return ProjectAccess.objects.filter(
            **filter_kwargs
        ).select_related('user', 'user__organization')
    
    @staticmethod
    def count_project_members(project):
        """Count active members of a project."""
        return ProjectAccess.objects.filter(
            project=project,
            is_active=True
        ).count()
    
    @staticmethod
    def get_users_projects_count(user):
        """Get count of active projects for a user."""
        return ProjectAccess.objects.filter(
            user=user,
            is_active=True
        ).count()


class AuditLogSelectors:
    """
    Selectors for AuditLog model queries.
    """
    
    @staticmethod
    def get_user_logs(user, limit=100):
        """Get recent audit logs for a user."""
        return AuditLog.objects.filter(
            user=user
        ).select_related('user').order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_user_login_history(user, limit=50):
        """Get login history for a user."""
        return AuditLog.objects.filter(
            user=user,
            action__in=['user_login', 'user_logout', 'login_failed']
        ).order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_recent_logs(limit=100):
        """Get recent audit logs across all users."""
        return AuditLog.objects.all().select_related('user').order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_logs_by_action(action, limit=100):
        """Get logs for a specific action type."""
        return AuditLog.objects.filter(
            action=action
        ).select_related('user').order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_failed_login_attempts(hours=24):
        """Get failed login attempts within specified hours."""
        since = timezone.now() - timezone.timedelta(hours=hours)
        return AuditLog.objects.filter(
            action='login_failed',
            timestamp__gte=since
        ).select_related('user').order_by('-timestamp')
    
    @staticmethod
    def get_logs_by_ip(ip_address, limit=100):
        """Get audit logs from a specific IP address."""
        return AuditLog.objects.filter(
            ip_address=ip_address
        ).select_related('user').order_by('-timestamp')[:limit]
    
    @staticmethod
    def get_logs_in_date_range(start_date, end_date):
        """Get audit logs within a date range."""
        return AuditLog.objects.filter(
            timestamp__gte=start_date,
            timestamp__lte=end_date
        ).select_related('user').order_by('-timestamp')
    
    @staticmethod
    def get_security_events(limit=100):
        """Get security-related events (logins, failures, access changes)."""
        return AuditLog.objects.filter(
            action__in=[
                'user_login',
                'user_logout',
                'login_failed',
                'access_granted',
                'access_revoked',
                'permission_changed'
            ]
        ).select_related('user').order_by('-timestamp')[:limit]


class OrganizationSelectors:
    """
    Selectors for Organization model queries.
    """
    
    @staticmethod
    def get_by_id(org_id):
        """Get organization by ID with owner."""
        return Organization.objects.select_related('owner').filter(id=org_id).first()
    
    @staticmethod
    def get_active_organizations():
        """Get all active organizations."""
        return Organization.objects.filter(
            is_active=True
        ).select_related('owner').annotate(
            member_count=Count('members')
        )
    
    @staticmethod
    def get_by_type(org_type):
        """Get organizations by type."""
        return Organization.objects.filter(
            org_type=org_type,
            is_active=True
        ).select_related('owner').annotate(
            member_count=Count('members')
        )
    
    @staticmethod
    def get_contractors():
        """Get contractor organizations."""
        return Organization.objects.filter(
            org_type='contractor',
            is_active=True
        ).select_related('owner').annotate(
            member_count=Count('members')
        )
    
    @staticmethod
    def get_clients():
        """Get client organizations."""
        return Organization.objects.filter(
            org_type='client',
            is_active=True
        ).select_related('owner').annotate(
            member_count=Count('members')
        )
    
    @staticmethod
    def get_organization_members(org_id):
        """Get all members of an organization."""
        return User.objects.filter(
            organization_id=org_id,
            is_active=True
        ).select_related('organization')
    
    @staticmethod
    def search_organizations(query):
        """
        Search organizations by name.
        
        Args:
            query: Search string
        
        Returns:
            QuerySet of matching organizations
        """
        return Organization.objects.filter(
            Q(name__icontains=query),
            is_active=True
        ).select_related('owner').annotate(
            member_count=Count('members')
        )
