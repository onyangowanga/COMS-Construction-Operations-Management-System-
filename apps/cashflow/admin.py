from django.contrib import admin
from .models import CashFlowForecast, PortfolioCashFlowSummary


@admin.register(CashFlowForecast)
class CashFlowForecastAdmin(admin.ModelAdmin):
    list_display = [
        'project',
        'forecast_month',
        'total_inflow',
        'total_outflow',
        'net_cash_flow',
        'cumulative_cash_balance',
        'is_actual',
    ]
    
    list_filter = [
        'is_actual',
        'forecast_month',
        'project__status',
    ]
    
    search_fields = [
        'project__name',
        'project__project_code',
    ]
    
    readonly_fields = [
        'total_inflow',
        'total_outflow',
        'net_cash_flow',
        'forecast_generated_at',
        'updated_at',
    ]
    
    fieldsets = (
        ('Project & Period', {
            'fields': ('project', 'forecast_month', 'is_actual')
        }),
        ('Inflows', {
            'fields': (
                'expected_valuations',
                'expected_client_payments',
                'expected_retention_releases',
                'expected_variation_order_payments',
                'total_inflow',
            )
        }),
        ('Outflows', {
            'fields': (
                'expected_supplier_payments',
                'expected_labour_costs',
                'expected_consultant_fees',
                'expected_procurement_payments',
                'expected_site_expenses',
                'expected_other_expenses',
                'total_outflow',
            )
        }),
        ('Calculated Metrics', {
            'fields': (
                'net_cash_flow',
                'cumulative_cash_balance',
            )
        }),
        ('Metadata', {
            'fields': ('forecast_generated_at', 'updated_at')
        }),
    )
    
    date_hierarchy = 'forecast_month'
    
    actions = ['recalculate_forecasts']
    
    def recalculate_forecasts(self, request, queryset):
        """Recalculate selected forecasts"""
        count = 0
        for forecast in queryset:
            forecast.save()  # Triggers auto-calculation
            count += 1
        
        self.message_user(request, f"Recalculated {count} forecasts successfully.")
    
    recalculate_forecasts.short_description = "Recalculate selected forecasts"


@admin.register(PortfolioCashFlowSummary)
class PortfolioCashFlowSummaryAdmin(admin.ModelAdmin):
    list_display = [
        'forecast_month',
        'total_portfolio_inflow',
        'total_portfolio_outflow',
        'net_portfolio_cash_flow',
       'cumulative_portfolio_balance',
        'active_projects_count',
        'projects_with_negative_flow',
    ]
    
    readonly_fields = [
        'forecast_generated_at',
        'updated_at',
    ]
    
    date_hierarchy = 'forecast_month'
    
    fieldsets = (
        ('Period', {
            'fields': ('forecast_month',)
        }),
        ('Portfolio Cash Flow', {
            'fields': (
                'total_portfolio_inflow',
                'total_portfolio_outflow',
                'net_portfolio_cash_flow',
                'cumulative_portfolio_balance',
            )
        }),
        ('Project Statistics', {
            'fields': (
                'active_projects_count',
                'projects_with_negative_flow',
            )
        }),
        ('Metadata', {
            'fields': ('forecast_generated_at', 'updated_at')
        }),
    )
