"""
Reporting Engine - Admin Interface

Django admin configuration for report management.
"""

from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from apps.reporting.models import Report, ReportSchedule, ReportExecution, ReportWidget


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin interface for Report model"""
    
    list_display = [
        'name', 'report_type', 'organization', 'is_active',
        'is_public', 'executions_count', 'created_at'
    ]
    list_filter = ['report_type', 'is_active', 'is_public', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['id', 'created_at', 'updated_at', 'executions_count', 'last_execution_info']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'name', 'description', 'report_type')
        }),
        ('Configuration', {
            'fields': ('default_parameters', 'cache_duration', 'is_active', 'is_public')
        }),
        ('Statistics', {
            'fields': ('executions_count', 'last_execution_info', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def executions_count(self, obj):
        """Display total executions count"""
        count = obj.total_executions
        if count:
            url = reverse('admin:reporting_reportexecution_changelist')
            return format_html(
                '<a href="{}?report__id__exact={}">{}</a>',
                url, obj.id, count
            )
        return '0'
    executions_count.short_description = 'Executions'
    
    def last_execution_info(self, obj):
        """Display last execution information"""
        execution = obj.last_execution
        if execution:
            status_colors = {
                'COMPLETED': 'green',
                'FAILED': 'red',
                'PROCESSING': 'orange',
                'PENDING': 'grey',
                'CACHED': 'blue'
            }
            color = status_colors.get(execution.status, 'black')
            
            return format_html(
                '<span style="color: {};">{}</span> - {}',
                color,
                execution.status,
                execution.created_at.strftime('%Y-%m-%d %H:%M')
            )
        return '-'
    last_execution_info.short_description = 'Last Execution'


@admin.register(ReportSchedule)
class ReportScheduleAdmin(admin.ModelAdmin):
    """Admin interface for ReportSchedule model"""
    
    list_display = [
        'name', 'report', 'frequency', 'export_format',
        'is_active', 'next_run_display', 'due_status'
    ]
    list_filter = ['frequency', 'delivery_method', 'is_active', 'next_run']
    search_fields = ['name', 'report__name']
    readonly_fields = ['id', 'last_run', 'next_run', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'report', 'name', 'frequency', 'cron_expression')
        }),
        ('Export Settings', {
            'fields': ('export_format', 'parameters')
        }),
        ('Delivery Settings', {
            'fields': ('delivery_method', 'recipients')
        }),
        ('Schedule Status', {
            'fields': ('is_active', 'last_run', 'next_run', 'created_by', 'created_at', 'updated_at')
        }),
    )
    
    def next_run_display(self, obj):
        """Display next scheduled run"""
        if obj.next_run:
            return obj.next_run.strftime('%Y-%m-%d %H:%M')
        return '-'
    next_run_display.short_description = 'Next Run'
    
    def due_status(self, obj):
        """Display if schedule is due"""
        if obj.is_due:
            return format_html('<span style="color: red; font-weight: bold;">● DUE</span>')
        return format_html('<span style="color: green;">○ Scheduled</span>')
    due_status.short_description = 'Status'


@admin.register(ReportExecution)
class ReportExecutionAdmin(admin.ModelAdmin):
    """Admin interface for ReportExecution model"""
    
    list_display = [
        'report', 'status_badge', 'export_format',
        'execution_time_display', 'file_size_display',
        'row_count', 'created_at'
    ]
    list_filter = ['status', 'export_format', 'created_at']
    search_fields = ['report__name', 'executed_by__username']
    readonly_fields = [
        'id', 'report', 'schedule', 'status', 'export_format',
        'parameters', 'file_path', 'file_size_display', 'row_count',
        'execution_time_display', 'error_display', 'cache_key',
        'executed_by', 'created_at', 'completed_at', 'duration_display'
    ]
    
    fieldsets = (
        ('Execution Information', {
            'fields': (
                'id', 'report', 'schedule', 'status', 'export_format',
                'executed_by', 'created_at', 'completed_at', 'duration_display'
            )
        }),
        ('Parameters', {
            'fields': ('parameters',)
        }),
        ('Results', {
            'fields': (
                'file_path', 'file_size_display', 'row_count',
                'execution_time_display', 'cache_key'
            )
        }),
        ('Error Information', {
            'fields': ('error_display',),
            'classes': ('collapse',)
        }),
    )
    
    def status_badge(self, obj):
        """Display status with colored badge"""
        status_colors = {
            'COMPLETED': '#28a745',  # Green
            'FAILED': '#dc3545',     # Red
            'PROCESSING': '#ffc107', # Yellow
            'PENDING': '#6c757d',    # Grey
            'CACHED': '#17a2b8'      # Blue
        }
        color = status_colors.get(obj.status, '#000000')
        
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 10px; border-radius: 3px; font-weight: bold;">{}</span>',
            color, obj.status
        )
    status_badge.short_description = 'Status'
    
    def execution_time_display(self, obj):
        """Display execution time in seconds"""
        if obj.execution_time:
            return f"{obj.execution_time:.2f}s"
        return '-'
    execution_time_display.short_description = 'Execution Time'
    
    def file_size_display(self, obj):
        """Display file size in human-readable format"""
        if obj.file_size:
            size = obj.file_size
            for unit in ['B', 'KB', 'MB', 'GB']:
                if size < 1024:
                    return f"{size:.2f} {unit}"
                size /= 1024
            return f"{size:.2f} TB"
        return '-'
    file_size_display.short_description = 'File Size'
    
    def duration_display(self, obj):
        """Display execution duration"""
        duration = obj.duration
        if duration:
            return str(duration)
        return '-'
    duration_display.short_description = 'Duration'
    
    def error_display(self, obj):
        """Display error information"""
        if obj.error_message:
            error_html = f"<strong>Error:</strong> {obj.error_message}<br/>"
            if obj.stack_trace:
                error_html += f"<br/><strong>Stack Trace:</strong><br/><pre>{obj.stack_trace}</pre>"
            return mark_safe(error_html)
        return '-'
    error_display.short_description = 'Error Details'
    
    def has_add_permission(self, request):
        """Prevent manual creation"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Allow deletion of old executions"""
        return True


@admin.register(ReportWidget)
class ReportWidgetAdmin(admin.ModelAdmin):
    """Admin interface for ReportWidget model"""
    
    list_display = [
        'name', 'widget_type', 'chart_type', 'organization',
        'display_order', 'is_active', 'preview'
    ]
    list_filter = ['widget_type', 'chart_type', 'is_active']
    search_fields = ['name', 'data_source']
    readonly_fields = ['id', 'created_at', 'updated_at']
    list_editable = ['display_order', 'is_active']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('id', 'organization', 'report', 'name', 'widget_type', 'chart_type')
        }),
        ('Data Configuration', {
            'fields': ('data_source', 'query_parameters', 'refresh_interval')
        }),
        ('Display Settings', {
            'fields': ('display_order', 'icon', 'color', 'is_active')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at')
        }),
    )
    
    def preview(self, obj):
        """Display widget preview"""
        if obj.icon:
            return format_html(
                '<span style="color: {}; font-size: 18px;">{}</span>',
                obj.color or '#000000',
                obj.icon
            )
        return '-'
    preview.short_description = 'Preview'
