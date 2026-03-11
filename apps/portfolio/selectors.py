"""
Portfolio Selectors - Query Layer
Optimized database queries for portfolio analytics
"""
from typing import List, Dict, Any, Optional
from decimal import Decimal
from django.db.models import QuerySet, Q, Prefetch, F
from django.utils import timezone

from apps.portfolio.models import ProjectMetrics
from apps.projects.models import Project


def get_portfolio_summary() -> Dict[str, Any]:
    """
    Get comprehensive portfolio summary with all metrics
    Uses service layer for computation
    
    Returns:
        Dictionary with portfolio-wide metrics
    """
    from apps.portfolio.services import PortfolioAnalyticsService
    return PortfolioAnalyticsService.compute_portfolio_summary()


def get_all_projects_with_metrics() -> QuerySet[Project]:
    """
    Get all active projects with their metrics
    
    Returns:
        QuerySet of projects with metrics preloaded
    """
    return Project.objects.exclude(
        status='CANCELLED'
    ).select_related(
        'organization'
    ).prefetch_related(
        Prefetch(
            'metrics',
            queryset=ProjectMetrics.objects.all()
        )
    ).order_by('-created_at')


def get_projects_by_risk_level(risk_level: str) -> QuerySet[ProjectMetrics]:
    """
    Get projects filtered by risk level
    
    Args:
        risk_level: One of LOW, MEDIUM, HIGH, CRITICAL
    
    Returns:
        QuerySet of ProjectMetrics filtered by risk level
    """
    return ProjectMetrics.objects.filter(
        risk_level=risk_level,
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('-last_updated')


def get_high_risk_projects() -> QuerySet[ProjectMetrics]:
    """
    Get high and critical risk projects
    
    Returns:
        QuerySet of high/critical risk projects
    """
    return ProjectMetrics.objects.filter(
        risk_level__in=['HIGH', 'CRITICAL'],
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('risk_level', '-budget_utilization')


def get_projects_over_budget() -> QuerySet[ProjectMetrics]:
    """
    Get projects that have exceeded their budget
    
    Returns:
        QuerySet of projects with expenses > contract value
    """
    return ProjectMetrics.objects.filter(
        is_over_budget=True,
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('-budget_utilization')


def get_projects_behind_schedule() -> QuerySet[ProjectMetrics]:
    """
    Get projects that are behind schedule
    
    Returns:
        QuerySet of delayed projects
    """
    return ProjectMetrics.objects.filter(
        is_behind_schedule=True,
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('schedule_performance_index')


def get_project_metrics(project_id: str) -> Optional[ProjectMetrics]:
    """
    Get metrics for a specific project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        ProjectMetrics instance or None
    """
    try:
        return ProjectMetrics.objects.select_related(
            'project',
            'project__organization'
        ).get(project_id=project_id)
    except ProjectMetrics.DoesNotExist:
        return None


def get_projects_by_health(health_status: str) -> QuerySet[ProjectMetrics]:
    """
    Get projects filtered by health status
    
    Args:
        health_status: One of EXCELLENT, GOOD, WARNING, CRITICAL
    
    Returns:
        QuerySet of projects with specified health status
    """
    return ProjectMetrics.objects.filter(
        project_health=health_status,
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('-last_updated')


def get_top_performing_projects(limit: int = 10) -> QuerySet[ProjectMetrics]:
    """
    Get top performing projects based on profit margin and CPI
    
    Args:
        limit: Maximum number of projects to return
    
    Returns:
        QuerySet of top performing projects
    """
    return ProjectMetrics.objects.filter(
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by(
        '-profit_margin',
        '-cost_performance_index'
    )[:limit]


def get_bottom_performing_projects(limit: int = 10) -> QuerySet[ProjectMetrics]:
    """
    Get bottom performing projects based on profit margin and CPI
    
    Args:
        limit: Maximum number of projects to return
    
    Returns:
        QuerySet of bottom performing projects
    """
    return ProjectMetrics.objects.filter(
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by(
        'profit_margin',
        'cost_performance_index'
    )[:limit]


def get_projects_requiring_attention() -> QuerySet[ProjectMetrics]:
    """
    Get projects requiring immediate attention
    Criteria: HIGH/CRITICAL risk OR over budget OR behind schedule
    
    Returns:
        QuerySet of projects needing attention
    """
    return ProjectMetrics.objects.filter(
        Q(risk_level__in=['HIGH', 'CRITICAL']) |
        Q(is_over_budget=True) |
        Q(is_behind_schedule=True)
    ).filter(
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    ).select_related(
        'project',
        'project__organization'
    ).order_by('risk_level', '-budget_utilization')


def get_portfolio_risk_distribution() -> Dict[str, int]:
    """
    Get distribution of projects by risk level
    
    Returns:
        Dictionary with counts per risk level
    """
    metrics = ProjectMetrics.objects.filter(
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    )
    
    return {
        'low': metrics.filter(risk_level='LOW').count(),
        'medium': metrics.filter(risk_level='MEDIUM').count(),
        'high': metrics.filter(risk_level='HIGH').count(),
        'critical': metrics.filter(risk_level='CRITICAL').count(),
    }


def get_portfolio_health_distribution() -> Dict[str, int]:
    """
    Get distribution of projects by health status
    
    Returns:
        Dictionary with counts per health status
    """
    metrics = ProjectMetrics.objects.filter(
        project__status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD']
    )
    
    return {
        'excellent': metrics.filter(project_health='EXCELLENT').count(),
        'good': metrics.filter(project_health='GOOD').count(),
        'warning': metrics.filter(project_health='WARNING').count(),
        'critical': metrics.filter(project_health='CRITICAL').count(),
    }


def get_evm_summary_for_project(project_id: str) -> Dict[str, Any]:
    """
    Get detailed EVM summary for a specific project
    
    Args:
        project_id: UUID of the project
    
    Returns:
        Dictionary with EVM metrics and variance analysis
    """
    metrics = get_project_metrics(project_id)
    
    if not metrics:
        return {
            'planned_value': Decimal('0.00'),
            'earned_value': Decimal('0.00'),
            'actual_cost': Decimal('0.00'),
            'cost_variance': Decimal('0.00'),
            'schedule_variance': Decimal('0.00'),
            'cost_performance_index': Decimal('1.00'),
            'schedule_performance_index': Decimal('1.00'),
            'estimate_at_completion': Decimal('0.00'),
            'variance_at_completion': Decimal('0.00'),
        }
    
    # Cost Variance (CV) = EV - AC
    cost_variance = metrics.earned_value - metrics.actual_cost
    
    # Schedule Variance (SV) = EV - PV
    schedule_variance = metrics.earned_value - metrics.planned_value
    
    # Estimate at Completion (EAC) = BAC / CPI
    # where BAC (Budget at Completion) = total contract value
    estimate_at_completion = Decimal('0.00')
    if metrics.cost_performance_index > 0:
        estimate_at_completion = (
            metrics.total_contract_value / metrics.cost_performance_index
        )
    
    # Variance at Completion (VAC) = BAC - EAC
    variance_at_completion = metrics.total_contract_value - estimate_at_completion
    
    return {
        'planned_value': metrics.planned_value,
        'earned_value': metrics.earned_value,
        'actual_cost': metrics.actual_cost,
        'cost_variance': cost_variance,
        'schedule_variance': schedule_variance,
        'cost_performance_index': metrics.cost_performance_index,
        'schedule_performance_index': metrics.schedule_performance_index,
        'estimate_at_completion': estimate_at_completion,
        'variance_at_completion': variance_at_completion,
        'budget_at_completion': metrics.total_contract_value,
    }
