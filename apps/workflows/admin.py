from django.contrib import admin
from .models import Approval, ProjectActivity


@admin.register(Approval)
class ApprovalAdmin(admin.ModelAdmin):
    list_display = ['approval_type', 'status', 'amount', 'requested_by', 'requested_at', 'approved_by']
    list_filter = ['approval_type', 'status', 'requested_at']
    search_fields = ['reason', 'notes']
    readonly_fields = ['requested_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Approval Information', {
            'fields': ('approval_type', 'status', 'amount', 'reason')
        }),
        ('Object References', {
            'fields': ('expense_id', 'supplier_payment_id', 'consultant_payment_id', 'lpo_id')
        }),
        ('Request Details', {
            'fields': ('requested_by', 'requested_at')
        }),
        ('Approval Details', {
            'fields': ('approved_by', 'approved_at', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(ProjectActivity)
class ProjectActivityAdmin(admin.ModelAdmin):
    list_display = ['activity_type', 'project_id', 'description', 'amount', 'performed_by', 'created_at']
    list_filter = ['activity_type', 'created_at']
    search_fields = ['description', 'project_id']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Activity Information', {
            'fields': ('project_id', 'activity_type', 'description', 'amount')
        }),
        ('Related Object', {
            'fields': ('related_object_type', 'related_object_id')
        }),
        ('Performer', {
            'fields': ('performed_by',)
        }),
        ('Metadata', {
            'fields': ('metadata',)
        }),
        ('Timestamp', {
            'fields': ('created_at',)
        }),
    )
