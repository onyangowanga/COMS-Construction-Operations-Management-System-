from django.contrib import admin
from .models import DailySiteReport, MaterialDelivery, SiteIssue


@admin.register(DailySiteReport)
class DailySiteReportAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'report_date',
        'weather',
        'prepared_by',
        'has_issues',
        'created_at'
    ]
    list_filter = [
        'weather',
        'report_date',
        'project',
        'prepared_by'
    ]
    search_fields = [
        'project__name',
        'work_completed',
        'issues',
        'labour_summary'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'report_date'
    
    fieldsets = (
        ('Report Information', {
            'fields': ('project', 'report_date', 'weather', 'prepared_by')
        }),
        ('Site Details', {
            'fields': ('labour_summary', 'work_completed', 'materials_delivered')
        }),
        ('Issues & Concerns', {
            'fields': ('issues',)
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(MaterialDelivery)
class MaterialDeliveryAdmin(admin.ModelAdmin):
    list_display = [
        'delivery_note_number',
        'project',
        'material_name',
        'quantity',
        'unit',
        'supplier_display',
        'delivery_date',
        'status',
        'received_by'
    ]
    list_filter = [
        'status',
        'delivery_date',
        'project',
        'supplier'
    ]
    search_fields = [
        'delivery_note_number',
        'material_name',
        'supplier_name',
        'project__name'
    ]
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'delivery_date'
    
    fieldsets = (
        ('Delivery Information', {
            'fields': ('project', 'delivery_note_number', 'delivery_date')
        }),
        ('Material Details', {
            'fields': ('material_name', 'quantity', 'unit')
        }),
        ('Supplier Information', {
            'fields': ('supplier', 'supplier_name')
        }),
        ('Reception', {
            'fields': ('received_by', 'status', 'notes')
        }),
        ('Metadata', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SiteIssue)
class SiteIssueAdmin(admin.ModelAdmin):
    list_display = [
        'title',
        'project',
        'severity',
        'status',
        'reported_by',
        'assigned_to',
        'reported_date',
        'is_high_priority'
    ]
    list_filter = [
        'severity',
        'status',
        'project',
        'reported_date'
    ]
    search_fields = [
        'title',
        'description',
        'project__name',
        'resolution_notes'
    ]
    readonly_fields = ['reported_date', 'created_at', 'updated_at']
    date_hierarchy = 'reported_date'
    
    fieldsets = (
        ('Issue Information', {
            'fields': ('project', 'title', 'description')
        }),
        ('Classification', {
            'fields': ('severity', 'status')
        }),
        ('Assignment', {
            'fields': ('reported_by', 'assigned_to')
        }),
        ('Resolution', {
            'fields': ('resolved_date', 'resolution_notes')
        }),
        ('Metadata', {
            'fields': ('reported_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_resolved', 'mark_as_in_progress']
    
    def mark_as_resolved(self, request, queryset):
        from django.utils import timezone
        queryset.update(status='RESOLVED', resolved_date=timezone.now())
        self.message_user(request, f"{queryset.count()} issues marked as resolved.")
    mark_as_resolved.short_description = "Mark selected issues as resolved"
    
    def mark_as_in_progress(self, request, queryset):
        queryset.update(status='IN_PROGRESS')
        self.message_user(request, f"{queryset.count()} issues marked as in progress.")
    mark_as_in_progress.short_description = "Mark selected issues as in progress"
