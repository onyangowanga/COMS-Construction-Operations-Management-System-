"""
Django Admin configuration for Projects app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import Project, ProjectStage


class ProjectStageInline(admin.TabularInline):
    """Inline for project construction stages"""
    model = ProjectStage
    extra = 0
    fields = ['name', 'order', 'is_completed', 'start_date', 'end_date', 'description']
    ordering = ['order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'name', 'client_name', 'contract_type', 
        'project_value_display', 'status', 'start_date', 
        'progress_indicator', 'created_at'
    ]
    list_filter = ['status', 'contract_type', 'project_type', 'created_at']
    search_fields = ['code', 'name', 'client_name', 'location']
    autocomplete_fields = ['organization']
    date_hierarchy = 'start_date'
    ordering = ['-created_at']
    inlines = [ProjectStageInline]
    
    # Enable autocomplete for this model when referenced in other admins
    def get_search_results(self, request, queryset, search_term):
        queryset, use_distinct = super().get_search_results(request, queryset, search_term)
        return queryset, use_distinct
    
    fieldsets = (
        (_('Project Information'), {
            'fields': ('organization', 'name', 'code', 'client_name', 'location')
        }),
        (_('Project Details'), {
            'fields': ('project_type', 'contract_type', 'project_value')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date')
        }),
        (_('Status'), {
            'fields': ('status', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def project_value_display(self, obj):
        """Display formatted project value"""
        if obj.project_value:
            return f"KES {obj.project_value:,.2f}"
        return "-"
    project_value_display.short_description = _('Project Value')
    project_value_display.admin_order_field = 'project_value'
    
    def progress_indicator(self, obj):
        """Visual progress indicator"""
        stages = obj.stages.all()
        if not stages:
            return "-"
        total = stages.count()
        completed = stages.filter(is_completed=True).count()
        percent = (completed / total * 100) if total > 0 else 0
        
        if percent >= 80:
            color = 'green'
        elif percent >= 40:
            color = 'orange'
        else:
            color = 'red'
        
        return format_html(
            '<span style="color: {};">{:.0f}% ({}/{})</span>',
            color, percent, completed, total
        )
    progress_indicator.short_description = _('Progress')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('organization').prefetch_related('stages')


@admin.register(ProjectStage)
class ProjectStageAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'order', 'is_completed', 'start_date', 'end_date']
    list_filter = ['is_completed', 'name']
    search_fields = ['name', 'project__name', 'project__code', 'description']
    autocomplete_fields = ['project']
    ordering = ['project', 'order']
    
    fieldsets = (
        (_('Stage Information'), {
            'fields': ('project', 'name', 'order', 'description')
        }),
        (_('Schedule'), {
            'fields': ('start_date', 'end_date', 'is_completed')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
