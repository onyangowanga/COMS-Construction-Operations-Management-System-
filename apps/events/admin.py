"""
Event Logging Admin Interface

This module provides Django admin interface for viewing and managing system events.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.db.models import Count
from django.urls import reverse
from django.utils import timezone
import json

from apps.events.models import SystemEvent


class EventTypeCategoryFilter(admin.SimpleListFilter):
    """Filter events by category"""
    title = 'Event Category'
    parameter_name = 'category'
    
    def lookups(self, request, model_admin):
        """Return list of categories"""
        categories = set(SystemEvent.EVENT_CATEGORIES.values())
        return [(cat, cat.replace('_', ' ').title()) for cat in sorted(categories)]
    
    def queryset(self, request, queryset):
        """Filter queryset by category"""
        if self.value():
            event_types = [
                event_type for event_type, cat in SystemEvent.EVENT_CATEGORIES.items()
                if cat == self.value()
            ]
            return queryset.filter(event_type__in=event_types)
        return queryset


class ResponseStatusFilter(admin.SimpleListFilter):
    """Filter by HTTP response status groups"""
    title = 'Response Status'
    parameter_name = 'status_group'
    
    def lookups(self, request, model_admin):
        return [
            ('2xx', '2xx - Success'),
            ('4xx', '4xx - Client Error'),
            ('5xx', '5xx - Server Error'),
        ]
    
    def queryset(self, request, queryset):
        if self.value() == '2xx':
            return queryset.filter(response_status__gte=200, response_status__lt=300)
        elif self.value() == '4xx':
            return queryset.filter(response_status__gte=400, response_status__lt=500)
        elif self.value() == '5xx':
            return queryset.filter(response_status__gte=500, response_status__lt=600)
        return queryset


@admin.register(SystemEvent)
class SystemEventAdmin(admin.ModelAdmin):
    """Admin interface for SystemEvent model"""
    
    list_display = [
        'id_short',
        'event_type_badge',
        'category_badge',
        'user_display',
        'entity_display_admin',
        'project_display',
        'timestamp_display',
        'status_badge',
        'duration_display',
    ]
    
    list_filter = [
        EventTypeCategoryFilter,
        'event_type',
        ('user', admin.RelatedOnlyFieldListFilter),
        ('organization', admin.RelatedOnlyFieldListFilter),
        ('project', admin.RelatedOnlyFieldListFilter),
        ResponseStatusFilter,
        ('timestamp', admin.DateFieldListFilter),
    ]
    
    search_fields = [
        'id',
        'event_type',
        'user__email',
        'user__first_name',
        'user__last_name',
        'organization__name',
        'project__name',
        'request_path',
        'ip_address',
        'metadata',
    ]
    
    readonly_fields = [
        'id',
        'event_type',
        'entity_type',
        'entity_id',
        'user',
        'organization',
        'project',
        'timestamp',
        'metadata_display',
        'ip_address',
        'user_agent',
        'request_path',
        'request_method',
        'response_status',
        'duration_ms',
    ]
    
    date_hierarchy = 'timestamp'
    
    ordering = ['-timestamp']
    
    list_per_page = 50
    
    fieldsets = (
        ('Event Information', {
            'fields': (
                'id',
                'event_type',
                'timestamp',
            )
        }),
        ('Context', {
            'fields': (
                'user',
                'organization',
                'project',
            )
        }),
        ('Related Entity', {
            'fields': (
                'entity_type',
                'entity_id',
            )
        }),
        ('Request Details', {
            'fields': (
                'request_method',
                'request_path',
                'response_status',
                'duration_ms',
                'ip_address',
                'user_agent',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'metadata_display',
            ),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """Disable adding events through admin (use services instead)"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable changing events (immutable audit log)"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion only for superusers"""
        return request.user.is_superuser
    
    def id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def event_type_badge(self, obj):
        """Display event type with color coding"""
        category = obj.category
        
        # Color mapping by category
        color_map = {
            'authentication': '#007bff',  # Blue
            'organization': '#6610f2',     # Purple
            'project': '#6f42c1',          # Indigo
            'contract': '#e83e8c',         # Pink
            'subcontract': '#fd7e14',      # Orange
            'document': '#20c997',         # Teal
            'variation': '#17a2b8',        # Cyan
            'claim': '#28a745',            # Green
            'payment': '#ffc107',          # Yellow
            'approval': '#dc3545',         # Red
            'report': '#6c757d',           # Gray
            'procurement': '#343a40',      # Dark
            'notification': '#007bff',     # Blue
            'system': '#6c757d',           # Gray
            'api': '#000000',              # Black
        }
        
        color = color_map.get(category, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; white-space: nowrap;">{}</span>',
            color,
            obj.get_event_type_display()
        )
    event_type_badge.short_description = 'Event Type'
    
    def category_badge(self, obj):
        """Display category badge"""
        category = obj.category.replace('_', ' ').title()
        return format_html(
            '<span style="background-color: #f8f9fa; color: #495057; padding: 2px 6px; '
            'border-radius: 3px; font-size: 10px; border: 1px solid #dee2e6;">{}</span>',
            category
        )
    category_badge.short_description = 'Category'
    
    def user_display(self, obj):
        """Display user with link to admin"""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name() or obj.user.email)
        return format_html('<span style="color: #6c757d;">System</span>')
    user_display.short_description = 'User'
    
    def entity_display_admin(self, obj):
        """Display related entity with link if possible"""
        if obj.entity:
            return format_html(
                '<span title="{}">{}</span>',
                obj.entity_type.model,
                str(obj.entity)[:50]
            )
        return '-'
    entity_display_admin.short_description = 'Entity'
    
    def project_display(self, obj):
        """Display project with link"""
        if obj.project:
            url = reverse('admin:projects_project_change', args=[obj.project.pk])
            return format_html('<a href="{}">{}</a>', url, obj.project.name)
        return '-'
    project_display.short_description = 'Project'
    
    def timestamp_display(self, obj):
        """Display timestamp with relative time"""
        return format_html(
            '<span title="{}">{}</span>',
            obj.timestamp.strftime('%Y-%m-%d %H:%M:%S'),
            obj.time_since + ' ago'
        )
    timestamp_display.short_description = 'When'
    
    def status_badge(self, obj):
        """Display HTTP status code with color"""
        if obj.response_status:
            if obj.response_status < 300:
                color = '#28a745'  # Green
            elif obj.response_status < 400:
                color = '#17a2b8'  # Cyan
            elif obj.response_status < 500:
                color = '#ffc107'  # Yellow
            else:
                color = '#dc3545'  # Red
            
            return format_html(
                '<span style="background-color: {}; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
                color,
                obj.response_status
            )
        return '-'
    status_badge.short_description = 'Status'
    
    def duration_display(self, obj):
        """Display request duration with color coding"""
        if obj.duration_ms is not None:
            # Color code by performance
            if obj.duration_ms < 100:
                color = '#28a745'  # Green - Fast
            elif obj.duration_ms < 500:
                color = '#ffc107'  # Yellow - Medium
            elif obj.duration_ms < 1000:
                color = '#fd7e14'  # Orange - Slow
            else:
                color = '#dc3545'  # Red - Very slow
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} ms</span>',
                color,
                obj.duration_ms
            )
        return '-'
    duration_display.short_description = 'Duration'
    
    def metadata_display(self, obj):
        """Display formatted metadata JSON"""
        if obj.metadata:
            formatted_json = json.dumps(obj.metadata, indent=2)
            return format_html('<pre style="margin: 0;">{}</pre>', formatted_json)
        return '-'
    metadata_display.short_description = 'Metadata'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'user',
            'organization',
            'project',
            'entity_type'
        )


# Custom admin actions
@admin.action(description='Export selected events as JSON')
def export_events_json(modeladmin, request, queryset):
    """Export selected events as JSON"""
    # This would need to be implemented with a file download
    # For now, just a placeholder
    pass


# Register the action
SystemEventAdmin.actions = [export_events_json]
