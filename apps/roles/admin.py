"""
Django Admin Configuration for Role-Based Access Control

This module provides admin interfaces for managing roles, permissions, and user roles.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from apps.roles.models import Role, Permission, UserRole


@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    """
    Admin interface for Role model.
    """
    
    list_display = [
        'code',
        'name',
        'colored_system_role',
        'colored_active_status',
        'permission_count_display',
        'user_count_display',
        'created_at'
    ]
    
    list_filter = [
        'is_system_role',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'code',
        'name',
        'description'
    ]
    
    filter_horizontal = ['permissions']
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'permission_count_display',
        'user_count_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Settings', {
            'fields': ('is_system_role', 'is_active')
        }),
        ('Permissions', {
            'fields': ('permissions', 'permission_count_display'),
            'description': 'Select permissions for this role'
        }),
        ('Statistics', {
            'fields': ('user_count_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def colored_system_role(self, obj):
        """Display system role status with color."""
        if obj.is_system_role:
            return format_html(
                '<span style="color: #0066cc; font-weight: bold;">✓ System</span>'
            )
        return format_html(
            '<span style="color: #666;">Custom</span>'
        )
    colored_system_role.short_description = 'Type'
    
    def colored_active_status(self, obj):
        """Display active status with color."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: red;">○ Inactive</span>'
        )
    colored_active_status.short_description = 'Status'
    
    def permission_count_display(self, obj):
        """Display permission count with link."""
        count = obj.permission_count
        if count > 0:
            url = reverse('admin:roles_permission_changelist') + f'?roles__id__exact={obj.id}'
            return format_html(
                '<a href="{}">{} permission{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 permissions'
    permission_count_display.short_description = 'Permissions'
    
    def user_count_display(self, obj):
        """Display user count with link."""
        count = obj.user_count
        if count > 0:
            url = reverse('admin:roles_userrole_changelist') + f'?role__id__exact={obj.id}'
            return format_html(
                '<a href="{}">{} user{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 users'
    user_count_display.short_description = 'Users'
    
    def get_readonly_fields(self, request, obj=None):
        """Make code readonly for system roles."""
        readonly = list(self.readonly_fields)
        if obj and obj.is_system_role:
            readonly.append('code')
            readonly.append('is_system_role')
        return readonly
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of system roles."""
        if obj and obj.is_system_role:
            return False
        return super().has_delete_permission(request, obj)


@admin.register(Permission)
class PermissionAdmin(admin.ModelAdmin):
    """
    Admin interface for Permission model.
    """
    
    list_display = [
        'code',
        'name',
        'colored_category',
        'colored_active_status',
        'role_count_display',
        'created_at'
    ]
    
    list_filter = [
        'category',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'code',
        'name',
        'description'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'role_count_display'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('code', 'name', 'description')
        }),
        ('Categorization', {
            'fields': ('category', 'is_active')
        }),
        ('Statistics', {
            'fields': ('role_count_display',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    # Category colors for visual distinction
    CATEGORY_COLORS = {
        'project': '#0066cc',
        'financial': '#009688',
        'document': '#673ab7',
        'variation': '#ff9800',
        'claim': '#4caf50',
        'payment': '#2196f3',
        'approval': '#f44336',
        'report': '#9c27b0',
        'procurement': '#795548',
        'subcontract': '#607d8b',
        'site_operations': '#ff5722',
        'system': '#000000',
    }
    
    def colored_category(self, obj):
        """Display category with color coding."""
        color = self.CATEGORY_COLORS.get(obj.category, '#666')
        return format_html(
            '<span style="color: {}; font-weight: bold;">●</span> {}',
            color,
            obj.get_category_display()
        )
    colored_category.short_description = 'Category'
    
    def colored_active_status(self, obj):
        """Display active status with color."""
        if obj.is_active:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        return format_html(
            '<span style="color: red;">○ Inactive</span>'
        )
    colored_active_status.short_description = 'Status'
    
    def role_count_display(self, obj):
        """Display role count with link."""
        count = obj.role_count
        if count > 0:
            url = reverse('admin:roles_role_changelist') + f'?permissions__id__exact={obj.id}'
            return format_html(
                '<a href="{}">{} role{}</a>',
                url,
                count,
                's' if count != 1 else ''
            )
        return '0 roles'
    role_count_display.short_description = 'Roles'


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    """
    Admin interface for UserRole model.
    """
    
    list_display = [
        'user_link',
        'role_link',
        'colored_context',
        'colored_status',
        'colored_expiry',
        'assigned_by_link',
        'assigned_at'
    ]
    
    list_filter = [
        'is_active',
        'role',
        'assigned_at',
        'expires_at'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'role__name',
        'role__code',
        'notes'
    ]
    
    readonly_fields = [
        'id',
        'assigned_at',
        'is_expired_display',
        'is_valid_display'
    ]
    
    autocomplete_fields = [
        'user',
        'role',
        'organization',
        'project',
        'assigned_by'
    ]
    
    fieldsets = (
        ('Assignment', {
            'fields': ('user', 'role')
        }),
        ('Context', {
            'fields': ('organization', 'project'),
            'description': 'Define the scope of this role assignment'
        }),
        ('Status', {
            'fields': ('is_active', 'expires_at', 'is_expired_display', 'is_valid_display')
        }),
        ('Assignment Details', {
            'fields': ('assigned_by', 'assigned_at', 'notes')
        }),
        ('Metadata', {
            'fields': ('id',),
            'classes': ('collapse',)
        }),
    )
    
    def user_link(self, obj):
        """Display user as clickable link."""
        url = reverse('admin:auth_user_change', args=[obj.user.pk])
        return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.username)
    user_link.short_description = 'User'
    
    def role_link(self, obj):
        """Display role as clickable link."""
        url = reverse('admin:roles_role_change', args=[obj.role.pk])
        return format_html('<a href="{}">{}</a>', url, obj.role.name)
    role_link.short_description = 'Role'
    
    def colored_context(self, obj):
        """Display context (org/project) with formatting."""
        parts = []
        
        if obj.organization:
            org_url = reverse('admin:authentication_organization_change', args=[obj.organization.pk])
            parts.append(format_html('<a href="{}">🏢 {}</a>', org_url, obj.organization.name))
        
        if obj.project:
            proj_url = reverse('admin:projects_project_change', args=[obj.project.pk])
            parts.append(format_html('<a href="{}">📁 {}</a>', proj_url, obj.project.name))
        
        if not parts:
            return format_html('<span style="color: #999;">System-wide</span>')
        
        return mark_safe(' / '.join(parts))
    colored_context.short_description = 'Context'
    
    def colored_status(self, obj):
        """Display status with color."""
        if obj.is_valid:
            return format_html(
                '<span style="color: green; font-weight: bold;">● Active</span>'
            )
        elif obj.is_expired:
            return format_html(
                '<span style="color: orange;">⏱ Expired</span>'
            )
        else:
            return format_html(
                '<span style="color: red;">○ Inactive</span>'
            )
    colored_status.short_description = 'Status'
    
    def colored_expiry(self, obj):
        """Display expiry status with color."""
        if not obj.expires_at:
            return format_html('<span style="color: #666;">No expiry</span>')
        
        if obj.is_expired:
            return format_html(
                '<span style="color: red;">Expired: {}</span>',
                obj.expires_at.strftime('%Y-%m-%d')
            )
        
        return format_html(
            '<span style="color: orange;">Expires: {}</span>',
            obj.expires_at.strftime('%Y-%m-%d')
        )
    colored_expiry.short_description = 'Expiry'
    
    def assigned_by_link(self, obj):
        """Display assigned_by as clickable link."""
        if not obj.assigned_by:
            return format_html('<span style="color: #999;">System</span>')
        
        url = reverse('admin:auth_user_change', args=[obj.assigned_by.pk])
        return format_html('<a href="{}">{}</a>', url, obj.assigned_by.get_full_name() or obj.assigned_by.username)
    assigned_by_link.short_description = 'Assigned By'
    
    def is_expired_display(self, obj):
        """Display if assignment is expired."""
        if obj.is_expired:
            return format_html('<span style="color: red; font-weight: bold;">Yes</span>')
        return format_html('<span style="color: green;">No</span>')
    is_expired_display.short_description = 'Is Expired'
    
    def is_valid_display(self, obj):
        """Display if assignment is valid."""
        if obj.is_valid:
            return format_html('<span style="color: green; font-weight: bold;">Yes</span>')
        return format_html('<span style="color: red;">No</span>')
    is_valid_display.short_description = 'Is Valid'
    
    actions = ['deactivate_roles', 'activate_roles']
    
    def deactivate_roles(self, request, queryset):
        """Bulk action to deactivate role assignments."""
        count = queryset.update(is_active=False)
        self.message_user(request, f'{count} role assignment(s) deactivated.')
    deactivate_roles.short_description = 'Deactivate selected role assignments'
    
    def activate_roles(self, request, queryset):
        """Bulk action to activate role assignments."""
        count = queryset.update(is_active=True)
        self.message_user(request, f'{count} role assignment(s) activated.')
    activate_roles.short_description = 'Activate selected role assignments'
