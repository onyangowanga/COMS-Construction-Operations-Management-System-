"""
Portfolio Admin Configuration
"""
from django.contrib import admin
from apps.portfolio.models import ProjectMetrics


@admin.register(ProjectMetrics)
class ProjectMetricsAdmin(admin.ModelAdmin):
    """Admin interface for Project Metrics"""
    
    list_display = [
        'project',
        'risk_level',
        'project_health',
        'budget_utilization',
        'profit_margin',
        'cost_performance_index',
        'schedule_performance_index',
        'is_over_budget',
        'is_behind_schedule',
        'last_updated',
    ]
    
    list_filter = [
        'risk_level',
        'project_health',
        'is_over_budget',
        'is_behind_schedule',
        'last_updated',
    ]
    
    search_fields = [
        'project__code',
        'project__name',
    ]
    
    readonly_fields = [
        'id',
        'created_at',
        'last_updated',
    ]
    
    fieldsets = (
        ('Project Information', {
            'fields': ('id', 'project')
        }),
        ('Financial Metrics', {
            'fields': (
                'total_contract_value',
                'total_expenses',
                'total_revenue',
                'total_profit',
                'budget_utilization',
                'profit_margin',
            )
        }),
        ('Risk Assessment', {
            'fields': (
                'project_health',
                'risk_level',
                'is_over_budget',
                'is_behind_schedule',
            )
        }),
        ('Earned Value Metrics', {
            'fields': (
                'planned_value',
                'earned_value',
                'actual_cost',
                'cost_performance_index',
                'schedule_performance_index',
            )
        }),
        ('Schedule Metrics', {
            'fields': (
                'days_elapsed',
                'days_remaining',
                'schedule_variance_days',
            )
        }),
        ('Metadata', {
            'fields': ('created_at', 'last_updated')
        }),
    )
    
    def has_add_permission(self, request):
        """Metrics are created automatically by services, not manually"""
        return False
    
    actions = ['update_metrics']
    
    @admin.action(description='Update selected project metrics')
    def update_metrics(self, request, queryset):
        """Batch update selected project metrics"""
        from apps.portfolio.services import PortfolioAnalyticsService
        
        updated_count = 0
        for metrics in queryset:
            PortfolioAnalyticsService.compute_project_risk_indicators(
                str(metrics.project.id)
            )
            updated_count += 1
        
        self.message_user(
            request,
            f"Successfully updated {updated_count} project metrics."
        )
