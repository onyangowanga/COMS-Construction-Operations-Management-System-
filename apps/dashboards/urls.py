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
]
