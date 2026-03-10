"""
Authentication Models for COMS
Handles user management, roles, and project-level access control
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from .validators import (
    validate_phone_number,
    validate_profile_picture,
    validate_organization_logo,
    validate_organization_name,
    validate_job_title,
)
from .constants import PHONE_REGEX_PATTERN


class SystemRole(models.TextChoices):
    """
    System-level roles - defines what a user can do globally in the system.
    Independent from project-specific roles.
    """
    SUPER_ADMIN = 'super_admin', _('Super Admin')
    CONTRACTOR = 'contractor', _('Contractor')
    SITE_MANAGER = 'site_manager', _('Site Manager')
    QS = 'qs', _('Quantity Surveyor')
    ARCHITECT = 'architect', _('Architect')
    CLIENT = 'client', _('Client')
    STAFF = 'staff', _('Staff Member')


class ProjectRole(models.TextChoices):
    """
    Project-level roles - defines what a user can do within a specific project.
    Users can have different roles across different projects.
    """
    OWNER = 'owner', _('Project Owner')
    MANAGER = 'manager', _('Project Manager')
    SITE_MANAGER = 'site_manager', _('Site Manager')
    QS = 'qs', _('Quantity Surveyor')
    ARCHITECT = 'architect', _('Architect')
    FOREMAN = 'foreman', _('Foreman')
    ENGINEER = 'engineer', _('Engineer')
    SUPERVISOR = 'supervisor', _('Supervisor')
    VIEWER = 'viewer', _('Viewer (Read-only)')


class Organization(models.Model):
    """
    Organization/Company model for multi-tenant support.
    Represents construction companies, consultancy firms, client organizations, etc.
    """
    
    class OrgType(models.TextChoices):
        CONTRACTOR = 'contractor', _('Contractor Company')
        CONSULTANT = 'consultant', _('Consultancy Firm')
        CLIENT = 'client', _('Client Organization')
        SUPPLIER = 'supplier', _('Supplier')
        OTHER = 'other', _('Other')
    
    name = models.CharField(
        max_length=255,
        unique=True,
        validators=[validate_organization_name],
        help_text=_("Organization name")
    )
    
    org_type = models.CharField(
        max_length=20,
        choices=OrgType.choices,
        default=OrgType.CONTRACTOR
    )
    
    registration_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Business registration number")
    )
    
    tax_id = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Tax identification number")
    )
    
    owner = models.ForeignKey(
        'User',
        on_delete=models.PROTECT,
        related_name='owned_organizations',
        help_text=_("Organization owner/primary contact"),
        null=True,
        blank=True
    )
    
    # Contact information
    address = models.TextField(blank=True)
    city = models.CharField(max_length=100, blank=True)
    country = models.CharField(max_length=100, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    
    logo = models.ImageField(
        upload_to='organizations/',
        blank=True,
        null=True,
        validators=[validate_organization_logo]
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Organization is currently active")
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'organizations'
        verbose_name = _('Organization')
        verbose_name_plural = _('Organizations')
        ordering = ['name']
        indexes = [
            models.Index(fields=['name']),
            models.Index(fields=['org_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.name


class User(AbstractUser):
    """
    Custom User model extending Django's AbstractUser.
    Supports role-based access control and multi-organization/project assignments.
    """
    
    # Organization relationship
    organization = models.ForeignKey(
        Organization,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='members',
        help_text=_("User's primary organization")
    )
    
    # Contact information
    phone_regex = RegexValidator(
        regex=PHONE_REGEX_PATTERN,
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    phone = models.CharField(
        validators=[phone_regex, validate_phone_number],
        max_length=17,
        blank=True,
        help_text=_("Contact phone number")
    )
    
    # System role
    system_role = models.CharField(
        max_length=20,
        choices=SystemRole.choices,
        default=SystemRole.CLIENT,
        help_text=_("System-level role (global permissions)")
    )
    
    # Job/position title
    job_title = models.CharField(
        max_length=100,
        blank=True,
        validators=[validate_job_title],
        help_text=_("Job title or position")
    )
    
    profile_picture = models.ImageField(
        upload_to='profiles/',
        blank=True,
        null=True,
        validators=[validate_profile_picture]
    )
    
    # Security tracking
    last_login_ip = models.GenericIPAddressField(
        blank=True,
        null=True,
        help_text=_("IP address of last login")
    )
    
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text=_("Count of consecutive failed login attempts")
    )
    
    locked_until = models.DateTimeField(
        blank=True,
        null=True,
        help_text=_("Account locked until this time (for security)")
    )
    
    # Account status
    is_verified = models.BooleanField(
        default=False,
        help_text=_("Email verification status")
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'users'
        verbose_name = _('User')
        verbose_name_plural = _('Users')
        ordering = ['-date_joined']
        indexes = [
            models.Index(fields=['email']),
            models.Index(fields=['system_role']),
            models.Index(fields=['is_active', 'system_role']),
            models.Index(fields=['organization']),
        ]
    
    def __str__(self):
        return f"{self.get_full_name() or self.username} ({self.get_system_role_display()})"
    
    def is_super_admin(self):
        """Check if user is a super admin"""
        return self.system_role == SystemRole.SUPER_ADMIN
    
    def has_project_access(self, project_id):
        """Check if user has access to a project"""
        if self.is_super_admin():
            return True
        return self.project_access.filter(
            project_id=project_id,
            is_active=True
        ).exists()
    
    def get_project_role(self, project_id):
        """Get user's role for a specific project"""
        try:
            access = self.project_access.get(project_id=project_id, is_active=True)
            return access.project_role
        except ProjectAccess.DoesNotExist:
            return None
    
    def is_account_locked(self):
        """Check if account is currently locked"""
        if self.locked_until and self.locked_until > timezone.now():
            return True
        return False


class ProjectAccess(models.Model):
    """
    Manages user access to specific projects with role-based permissions.
    Allows users to have different roles across different projects.
    
    Note: Permission logic has been moved to services.py for better maintainability.
    """
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='project_access',
        null=True,
        blank=True
    )
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='members',
        null=True,
        blank=True
    )
    
    project_role = models.CharField(
        max_length=20,
        choices=ProjectRole.choices,
        default=ProjectRole.VIEWER,
        help_text=_("Role within this specific project")
    )
    
    # Granular permissions
    can_edit = models.BooleanField(default=False, help_text=_("Can edit project details"))
    can_manage_budget = models.BooleanField(default=False, help_text=_("Can manage project budget"))
    can_manage_workers = models.BooleanField(default=False, help_text=_("Can assign and manage workers"))
    can_approve_documents = models.BooleanField(default=False, help_text=_("Can approve documents and reports"))
    can_view_financials = models.BooleanField(default=False, help_text=_("Can view financial reports"))
    
    # Access control
    is_active = models.BooleanField(default=True, help_text=_("User has active access to this project"))
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='granted_accesses'
    )
    assigned_at = models.DateTimeField(auto_now_add=True)
    removed_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'project_access'
        verbose_name = _('Project Access')
        verbose_name_plural = _('Project Accesses')
        unique_together = [['user', 'project']]
        ordering = ['-assigned_at']
        indexes = [
            models.Index(fields=['user', 'project', 'is_active']),
            models.Index(fields=['project', 'is_active']),
            models.Index(fields=['project_role']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.project.name} ({self.get_project_role_display()})"
    
    def deactivate(self):
        """Deactivate project access"""
        self.is_active = False
        self.removed_at = timezone.now()
        self.save()


class AuditLog(models.Model):
    """
    Audit logging for security and compliance tracking.
    Records user actions, authentication events, and permission changes.
    """
    
    class Action(models.TextChoices):
        USER_LOGIN = 'user_login', _('User Login')
        USER_LOGOUT = 'user_logout', _('User Logout')
        LOGIN_FAILED = 'login_failed', _('Login Failed')
        USER_CREATED = 'user_created', _('User Created')
        USER_UPDATED = 'user_updated', _('User Updated')
        USER_DELETED = 'user_deleted', _('User Deleted')
        ACCESS_GRANTED = 'access_granted', _('Project Access Granted')
        ACCESS_REVOKED = 'access_revoked', _('Project Access Revoked')
        PERMISSION_CHANGED = 'permission_changed', _('Permission Changed')
        PASSWORD_CHANGED = 'password_changed', _('Password Changed')
        PASSWORD_RESET = 'password_reset', _('Password Reset')
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='audit_logs'
    )
    
    action = models.CharField(
        max_length=50,
        choices=Action.choices
    )
    
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    
    details = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional context about the action")
    )
    
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'audit_logs'
        verbose_name = _('Audit Log')
        verbose_name_plural = _('Audit Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['-timestamp']),
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
            models.Index(fields=['ip_address']),
        ]
    
    def __str__(self):
        return f"{self.get_action_display()} - {self.user} @ {self.timestamp}"
