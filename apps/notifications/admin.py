"""
Django Admin Configuration for Notification Engine

Provides admin interface with:
- Notification management
- Preference management
- Template management
- Batch tracking
- Filters and search
- Custom actions
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils import timezone
from django.urls import reverse
from django.db.models import Count

from .models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationBatch,
    NotificationType,
    NotificationPriority
)
from .tasks import send_email_task, send_sms_task


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    """Admin interface for Notification model"""
    
    list_display = [
        'id_short',
        'user',
        'title_truncated',
        'notification_type_badge',
        'priority_badge',
        'is_read_badge',
        'email_sent_badge',
        'sms_sent_badge',
        'created_at',
        'actions_column'
    ]
    
    list_filter = [
        'notification_type',
        'priority',
        'is_read',
        'email_sent',
        'sms_sent',
        'created_at',
        ('user', admin.RelatedOnlyFieldListFilter),
    ]
    
    search_fields = [
        'id',
        'title',
        'message',
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name'
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'updated_at',
        'read_at',
        'email_sent_at',
        'sms_sent_at',
        'entity_type',
        'entity_id'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'user',
                'title',
                'message',
                'notification_type',
                'priority'
            )
        }),
        ('Entity Link', {
            'fields': (
                'entity_type',
                'entity_id'
            ),
            'classes': ('collapse',)
        }),
        ('Action Configuration', {
            'fields': (
                'action_url',
                'action_label'
            )
        }),
        ('Status', {
            'fields': (
                'is_read',
                'read_at',
                'email_sent',
                'email_sent_at',
                'sms_sent',
                'sms_sent_at'
            )
        }),
        ('Metadata', {
            'fields': (
                'metadata',
                'expires_at'
            ),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    date_hierarchy = 'created_at'
    
    actions = [
        'mark_as_read',
        'mark_as_unread',
        'send_email',
        'send_sms',
        'delete_selected'
    ]
    
    def id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def title_truncated(self, obj):
        """Display truncated title"""
        if len(obj.title) > 50:
            return obj.title[:50] + '...'
        return obj.title
    title_truncated.short_description = 'Title'
    
    def notification_type_badge(self, obj):
        """Display notification type with color badge"""
        colors = {
            NotificationType.SYSTEM: '#6c757d',
            NotificationType.WORKFLOW: '#0d6efd',
            NotificationType.FINANCIAL: '#198754',
            NotificationType.DOCUMENT: '#fd7e14',
            NotificationType.REPORT: '#6f42c1',
            NotificationType.DEADLINE: '#dc3545',
            NotificationType.APPROVAL: '#0dcaf0',
            NotificationType.VARIATION: '#ffc107',
            NotificationType.CONTRACT: '#20c997',
            NotificationType.PROCUREMENT: '#d63384',
        }
        
        color = colors.get(obj.notification_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'
    
    def priority_badge(self, obj):
        """Display priority with color badge"""
        colors = {
            NotificationPriority.LOW: '#6c757d',
            NotificationPriority.NORMAL: '#0d6efd',
            NotificationPriority.HIGH: '#ffc107',
            NotificationPriority.URGENT: '#dc3545',
        }
        
        color = colors.get(obj.priority, '#0d6efd')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def is_read_badge(self, obj):
        """Display read status with badge"""
        if obj.is_read:
            return format_html(
                '<span style="color: #198754; font-weight: bold;">✓ Read</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Unread</span>'
        )
    is_read_badge.short_description = 'Status'
    
    def email_sent_badge(self, obj):
        """Display email sent status"""
        if obj.email_sent:
            return format_html('<span style="color: #198754;">✓</span>')
        return format_html('<span style="color: #6c757d;">–</span>')
    email_sent_badge.short_description = 'Email'
    
    def sms_sent_badge(self, obj):
        """Display SMS sent status"""
        if obj.sms_sent:
            return format_html('<span style="color: #198754;">✓</span>')
        return format_html('<span style="color: #6c757d;">–</span>')
    sms_sent_badge.short_description = 'SMS'
    
    def actions_column(self, obj):
        """Display action buttons"""
        buttons = []
        
        if not obj.is_read:
            buttons.append(
                '<a href="#" onclick="markAsRead(\'{}\'); return false;" '
                'style="color: #0d6efd; text-decoration: none; margin-right: 10px;">Mark Read</a>'.format(obj.id)
            )
        
        if not obj.email_sent:
            buttons.append(
                '<a href="#" onclick="sendEmail(\'{}\'); return false;" '
                'style="color: #198754; text-decoration: none;">Send Email</a>'.format(obj.id)
            )
        
        return format_html(''.join(buttons))
    actions_column.short_description = 'Actions'
    
    def mark_as_read(self, request, queryset):
        """Action: Mark notifications as read"""
        count = 0
        for notification in queryset:
            if not notification.is_read:
                notification.mark_as_read()
                count += 1
        
        self.message_user(request, f'{count} notifications marked as read.')
    mark_as_read.short_description = 'Mark selected as read'
    
    def mark_as_unread(self, request, queryset):
        """Action: Mark notifications as unread"""
        count = 0
        for notification in queryset:
            if notification.is_read:
                notification.mark_as_unread()
                count += 1
        
        self.message_user(request, f'{count} notifications marked as unread.')
    mark_as_unread.short_description = 'Mark selected as unread'
    
    def send_email(self, request, queryset):
        """Action: Send email for selected notifications"""
        count = 0
        for notification in queryset:
            if not notification.email_sent:
                send_email_task.delay(str(notification.id))
                count += 1
        
        self.message_user(request, f'{count} email notifications queued for sending.')
    send_email.short_description = 'Send email for selected'
    
    def send_sms(self, request, queryset):
        """Action: Send SMS for selected notifications"""
        count = 0
        for notification in queryset:
            if not notification.sms_sent:
                send_sms_task.delay(str(notification.id))
                count += 1
        
        self.message_user(request, f'{count} SMS notifications queued for sending.')
    send_sms.short_description = 'Send SMS for selected'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    """Admin interface for NotificationPreference model"""
    
    list_display = [
        'user',
        'email_enabled_badge',
        'in_app_enabled_badge',
        'sms_enabled_badge',
        'digest_enabled_badge',
        'quiet_hours_badge',
        'phone_number',
        'updated_at'
    ]
    
    list_filter = [
        'email_enabled',
        'in_app_enabled',
        'sms_enabled',
        'digest_enabled',
        'quiet_hours_enabled',
        'system_notifications',
        'workflow_notifications',
        'financial_notifications'
    ]
    
    search_fields = [
        'user__username',
        'user__email',
        'user__first_name',
        'user__last_name',
        'sms_phone_number'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User', {
            'fields': ('user',)
        }),
        ('Channel Preferences', {
            'fields': (
                'email_enabled',
                'in_app_enabled',
                'sms_enabled',
                'sms_phone_number'
            )
        }),
        ('Notification Types', {
            'fields': (
                'system_notifications',
                'workflow_notifications',
                'financial_notifications',
                'document_notifications',
                'report_notifications',
                'deadline_notifications',
                'approval_notifications'
            )
        }),
        ('Digest Settings', {
            'fields': (
                'digest_enabled',
                'digest_time'
            )
        }),
        ('Quiet Hours', {
            'fields': (
                'quiet_hours_enabled',
                'quiet_hours_start',
                'quiet_hours_end'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def email_enabled_badge(self, obj):
        """Display email enabled status"""
        if obj.email_enabled:
            return format_html('<span style="color: #198754; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #dc3545;">✗</span>')
    email_enabled_badge.short_description = 'Email'
    
    def in_app_enabled_badge(self, obj):
        """Display in-app enabled status"""
        if obj.in_app_enabled:
            return format_html('<span style="color: #198754; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #dc3545;">✗</span>')
    in_app_enabled_badge.short_description = 'In-App'
    
    def sms_enabled_badge(self, obj):
        """Display SMS enabled status"""
        if obj.sms_enabled:
            return format_html('<span style="color: #198754; font-weight: bold;">✓</span>')
        return format_html('<span style="color: #dc3545;">✗</span>')
    sms_enabled_badge.short_description = 'SMS'
    
    def digest_enabled_badge(self, obj):
        """Display digest enabled status"""
        if obj.digest_enabled:
            return format_html('<span style="color: #0d6efd;">✓ {}</span>', obj.digest_time or '09:00')
        return format_html('<span style="color: #6c757d;">–</span>')
    digest_enabled_badge.short_description = 'Digest'
    
    def quiet_hours_badge(self, obj):
        """Display quiet hours status"""
        if obj.quiet_hours_enabled and obj.quiet_hours_start and obj.quiet_hours_end:
            return format_html(
                '<span style="color: #0d6efd;">{} - {}</span>',
                obj.quiet_hours_start.strftime('%H:%M'),
                obj.quiet_hours_end.strftime('%H:%M')
            )
        return format_html('<span style="color: #6c757d;">–</span>')
    quiet_hours_badge.short_description = 'Quiet Hours'
    
    def phone_number(self, obj):
        """Display phone number"""
        return obj.sms_phone_number or '–'
    phone_number.short_description = 'Phone'


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    """Admin interface for NotificationTemplate model"""
    
    list_display = [
        'code',
        'name',
        'notification_type_badge',
        'priority_badge',
        'is_active_badge',
        'usage_count',
        'updated_at'
    ]
    
    list_filter = [
        'notification_type',
        'priority',
        'is_active',
        'created_at'
    ]
    
    search_fields = [
        'code',
        'name',
        'description',
        'title_template',
        'message_template'
    ]
    
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Identification', {
            'fields': (
                'code',
                'name',
                'description',
                'notification_type',
                'priority',
                'is_active'
            )
        }),
        ('In-App Templates', {
            'fields': (
                'title_template',
                'message_template'
            )
        }),
        ('Email Templates', {
            'fields': (
                'email_subject_template',
                'email_body_template'
            ),
            'classes': ('collapse',)
        }),
        ('SMS Template', {
            'fields': (
                'sms_template',
            ),
            'classes': ('collapse',)
        }),
        ('Action Configuration', {
            'fields': (
                'action_url_template',
                'action_label'
            )
        }),
        ('Variables', {
            'fields': (
                'variables',
            ),
            'description': 'List of required template variables (JSON array)',
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )
    
    def notification_type_badge(self, obj):
        """Display notification type with color badge"""
        colors = {
            NotificationType.SYSTEM: '#6c757d',
            NotificationType.WORKFLOW: '#0d6efd',
            NotificationType.FINANCIAL: '#198754',
            NotificationType.DOCUMENT: '#fd7e14',
            NotificationType.REPORT: '#6f42c1',
            NotificationType.DEADLINE: '#dc3545',
            NotificationType.APPROVAL: '#0dcaf0',
        }
        
        color = colors.get(obj.notification_type, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_notification_type_display()
        )
    notification_type_badge.short_description = 'Type'
    
    def priority_badge(self, obj):
        """Display priority with color badge"""
        colors = {
            NotificationPriority.LOW: '#6c757d',
            NotificationPriority.NORMAL: '#0d6efd',
            NotificationPriority.HIGH: '#ffc107',
            NotificationPriority.URGENT: '#dc3545',
        }
        
        color = colors.get(obj.priority, '#0d6efd')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def is_active_badge(self, obj):
        """Display active status with badge"""
        if obj.is_active:
            return format_html(
                '<span style="color: #198754; font-weight: bold;">✓ Active</span>'
            )
        return format_html(
            '<span style="color: #dc3545; font-weight: bold;">✗ Inactive</span>'
        )
    is_active_badge.short_description = 'Status'
    
    def usage_count(self, obj):
        """Display usage count (placeholder)"""
        # Could be enhanced to count actual usage
        return '–'
    usage_count.short_description = 'Usage'


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    """Admin interface for NotificationBatch model"""
    
    list_display = [
        'id_short',
        'name',
        'template_name',
        'status_badge',
        'progress_bar',
        'success_rate_display',
        'created_by',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'created_at',
        ('created_by', admin.RelatedOnlyFieldListFilter),
        ('template', admin.RelatedOnlyFieldListFilter)
    ]
    
    search_fields = [
        'id',
        'name',
        'created_by__username'
    ]
    
    readonly_fields = [
        'id',
        'total_recipients',
        'sent_count',
        'failed_count',
        'created_at',
        'completed_at'
    ]
    
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'id',
                'name',
                'template',
                'created_by'
            )
        }),
        ('Progress', {
            'fields': (
                'status',
                'total_recipients',
                'sent_count',
                'failed_count'
            )
        }),
        ('Timestamps', {
            'fields': (
                'created_at',
                'completed_at'
            )
        })
    )
    
    date_hierarchy = 'created_at'
    
    def id_short(self, obj):
        """Display shortened UUID"""
        return str(obj.id)[:8]
    id_short.short_description = 'ID'
    
    def template_name(self, obj):
        """Display template name"""
        return obj.template.name if obj.template else '–'
    template_name.short_description = 'Template'
    
    def status_badge(self, obj):
        """Display status with color badge"""
        colors = {
            'PENDING': '#ffc107',
            'PROCESSING': '#0d6efd',
            'COMPLETED': '#198754',
            'FAILED': '#dc3545',
        }
        
        color = colors.get(obj.status, '#6c757d')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 11px; font-weight: bold;">{}</span>',
            color,
            obj.status
        )
    status_badge.short_description = 'Status'
    
    def progress_bar(self, obj):
        """Display progress bar"""
        if obj.total_recipients == 0:
            return format_html('<span style="color: #6c757d;">No recipients</span>')
        
        percentage = (obj.sent_count / obj.total_recipients) * 100
        
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px; overflow: hidden;">'
            '<div style="width: {}%; background-color: #198754; color: white; text-align: center; '
            'font-size: 11px; padding: 2px 0;">{:.0f}%</div>'
            '</div>',
            percentage,
            percentage
        )
    progress_bar.short_description = 'Progress'
    
    def success_rate_display(self, obj):
        """Display success rate"""
        if obj.total_recipients == 0:
            return '–'
        
        rate = obj.success_rate
        
        if rate >= 90:
            color = '#198754'
        elif rate >= 70:
            color = '#ffc107'
        else:
            color = '#dc3545'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">{:.1f}%</span>',
            color,
            rate
        )
    success_rate_display.short_description = 'Success Rate'
