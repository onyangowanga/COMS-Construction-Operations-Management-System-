"""
Dashboard URL patterns.
"""
from django.urls import path
from . import views

app_name = 'dashboards'

urlpatterns = [
    # Project Dashboard
    path(
        'projects/<uuid:project_id>/dashboard/',
        views.project_dashboard,
        name='project_dashboard'
    ),
    
    # Project Dashboard HTMX Partials
    path(
        'projects/<uuid:project_id>/dashboard/partials/financial-summary/',
        views.project_financial_summary_partial,
        name='project_financial_summary_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/budget-variance/',
        views.project_budget_variance_partial,
        name='project_budget_variance_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/recent-activity/',
        views.project_recent_activity_partial,
        name='project_recent_activity_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/supplier-outstanding/',
        views.project_supplier_outstanding_partial,
        name='project_supplier_outstanding_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/unpaid-wages/',
        views.project_unpaid_wages_partial,
        name='project_unpaid_wages_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/valuation-summary/',
        views.project_valuation_summary_partial,
        name='project_valuation_summary_partial'
    ),
    path(
        'projects/<uuid:project_id>/dashboard/partials/site-operations-summary/',
        views.project_site_operations_summary_partial,
        name='project_site_operations_summary_partial'
    ),
    
    # Procurement Dashboard
    path(
        'procurement/',
        views.procurement_dashboard,
        name='procurement_dashboard'
    ),
    path(
        'procurement/partials/pending-approvals/',
        views.pending_lpo_approvals_partial,
        name='pending_lpo_approvals_partial'
    ),
    path(
        'procurement/partials/delivered-not-invoiced/',
        views.delivered_not_invoiced_partial,
        name='delivered_not_invoiced_partial'
    ),
    path(
        'procurement/partials/invoiced-not-paid/',
        views.invoiced_not_paid_partial,
        name='invoiced_not_paid_partial'
    ),
    
    # Finance Dashboard
    path(
        'finance/',
        views.finance_dashboard,
        name='finance_dashboard'
    ),
    path(
        'finance/partials/summary/',
        views.finance_summary_partial,
        name='finance_summary_partial'
    ),
    
    # Portfolio Dashboard
    path(
        'portfolio/',
        views.portfolio_dashboard,
        name='portfolio_dashboard'
    ),
    path(
        'portfolio/partials/summary/',
        views.portfolio_summary_partial,
        name='portfolio_summary_partial'
    ),
    path(
        'portfolio/partials/projects-table/',
        views.portfolio_projects_table_partial,
        name='portfolio_projects_table_partial'
    ),
    path(
        'portfolio/partials/risk-distribution/',
        views.portfolio_risk_distribution_partial,
        name='portfolio_risk_distribution_partial'
    ),
    path(
        'portfolio/partials/high-risk-projects/',
        views.portfolio_high_risk_projects_partial,
        name='portfolio_high_risk_partial'
    ),
    
    # Cash Flow Dashboard URLs
    path(
        'portfolio/cashflow/',
        views.cashflow_dashboard,
        name='cashflow_dashboard'
    ),
    path(
        'portfolio/cashflow/partials/summary/',
        views.cashflow_summary_partial,
        name='cashflow_summary_partial'
    ),
    path(
        'portfolio/cashflow/partials/chart-data/',
        views.cashflow_chart_data_partial,
        name='cashflow_chart_data_partial'
    ),
    path(
        'portfolio/cashflow/partials/negative-projects/',
        views.cashflow_negative_projects_partial,
        name='cashflow_negative_projects_partial'
    ),
    path(
        'portfolio/cashflow/partials/alerts/',
        views.cashflow_alerts_partial,
        name='cashflow_alerts_partial'
    ),
    path(
        'portfolio/cashflow/generate/',
        views.cashflow_generate_forecast,
        name='cashflow_generate_forecast'
    ),
]
