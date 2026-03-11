"""
Django Admin configuration for Approvals app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ProjectApproval


@admin.register(ProjectApproval)
class ProjectApprovalAdmin(admin.ModelAdmin):
    list_display = [
        'project', 'authority', 'approval_type', 
        'status_display', 'application_date', 'approval_date', 
        'expiry_status', 'reference_number'
    ]
    list_filter = ['authority', 'approval_type', 'status', 'application_date', 'approval_date']
    search_fields = ['project__name', 'project__code', 'reference_number', 'notes']
    autocomplete_fields = ['project', 'document']
    date_hierarchy = 'application_date'
    ordering = ['-application_date']
    
    fieldsets = (
        (_('Approval Information'), {
            'fields': ('project', 'authority', 'approval_type')
        }),
        (_('Status & Dates'), {
            'fields': ('status', 'application_date', 'approval_date', 'expiry_date')
        }),
        (_('Reference & Document'), {
            'fields': ('reference_number', 'document')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def status_display(self, obj):
        """Display status with color coding"""
        colors = {
            'PENDING': 'orange',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'EXPIRED': 'gray',
        }
        color = colors.get(obj.status, 'black')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color, obj.get_status_display()
        )
    status_display.short_description = _('Status')
    
    def expiry_status(self, obj):
        """Display expiry status"""
        if not obj.expiry_date:
            return "-"
        
        from datetime import date
        today = date.today()
        
        if obj.expiry_date < today:
            return format_html('<span style="color: red;">✗ Expired</span>')
        elif (obj.expiry_date - today).days <= 30:
            return format_html('<span style="color: orange;">⚠ Expiring Soon</span>')
        else:
            return format_html('<span style="color: green;">✓ Valid</span>')
    expiry_status.short_description = _('Expiry')
