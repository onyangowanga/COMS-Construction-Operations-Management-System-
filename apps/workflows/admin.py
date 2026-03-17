from django.contrib import admin
from .models import (
    Approval,
    ProjectActivity,
    WorkflowDefinition,
    WorkflowHistory,
    WorkflowInstance,
    WorkflowState,
    WorkflowTransition,
)


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


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['module', 'name', 'is_active', 'created_at']
    list_filter = ['module', 'is_active']
    search_fields = ['module', 'name']


@admin.register(WorkflowState)
class WorkflowStateAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'is_initial', 'is_terminal', 'sort_order']
    list_filter = ['workflow__module', 'is_initial', 'is_terminal']
    search_fields = ['name', 'workflow__name', 'workflow__module']


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'from_state', 'action', 'to_state']
    list_filter = ['workflow__module', 'action']
    search_fields = ['workflow__name', 'action', 'from_state__name', 'to_state__name']


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['module', 'entity_id', 'current_state', 'last_transition_by', 'last_transition_at']
    list_filter = ['module', 'current_state__name']
    search_fields = ['module', 'entity_id']
    readonly_fields = ['history', 'created_at', 'updated_at']


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = ['instance', 'action', 'from_state', 'to_state', 'performed_by', 'timestamp']
    list_filter = ['instance__module', 'action']
    search_fields = ['instance__module', 'comment', 'action']
    readonly_fields = ['timestamp']
