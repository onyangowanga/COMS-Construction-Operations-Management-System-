"""
Valuation Selectors
Query layer for valuation data - keeps views thin
"""
from decimal import Decimal
from typing import Dict, Any, List, Optional
from django.db.models import Sum, Count, Max, Q, F, Prefetch
from django.utils import timezone

from .models import Valuation, BQItemProgress
from apps.projects.models import Project
from apps.bq.models import BQItem, BQElement, BQSection


def get_project_valuations(project_id: str) -> List[Valuation]:
    """
    Get all valuations for a project with related data
    
    Args:
        project_id: Project UUID
        
    Returns:
        List of Valuation objects with prefetched relations
    """
    return Valuation.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'submitted_by',
        'approved_by'
    ).prefetch_related(
        'item_progress__bq_item'
    ).order_by('-valuation_date', '-valuation_number')


def get_valuation_by_id(valuation_id: str) -> Optional[Valuation]:
    """
    Get a single valuation with all related data
    
    Args:
        valuation_id: Valuation UUID
        
    Returns:
        Valuation object or None
    """
    try:
        return Valuation.objects.select_related(
            'project',
            'submitted_by',
            'approved_by'
        ).prefetch_related(
            Prefetch(
                'item_progress',
                queryset=BQItemProgress.objects.select_related(
                    'bq_item__element__section'
                ).order_by(
                    'bq_item__element__section__order',
                    'bq_item__element__order'
                )
            )
        ).get(id=valuation_id)
    except Valuation.DoesNotExist:
        return None


def get_latest_valuation(project_id: str) -> Optional[Valuation]:
    """
    Get the most recent valuation for a project
    
    Args:
        project_id: Project UUID
        
    Returns:
        Latest Valuation object or None
    """
    return Valuation.objects.filter(
        project_id=project_id
    ).select_related(
        'project',
        'submitted_by',
        'approved_by'
    ).order_by('-valuation_date', '-valuation_number').first()


def get_valuation_summary(project_id: str) -> Dict[str, Any]:
    """
    Get summary statistics for project valuations
    
    Args:
        project_id: Project UUID
        
    Returns:
        Dictionary with:
        - total_valuations: Count of all valuations
        - total_certified: Sum of all approved valuations
        - total_paid: Sum of paid valuations
        - pending_payment: Sum of approved but unpaid
        - latest_valuation: Latest valuation object
        - retention_held: Total retention amount
    """
    valuations = Valuation.objects.filter(project_id=project_id)
    
    # Aggregate data
    approved_vals = valuations.filter(status__in=['APPROVED', 'PAID'])
    paid_vals = valuations.filter(status='PAID')
    
    total_certified = approved_vals.aggregate(
        total=Sum('work_completed_value')
    )['total'] or Decimal('0.00')
    
    total_paid = paid_vals.aggregate(
        total=Sum('amount_due')
    )['total'] or Decimal('0.00')
    
    retention_held = approved_vals.aggregate(
        total=Sum('retention_amount')
    )['total'] or Decimal('0.00')
    
    pending_payment = approved_vals.filter(
        status='APPROVED'
    ).aggregate(
        total=Sum('amount_due')
    )['total'] or Decimal('0.00')
    
    latest = get_latest_valuation(project_id)
    
    return {
        'total_valuations': valuations.count(),
        'total_certified': total_certified,
        'total_paid': total_paid,
        'pending_payment': pending_payment,
        'latest_valuation': latest,
        'retention_held': retention_held,
        'latest_valuation_number': latest.valuation_number if latest else None,
        'latest_valuation_date': latest.valuation_date if latest else None,
        'latest_amount_due': latest.amount_due if latest else Decimal('0.00')
    }


def get_bq_progress_summary(project_id: str) -> Dict[str, Any]:
    """
    Get overall BQ progress for a project based on latest valuations
    
    Args:
        project_id: Project UUID
        
    Returns:
        Dictionary with overall progress statistics
    """
    from django.db.models import OuterRef, Subquery
    
    # Get latest cumulative value for each BQ item
    latest_progress = BQItemProgress.objects.filter(
        bq_item=OuterRef('pk')
    ).order_by('-valuation__valuation_date').values('cumulative_value')[:1]
    
    bq_items = BQItem.objects.filter(
        element__section__project_id=project_id
    ).annotate(
        completed_value=Subquery(latest_progress)
    )
    
    # Calculate totals
    total_budget = bq_items.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    total_completed = bq_items.aggregate(
        total=Sum('completed_value')
    )['total'] or Decimal('0.00')
    
    percentage = (total_completed / total_budget * 100) if total_budget > 0 else Decimal('0.00')
    
    return {
        'total_budget': total_budget,
        'total_completed': total_completed,
        'remaining': total_budget - total_completed,
        'percentage_complete': round(percentage, 2)
    }


def get_next_valuation_number(project_id: str) -> str:
    """
    Generate next valuation number for a project
    
    Args:
        project_id: Project UUID
        
    Returns:
        Next valuation number (e.g., "IPC-001", "IPC-002")
    """
    latest = Valuation.objects.filter(
        project_id=project_id
    ).order_by('-valuation_number').first()
    
    if not latest:
        return "IPC-001"
    
    # Extract number from last valuation
    try:
        last_num = int(latest.valuation_number.split('-')[-1])
        next_num = last_num + 1
        return f"IPC-{next_num:03d}"
    except (ValueError, IndexError):
        # Fallback if number format is unexpected
        count = Valuation.objects.filter(project_id=project_id).count()
        return f"IPC-{count + 1:03d}"


def get_previous_bq_progress(project_id: str, current_valuation_id: Optional[str] = None) -> Dict[str, Decimal]:
    """
    Get the previous cumulative progress for all BQ items
    Used when creating a new valuation
    
    Args:
        project_id: Project UUID
        current_valuation_id: Exclude this valuation ID (for edits)
        
    Returns:
        Dictionary mapping BQ item IDs to their previous cumulative quantities
    """
    from django.db.models import OuterRef, Subquery
    
    # Get BQ items for this project
    bq_items = BQItem.objects.filter(
        element__section__project_id=project_id
    )
    
    progress_dict = {}
    
    for bq_item in bq_items:
        # Get latest progress for this item (excluding current valuation)
        query = BQItemProgress.objects.filter(
            bq_item=bq_item
        ).order_by('-valuation__valuation_date')
        
        if current_valuation_id:
            query = query.exclude(valuation_id=current_valuation_id)
        
        latest_progress = query.first()
        
        if latest_progress:
            progress_dict[str(bq_item.id)] = latest_progress.cumulative_quantity
        else:
            progress_dict[str(bq_item.id)] = Decimal('0.00')
    
    return progress_dict


def get_valuation_items_grouped(valuation_id: str) -> List[Dict[str, Any]]:
    """
    Get valuation items grouped by BQ section and element
    For display in reports
    
    Args:
        valuation_id: Valuation UUID
        
    Returns:
        List of sections with nested elements and items
    """
    valuation = get_valuation_by_id(valuation_id)
    if not valuation:
        return []
    
    # Get all progress items for this valuation
    progress_items = BQItemProgress.objects.filter(
        valuation_id=valuation_id
    ).select_related(
        'bq_item__element__section'
    ).order_by(
        'bq_item__element__section__order',
        'bq_item__element__order'
    )
    
    # Group by section
    sections_dict = {}
    
    for progress in progress_items:
        section = progress.bq_item.element.section
        element = progress.bq_item.element
        
        # Initialize section if not exists
        if section.id not in sections_dict:
            sections_dict[section.id] = {
                'section': section,
                'elements': {}
            }
        
        # Initialize element if not exists
        if element.id not in sections_dict[section.id]['elements']:
            sections_dict[section.id]['elements'][element.id] = {
                'element': element,
                'items': []
            }
        
        # Add item progress
        sections_dict[section.id]['elements'][element.id]['items'].append({
            'progress': progress,
            'bq_item': progress.bq_item
        })
    
    # Convert to list format
    result = []
    for section_data in sections_dict.values():
        elements_list = []
        for element_data in section_data['elements'].values():
            elements_list.append(element_data)
        
        result.append({
            'section': section_data['section'],
            'elements': elements_list
        })
    
    return result
