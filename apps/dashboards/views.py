"""
Dashboard views for operational monitoring using HTMX.
"""
from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from apps.projects.models import Project
from . import selectors


@login_required
@require_http_methods(["GET"])
def project_dashboard(request, project_id):
    """
    Main project dashboard view.
    
    URL: /projects/{id}/dashboard/
    """
    project = get_object_or_404(Project, id=project_id)
    
    context = {
        'project': project,
    }
    
    return render(request, 'dashboards/project_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def project_financial_summary_partial(request, project_id):
    """
    HTMX partial: Project financial summary.
    
    URL: /projects/{id}/dashboard/partials/financial-summary/
    """
    project = get_object_or_404(Project, id=project_id)
    summary = selectors.get_project_financial_summary(project_id)
    
    context = {
        'project': project,
        'summary': summary,
    }
    
    return render(request, 'dashboards/partials/financial_summary.html', context)


@login_required
@require_http_methods(["GET"])
def project_budget_variance_partial(request, project_id):
    """
    HTMX partial: Project budget variance.
    
    URL: /projects/{id}/dashboard/partials/budget-variance/
    """
    project = get_object_or_404(Project, id=project_id)
    variances = selectors.get_project_budget_variance(project_id)
    
    context = {
        'project': project,
        'variances': variances,
    }
    
    return render(request, 'dashboards/partials/budget_variance.html', context)


@login_required
@require_http_methods(["GET"])
def project_recent_activity_partial(request, project_id):
    """
    HTMX partial: Recent project activity.
    
    URL: /projects/{id}/dashboard/partials/recent-activity/
    """
    project = get_object_or_404(Project, id=project_id)
    limit = int(request.GET.get('limit', 20))
    activities = selectors.get_recent_project_activity(project_id, limit=limit)
    
    context = {
        'project': project,
        'activities': activities,
    }
    
    return render(request, 'dashboards/partials/recent_activity.html', context)


@login_required
@require_http_methods(["GET"])
def project_supplier_outstanding_partial(request, project_id):
    """
    HTMX partial: Outstanding supplier payments.
    
    URL: /projects/{id}/dashboard/partials/supplier-outstanding/
    """
    project = get_object_or_404(Project, id=project_id)
    outstanding = selectors.get_project_supplier_outstanding(project_id)
    
    context = {
        'project': project,
        'outstanding': outstanding,
    }
    
    return render(request, 'dashboards/partials/supplier_outstanding.html', context)


@login_required
@require_http_methods(["GET"])
def project_unpaid_wages_partial(request, project_id):
    """
    HTMX partial: Unpaid worker wages.
    
    URL: /projects/{id}/dashboard/partials/unpaid-wages/
    """
    project = get_object_or_404(Project, id=project_id)
    unpaid_wages = selectors.get_project_unpaid_wages(project_id)
    
    context = {
        'project': project,
        'unpaid_wages': unpaid_wages,
    }
    
    return render(request, 'dashboards/partials/unpaid_wages.html', context)


# Procurement Dashboard Views
@login_required
@require_http_methods(["GET"])
def procurement_dashboard(request):
    """
    Main procurement dashboard view.
    
    URL: /procurement/
    """
    context = {}
    return render(request, 'dashboards/procurement_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def pending_lpo_approvals_partial(request):
    """
    HTMX partial: Pending LPO approvals.
    
    URL: /procurement/partials/pending-approvals/
    """
    pending_lpos = selectors.get_pending_lpo_approvals()
    
    context = {
        'pending_lpos': pending_lpos,
    }
    
    return render(request, 'dashboards/partials/pending_lpo_approvals.html', context)


@login_required
@require_http_methods(["GET"])
def delivered_not_invoiced_partial(request):
    """
    HTMX partial: Delivered but not invoiced LPOs.
    
    URL: /procurement/partials/delivered-not-invoiced/
    """
    lpos = selectors.get_delivered_not_invoiced_lpos()
    
    context = {
        'lpos': lpos,
    }
    
    return render(request, 'dashboards/partials/delivered_not_invoiced.html', context)


@login_required
@require_http_methods(["GET"])
def invoiced_not_paid_partial(request):
    """
    HTMX partial: Invoiced but not paid LPOs.
    
    URL: /procurement/partials/invoiced-not-paid/
    """
    lpos = selectors.get_invoiced_not_paid_lpos()
    
    context = {
        'lpos': lpos,
    }
    
    return render(request, 'dashboards/partials/invoiced_not_paid.html', context)


# Finance Dashboard Views
@login_required
@require_http_methods(["GET"])
def finance_dashboard(request):
    """
    Main finance dashboard view.
    
    URL: /finance/
    """
    context = {}
    return render(request, 'dashboards/finance_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def finance_summary_partial(request):
    """
    HTMX partial: Organization-wide financial summary.
    
    URL: /finance/partials/summary/
    """
    summary = selectors.get_finance_summary()
    
    context = {
        'summary': summary,
    }
    
    return render(request, 'dashboards/partials/finance_summary.html', context)


@login_required
@require_http_methods(["GET"])
def project_valuation_summary_partial(request, project_id):
    """
    HTMX partial: Project valuation summary.
    
    URL: /projects/{id}/dashboard/partials/valuation-summary/
    """
    project = get_object_or_404(Project, id=project_id)
    valuation_summary = selectors.get_project_valuation_summary(str(project_id))
    
    context = {
        'project': project,
        'valuation_summary': valuation_summary,
    }
    
    return render(request, 'dashboards/partials/valuation_summary.html', context)


@login_required
def project_site_operations_summary_partial(request, project_id):
    """
    HTMX partial: Project site operations summary.
    
    URL: /projects/{id}/dashboard/partials/site-operations-summary/
    """
    project = get_object_or_404(Project, id=project_id)
    site_ops_summary = selectors.get_project_site_operations_summary(str(project_id))
    
    context = {
        'project': project,
        'site_ops_summary': site_ops_summary,
    }
    
    return render(request, 'dashboards/partials/site_operations_summary.html', context)


# Portfolio Dashboard Views
@login_required
@require_http_methods(["GET"])
def portfolio_dashboard(request):
    """
    Main portfolio dashboard view.
    
    URL: /portfolio/
    """
    context = {}
    return render(request, 'dashboards/portfolio_dashboard.html', context)


@login_required
@require_http_methods(["GET"])
def portfolio_summary_partial(request):
    """
    HTMX partial: Portfolio-wide summary metrics.
    
    URL: /portfolio/partials/summary/
    """
    from apps.portfolio import selectors as portfolio_selectors
    
    summary = portfolio_selectors.get_portfolio_summary()
    
    context = {
        'summary': summary,
    }
    
    return render(request, 'dashboards/partials/portfolio_summary.html', context)


@login_required
@require_http_methods(["GET"])
def portfolio_projects_table_partial(request):
    """
    HTMX partial: All projects with metrics table.
    
    URL: /portfolio/partials/projects-table/
    """
    from apps.portfolio import selectors as portfolio_selectors
    
    # Get filter parameters
    risk_level = request.GET.get('risk_level', '').upper()
    health = request.GET.get('health', '').upper()
    show_attention_only = request.GET.get('attention_only', 'false').lower() == 'true'
    
    if show_attention_only:
        projects_metrics = portfolio_selectors.get_projects_requiring_attention()
    else:
        projects_metrics = portfolio_selectors.get_all_projects_with_metrics()
        
        # Apply filters if provided
        if risk_level and risk_level in ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']:
            projects_metrics = projects_metrics.filter(metrics__risk_level=risk_level)
        if health and health in ['EXCELLENT', 'GOOD', 'WARNING', 'CRITICAL']:
            projects_metrics = projects_metrics.filter(metrics__project_health=health)
    
    context = {
        'projects_metrics': projects_metrics,
        'current_risk_filter': risk_level,
        'current_health_filter': health,
    }
    
    return render(request, 'dashboards/partials/portfolio_projects_table.html', context)


@login_required
@require_http_methods(["GET"])
def portfolio_risk_distribution_partial(request):
    """
    HTMX partial: Risk distribution chart data.
    
    URL: /portfolio/partials/risk-distribution/
    """
    from apps.portfolio import selectors as portfolio_selectors
    
    distribution = portfolio_selectors.get_portfolio_risk_distribution()
    
    context = {
        'distribution': distribution,
    }
    
    return render(request, 'dashboards/partials/portfolio_risk_distribution.html', context)


@login_required
@require_http_methods(["GET"])
def portfolio_high_risk_projects_partial(request):
    """
    HTMX partial: High and critical risk projects list.
    
    URL: /portfolio/partials/high-risk-projects/
    """
    from apps.portfolio import selectors as portfolio_selectors
    
    high_risk_projects = portfolio_selectors.get_high_risk_projects()
    
    context = {
        'high_risk_projects': high_risk_projects,
    }
    
    return render(request, 'dashboards/partials/portfolio_high_risk.html', context)
