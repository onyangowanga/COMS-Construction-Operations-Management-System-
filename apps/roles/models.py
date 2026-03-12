"""
Role-Based Access Control Models

This module defines the core RBAC models for managing roles, permissions,
and user-role associations throughout the COMS platform.
"""

from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid


class Role(models.Model):
    """
    Role model defining different user roles in the system.
    
    Predefined roles:
    - ADMIN: Full system access
    - FINANCE_MANAGER: Financial operations and reporting
    - PROJECT_MANAGER: Project management and oversight
    - SITE_ENGINEER: Site operations and daily reporting
    - CONSULTANT: Consultant-specific access
    - CLIENT: Client portal access
    - SUPPLIER: Supplier portal access
    - SUBCONTRACTOR: Subcontractor portal access
    """
    
    # Role Types (Predefined System Roles)
    ADMIN = 'admin'
    FINANCE_MANAGER = 'finance_manager'
    PROJECT_MANAGER = 'project_manager'
    SITE_ENGINEER = 'site_engineer'
    CONSULTANT = 'consultant'
    CLIENT = 'client'
    SUPPLIER = 'supplier'
    SUBCONTRACTOR = 'subcontractor'
    
    ROLE_CHOICES = [
        (ADMIN, 'Administrator'),
        (FINANCE_MANAGER, 'Finance Manager'),
        (PROJECT_MANAGER, 'Project Manager'),
        (SITE_ENGINEER, 'Site Engineer'),
        (CONSULTANT, 'Consultant'),
        (CLIENT, 'Client'),
        (SUPPLIER, 'Supplier'),
        (SUBCONTRACTOR, 'Subcontractor'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the role"
    )
    
    code = models.CharField(
        max_length=50,
        unique=True,
        choices=ROLE_CHOICES,
        help_text="Unique code for the role"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Display name for the role"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of role responsibilities"
    )
    
    is_system_role = models.BooleanField(
        default=True,
        help_text="Whether this is a system-defined role (cannot be deleted)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this role is currently active"
    )
    
    permissions = models.ManyToManyField(
        'Permission',
        related_name='roles',
        blank=True,
        help_text="Permissions assigned to this role"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the role was created"
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="When the role was last updated"
    )
    
    class Meta:
        db_table = 'roles'
        ordering = ['name']
        verbose_name = 'Role'
        verbose_name_plural = 'Roles'
    
    def __str__(self):
        return self.name
    
    @property
    def permission_count(self):
        """Get count of permissions assigned to this role"""
        return self.permissions.count()
    
    @property
    def user_count(self):
        """Get count of users with this role"""
        return self.user_roles.filter(is_active=True).count()


class Permission(models.Model):
    """
    Permission model defining granular access controls.
    
    Permissions are organized by module and action type.
    Examples: view_reports, approve_variations, certify_claims, etc.
    """
    
    # Permission Categories
    CATEGORY_PROJECT = 'project'
    CATEGORY_FINANCIAL = 'financial'
    CATEGORY_DOCUMENT = 'document'
    CATEGORY_VARIATION = 'variation'
    CATEGORY_CLAIM = 'claim'
    CATEGORY_PAYMENT = 'payment'
    CATEGORY_APPROVAL = 'approval'
    CATEGORY_REPORT = 'report'
    CATEGORY_PROCUREMENT = 'procurement'
    CATEGORY_SUBCONTRACT = 'subcontract'
    CATEGORY_SITE_OPS = 'site_operations'
    CATEGORY_SYSTEM = 'system'
    
    CATEGORY_CHOICES = [
        (CATEGORY_PROJECT, 'Project Management'),
        (CATEGORY_FINANCIAL, 'Financial'),
        (CATEGORY_DOCUMENT, 'Document Management'),
        (CATEGORY_VARIATION, 'Variation Orders'),
        (CATEGORY_CLAIM, 'Claims & Valuations'),
        (CATEGORY_PAYMENT, 'Payments'),
        (CATEGORY_APPROVAL, 'Approvals'),
        (CATEGORY_REPORT, 'Reporting'),
        (CATEGORY_PROCUREMENT, 'Procurement'),
        (CATEGORY_SUBCONTRACT, 'Subcontracts'),
        (CATEGORY_SITE_OPS, 'Site Operations'),
        (CATEGORY_SYSTEM, 'System Administration'),
    ]
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the permission"
    )
    
    code = models.CharField(
        max_length=100,
        unique=True,
        db_index=True,
        help_text="Unique code for the permission (e.g., 'approve_variations')"
    )
    
    name = models.CharField(
        max_length=150,
        help_text="Display name for the permission"
    )
    
    description = models.TextField(
        blank=True,
        help_text="Detailed description of what this permission allows"
    )
    
    category = models.CharField(
        max_length=50,
        choices=CATEGORY_CHOICES,
        db_index=True,
        help_text="Category this permission belongs to"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this permission is currently active"
    )
    
    created_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the permission was created"
    )
    
    class Meta:
        db_table = 'permissions'
        ordering = ['category', 'name']
        verbose_name = 'Permission'
        verbose_name_plural = 'Permissions'
        indexes = [
            models.Index(fields=['code'], name='perm_code_idx'),
            models.Index(fields=['category'], name='perm_category_idx'),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    @property
    def role_count(self):
        """Get count of roles with this permission"""
        return self.roles.count()


class UserRole(models.Model):
    """
    User-Role association model.
    
    Links users to roles with optional context (organization, project).
    Supports role assignment at different levels:
    - System-wide (no context)
    - Organization-level (organization specified)
    - Project-level (project specified)
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the user-role assignment"
    )
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_index=True,
        help_text="User to whom the role is assigned"
    )
    
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        db_index=True,
        help_text="Role assigned to the user"
    )
    
    organization = models.ForeignKey(
        'authentication.Organization',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_roles',
        db_index=True,
        help_text="Organization context (optional)"
    )
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='user_roles',
        db_index=True,
        help_text="Project context (optional, for project-specific roles)"
    )
    
    is_active = models.BooleanField(
        default=True,
        db_index=True,
        help_text="Whether this role assignment is currently active"
    )
    
    assigned_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='roles_assigned',
        help_text="User who assigned this role"
    )
    
    assigned_at = models.DateTimeField(
        default=timezone.now,
        help_text="When the role was assigned"
    )
    
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the role assignment expires (optional)"
    )
    
    notes = models.TextField(
        blank=True,
        help_text="Additional notes about this role assignment"
    )
    
    class Meta:
        db_table = 'user_roles'
        ordering = ['-assigned_at']
        verbose_name = 'User Role'
        verbose_name_plural = 'User Roles'
        unique_together = [
            ['user', 'role', 'organization', 'project']
        ]
        indexes = [
            models.Index(fields=['user', 'is_active'], name='ur_user_active_idx'),
            models.Index(fields=['role', 'is_active'], name='ur_role_active_idx'),
            models.Index(fields=['organization', 'is_active'], name='ur_org_active_idx'),
            models.Index(fields=['project', 'is_active'], name='ur_project_active_idx'),
        ]
    
    def __str__(self):
        context = ""
        if self.project:
            context = f" on {self.project.name}"
        elif self.organization:
            context = f" at {self.organization.name}"
        return f"{self.user.get_full_name()} - {self.role.name}{context}"
    
    @property
    def is_expired(self):
        """Check if role assignment has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_valid(self):
        """Check if role assignment is currently valid"""
        return self.is_active and not self.is_expired
    
    def deactivate(self):
        """Deactivate this role assignment"""
        self.is_active = False
        self.save(update_fields=['is_active'])
