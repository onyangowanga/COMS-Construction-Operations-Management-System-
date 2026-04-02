"""
Variation Order Selectors

Optimized database queries for variation order data retrieval.
"""

from typing import Optional, List, Dict, Any
from decimal import Decimal
from datetime import datetime
from django.db.models import QuerySet, Sum, Count, Q, Avg, Max, Min
from django.utils import timezone

from apps.variations.models import VariationOrder
from apps.projects.models import Project


def get_variation_by_id(variation_id: str) -> VariationOrder:
    """
    Get variation order by ID.
    
    Args:
        variation_id: Variation UUID
    
    Returns:
        VariationOrder instance
    """
    return VariationOrder.objects.select_related(
        'project',
        'project__organization',
        'created_by',
        'submitted_by',
        'approved_by'
    ).get(id=variation_id)


def get_variation_by_reference(reference_number: str) -> VariationOrder:
    """
    Get variation order by reference number.
    
    Args:
        reference_number: Variation reference (e.g., VO-PRJ001-2026-001)
    
    Returns:
        VariationOrder instance
    """
    return VariationOrder.objects.select_related(
        'project',
        'project__organization',
        'created_by',
        'submitted_by',
        'approved_by'
    ).get(reference_number=reference_number)


def get_project_variations(
    project_id: str,
    status: Optional[str] = None,
    priority: Optional[str] = None
) -> QuerySet[VariationOrder]:
    """
    Get all variation orders for a project.
    
    Args:
        project_id: Project UUID
        status: Filter by status (optional)
        priority: Filter by priority (optional)
    
    Returns:
        QuerySet of VariationOrder instances
    """
    variations = VariationOrder.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'created_by',
        'submitted_by',
        'approved_by'
    )
    
    if status:
        variations = variations.filter(status=status)
    
    if priority:
        variations = variations.filter(priority=priority)
    
    return variations.order_by('-instruction_date', '-created_at')


def get_pending_variations(project_id: Optional[str] = None) -> QuerySet[VariationOrder]:
    """
    Get pending variations (submitted for approval).
    
    Args:
        project_id: Project UUID (optional, filters to specific project)
    
    Returns:
        QuerySet of pending variations
    """
    variations = VariationOrder.objects.filter(
        status=VariationOrder.Status.SUBMITTED
    ).select_related(
        'project',
        'project__organization',
        'submitted_by'
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    return variations.order_by('instruction_date')


def get_approved_variations(project_id: Optional[str] = None) -> QuerySet[VariationOrder]:
    """
    Get approved variations.
    
    Args:
        project_id: Project UUID (optional)
    
    Returns:
        QuerySet of approved variations
    """
    variations = VariationOrder.objects.filter(
        status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED,
            VariationOrder.Status.PAID
        ]
    ).select_related(
        'project',
        'project__organization',
        'approved_by'
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    return variations.order_by('-approved_date')


def get_outstanding_variations(project_id: Optional[str] = None) -> QuerySet[VariationOrder]:
    """
    Get variations that are approved but not fully paid.
    
    Args:
        project_id: Project UUID (optional)
    
    Returns:
        QuerySet of variations with outstanding amounts
    """
    variations = VariationOrder.objects.filter(
        status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED
        ]
    ).select_related(
        'project',
        'project__organization'
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    return variations.order_by('-approved_date')


def get_project_variation_summary(project_id: str) -> Dict[str, Any]:
    """
    Get comprehensive variation summary for a project.
    
    Args:
        project_id: Project UUID
    
    Returns:
        Dictionary with variation metrics
    """
    project = Project.objects.get(id=project_id)
    variations = VariationOrder.objects.filter(project_id=project_id)
    
    # Basic counts
    total_count = variations.count()
    
    # Status breakdown
    status_counts = variations.values('status').annotate(
        count=Count('id')
    )
    
    status_breakdown = {
        'draft': 0,
        'submitted': 0,
        'approved': 0,
        'rejected': 0,
        'invoiced': 0,
        'paid': 0,
    }
    
    for item in status_counts:
        status_breakdown[item['status'].lower()] = item['count']
    
    # Financial aggregates
    financial_summary = variations.aggregate(
        total_estimated=Sum('estimated_value'),
        total_approved=Sum('approved_value', filter=Q(status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED,
            VariationOrder.Status.PAID
        ])),
        total_invoiced=Sum('invoiced_value'),
        total_paid=Sum('paid_value'),
        avg_estimated=Avg('estimated_value'),
        max_estimated=Max('estimated_value'),
    )
    
    total_approved = financial_summary['total_approved'] or Decimal('0.00')
    total_paid = financial_summary['total_paid'] or Decimal('0.00')
    
    # Calculate impact on contract
    contract_impact_percentage = Decimal('0.00')
    if project.contract_sum and project.contract_sum > 0:
        contract_impact_percentage = (total_approved / project.contract_sum) * 100
    
    return {
        'project': project,
        'total_variations': total_count,
        'status_breakdown': status_breakdown,
        'total_estimated_value': financial_summary['total_estimated'] or Decimal('0.00'),
        'total_approved_value': total_approved,
        'total_invoiced_value': financial_summary['total_invoiced'] or Decimal('0.00'),
        'total_paid_value': total_paid,
        'outstanding_value': total_approved - total_paid,
        'average_variation_value': financial_summary['avg_estimated'] or Decimal('0.00'),
        'largest_variation_value': financial_summary['max_estimated'] or Decimal('0.00'),
        'contract_impact_percentage': contract_impact_percentage,
        'original_contract_sum': project.contract_sum or Decimal('0.00'),
        'revised_contract_sum': (project.contract_sum or Decimal('0.00')),
    }


def get_variation_trend_data(
    project_id: Optional[str] = None,
    months: int = 6
) -> List[Dict[str, Any]]:
    """
    Get variation trend data for charting.
    
    Args:
        project_id: Project UUID (optional, for project-specific trends)
        months: Number of months to analyze
    
    Returns:
        List of dictionaries with monthly variation data
    """
    from dateutil.relativedelta import relativedelta
    
    start_date = timezone.now().date() - relativedelta(months=months)
    
    variations = VariationOrder.objects.filter(
        instruction_date__gte=start_date
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    # Group by month
    monthly_data = []
    current_date = start_date.replace(day=1)
    end_date = timezone.now().date().replace(day=1)
    
    while current_date <= end_date:
        next_month = current_date + relativedelta(months=1)
        
        month_variations = variations.filter(
            instruction_date__gte=current_date,
            instruction_date__lt=next_month
        )
        
        month_summary = month_variations.aggregate(
            count=Count('id'),
            total_estimated=Sum('estimated_value'),
            total_approved=Sum('approved_value'),
            approved_count=Count('id', filter=Q(status=VariationOrder.Status.APPROVED)),
        )
        
        monthly_data.append({
            'month': current_date.strftime('%Y-%m'),
            'month_label': current_date.strftime('%b %Y'),
            'variation_count': month_summary['count'] or 0,
            'total_estimated': month_summary['total_estimated'] or Decimal('0.00'),
            'total_approved': month_summary['total_approved'] or Decimal('0.00'),
            'approved_count': month_summary['approved_count'] or 0,
        })
        
        current_date = next_month
    
    return monthly_data


def get_high_value_variations(
    threshold: Decimal = Decimal('500000.00'),
    project_id: Optional[str] = None
) -> QuerySet[VariationOrder]:
    """
    Get high-value variation orders above threshold.
    
    Args:
        threshold: Minimum value threshold
        project_id: Project UUID (optional)
    
    Returns:
        QuerySet of high-value variations
    """
    variations = VariationOrder.objects.filter(
        estimated_value__gte=threshold
    ).select_related(
        'project',
        'project__organization',
        'created_by'
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    return variations.order_by('-estimated_value')


def get_urgent_variations(project_id: Optional[str] = None) -> QuerySet[VariationOrder]:
    """
    Get urgent variations requiring attention.
    
    Args:
        project_id: Project UUID (optional)
    
    Returns:
        QuerySet of urgent variations
    """
    variations = VariationOrder.objects.filter(
        priority=VariationOrder.Priority.URGENT,
        status__in=[
            VariationOrder.Status.DRAFT,
            VariationOrder.Status.SUBMITTED
        ]
    ).select_related(
        'project',
        'project__organization',
        'created_by'
    )
    
    if project_id:
        variations = variations.filter(project_id=project_id)
    
    return variations.order_by('instruction_date')


def get_portfolio_variation_summary() -> Dict[str, Any]:
    """
    Get portfolio-wide variation summary across all projects.
    
    Returns:
        Dictionary with portfolio-level metrics
    """
    all_variations = VariationOrder.objects.all()
    
    summary = all_variations.aggregate(
        total_count=Count('id'),
        pending_count=Count('id', filter=Q(status=VariationOrder.Status.SUBMITTED)),
        approved_count=Count('id', filter=Q(status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED,
            VariationOrder.Status.PAID
        ])),
        rejected_count=Count('id', filter=Q(status=VariationOrder.Status.REJECTED)),
        urgent_count=Count('id', filter=Q(
            priority=VariationOrder.Priority.URGENT,
            status__in=[VariationOrder.Status.DRAFT, VariationOrder.Status.SUBMITTED]
        )),
        total_estimated=Sum('estimated_value'),
        total_approved=Sum('approved_value', filter=Q(status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED,
            VariationOrder.Status.PAID
        ])),
        total_outstanding=Sum('approved_value', filter=Q(status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED
        ])) - Sum('paid_value', filter=Q(status__in=[
            VariationOrder.Status.APPROVED,
            VariationOrder.Status.INVOICED,
            VariationOrder.Status.PAID
        ])),
    )
    
    # Get project count with variations
    projects_with_variations = VariationOrder.objects.values(
        'project'
    ).distinct().count()
    
    return {
        'total_variations': summary['total_count'] or 0,
        'pending_approval': summary['pending_count'] or 0,
        'approved': summary['approved_count'] or 0,
        'rejected': summary['rejected_count'] or 0,
        'urgent': summary['urgent_count'] or 0,
        'total_estimated_value': summary['total_estimated'] or Decimal('0.00'),
        'total_approved_value': summary['total_approved'] or Decimal('0.00'),
        'total_outstanding_value': summary['total_outstanding'] or Decimal('0.00'),
        'projects_affected': projects_with_variations,
    }
