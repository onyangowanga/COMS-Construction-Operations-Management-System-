"""
Django Admin configuration for Authentication models
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

from .models import User, ProjectAccess, AuditLog, Organization


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    """Organization admin interface"""
    
    list_display = ['name', 'org_type', 'owner', 'is_active', 'member_count', 'created_at']
    list_filter = ['org_type', 'is_active', 'created_at']
    search_fields = ['name', 'registration_number', 'tax_id', 'owner__username', 'owner__email']
    raw_id_fields = ['owner']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Organization Details'), {
            'fields': ('name', 'org_type', 'owner', 'is_active')
        }),
        (_('Registration Information'), {
            'fields': ('registration_number', 'tax_id', 'default_currency', 'fiscal_year_start'),
            'classes': ('collapse',)
        }),
        (_('Contact Information'), {
            'fields': ('email', 'phone', 'address', 'city', 'country', 'website'),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def member_count(self, obj):
        """Display count of organization members"""
        return obj.members.count()
    member_count.short_description = 'Members'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('owner').prefetch_related('members')


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Custom User admin interface"""
    
    list_display = ['username', 'email', 'system_role', 'organization', 'is_active', 'is_verified', 'date_joined']
    list_filter = ['system_role', 'is_active', 'is_verified', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'organization__name', 'phone']
    ordering = ['-date_joined']
    
    fieldsets = (
        (None, {'fields': ('username', 'password')}),
        (_('Personal info'), {'fields': ('first_name', 'last_name', 'email', 'phone', 'job_title', 'organization', 'profile_picture')}),
        (_('UI Preferences'), {'fields': ('ui_theme', 'ui_timezone', 'ui_language', 'ui_compact_mode'), 'classes': ('collapse',)}),
        (_('Role & Permissions'), {'fields': ('system_role', 'is_verified', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        (_('Security'), {'fields': ('last_login_ip', 'failed_login_attempts', 'locked_until'), 'classes': ('collapse',)}),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'system_role', 'organization'),
        }),
    )
    
    readonly_fields = ['date_joined', 'last_login']
    
    raw_id_fields = ['organization']
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related('organization')


@admin.register(ProjectAccess)
class ProjectAccessAdmin(admin.ModelAdmin):
    """Project Access admin interface"""
    
    list_display = ['user', 'project', 'project_role', 'is_active', 'assigned_at', 'assigned_by']
    list_filter = ['project_role', 'is_active', 'assigned_at', 'can_edit', 'can_manage_budget']
    search_fields = ['user__username', 'user__email', 'project__name', 'project__code']
    raw_id_fields = ['user', 'project', 'assigned_by']
    date_hierarchy = 'assigned_at'
    ordering = ['-assigned_at']
    
    fieldsets = (
        (_('Access Details'), {
            'fields': ('user', 'project', 'project_role', 'is_active')
        }),
        (_('Permissions'), {
            'fields': ('can_edit', 'can_manage_budget', 'can_manage_workers', 'can_approve_documents', 'can_view_financials'),
            'classes': ('collapse',)
        }),
        (_('Audit Information'), {
            'fields': ('assigned_by', 'assigned_at', 'removed_at', 'notes'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['assigned_at']
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('user', 'project', 'assigned_by')
    
    actions = ['deactivate_access', 'activate_access']
    
    def deactivate_access(self, request, queryset):
        """Bulk deactivate project access"""
        for access in queryset:
            access.deactivate()
        self.message_user(request, f"{queryset.count()} access records deactivated.")
    deactivate_access.short_description = "Deactivate selected access"
    
    def activate_access(self, request, queryset):
        """Bulk activate project access"""
        queryset.update(is_active=True, removed_at=None)
        self.message_user(request, f"{queryset.count()} access records activated.")
    activate_access.short_description = "Activate selected access"


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Audit Log admin interface (read-only)"""
    
    list_display = ['timestamp', 'action', 'user', 'ip_address', 'user_agent_short']
    list_filter = ['action', 'timestamp']
    search_fields = ['user__username', 'user__email', 'ip_address']
    date_hierarchy = 'timestamp'
    ordering = ['-timestamp']
    
    readonly_fields = ['user', 'action', 'ip_address', 'user_agent', 'details', 'timestamp']
    
    def has_add_permission(self, request):
        """Prevent manual creation of audit logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Prevent deletion of audit logs"""
        return False
    
    def user_agent_short(self, obj):
        """Show truncated user agent"""
        return obj.user_agent[:50] + '...' if len(obj.user_agent) > 50 else obj.user_agent
    user_agent_short.short_description = 'User Agent'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('user')

