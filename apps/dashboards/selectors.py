"""
Dashboard data selectors for aggregating information from multiple sources.
"""
from decimal import Decimal
from typing import Dict, Any, List
from django.db.models import Sum, Count, Q, F, Case, When, DecimalField, Value
from django.utils import timezone
from datetime import timedelta

from apps.projects.models import Project
from apps.ledger.models import Expense, ClientPayment
from apps.suppliers.models import LocalPurchaseOrder, SupplierPayment
from apps.workers.models import Worker
from apps.workflows.models import Approval, ProjectActivity


def get_project_financial_summary(project_id: str) -> Dict[str, Any]:
    """
    Get comprehensive financial summary for a project.
    
    Returns:
        - total_revenue: Total client payments received
        - total_expenses: Total expenses incurred
        - profit: Revenue - Expenses
        - budget_allocated: Total BQ budget
        - budget_spent: Total expenses against BQ items
        - budget_remaining: Budget not yet spent
    """
    project = Project.objects.get(id=project_id)
    
    # Revenue
    total_revenue = ClientPayment.objects.filter(
        project_id=project_id
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Expenses
    total_expenses = Expense.objects.filter(
        project_id=project_id
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Budget from BQ
    budget_allocated = project.bq_items.aggregate(
        total=Sum('budget')
    )['total'] or Decimal('0.00')
    
    # Calculate profit
    profit = total_revenue - total_expenses
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': profit,
        'profit_margin': profit_margin,
        'budget_allocated': budget_allocated,
        'budget_spent': total_expenses,
        'budget_remaining': budget_allocated - total_expenses,
        'budget_utilization': (total_expenses / budget_allocated * 100) if budget_allocated > 0 else Decimal('0.00'),
    }


def get_project_budget_variance(project_id: str) -> List[Dict[str, Any]]:
    """
    Get budget variance for all BQ items in a project.
    
    Returns list of BQ items with variance information.
    """
    from apps.bq.models import BQItem
    from django.db.models import OuterRef, Subquery
    
    # Subquery to calculate spent amount per BQ item
    expense_sum = Expense.objects.filter(
        project_id=project_id,
        allocations__bq_item_id=OuterRef('id')
    ).values('allocations__bq_item_id').annotate(
        total=Sum('allocations__amount')
    ).values('total')
    
    bq_items = BQItem.objects.filter(
        project_id=project_id
    ).annotate(
        spent=Subquery(expense_sum, output_field=DecimalField(max_digits=15, decimal_places=2))
    ).values(
        'id', 'description', 'quantity', 'unit', 'rate', 'budget', 'spent'
    )
    
    variances = []
    for item in bq_items:
        spent = item['spent'] or Decimal('0.00')
        budget = item['budget'] or Decimal('0.00')
        variance = budget - spent
        variance_pct = (variance / budget * 100) if budget > 0 else Decimal('0.00')
        
        variances.append({
            'id': item['id'],
            'description': item['description'],
            'budget': budget,
            'spent': spent,
            'remaining': variance,
            'variance_percentage': variance_pct,
            'status': 'over' if variance < 0 else 'under' if variance > 0 else 'exact',
        })
    
    # Sort by variance (most over budget first)
    variances.sort(key=lambda x: x['variance_percentage'])
    
    return variances


def get_project_supplier_outstanding(project_id: str) -> List[Dict[str, Any]]:
    """
    Get outstanding supplier payments for a project.
    
    Returns list of LPOs that are invoiced but not fully paid.
    """
    lpos = LocalPurchaseOrder.objects.filter(
        project_id=project_id,
        status__in=['INVOICED']
    ).select_related('supplier').annotate(
        paid_amount=Sum('supplier_payments__amount')
    ).values(
        'id', 'lpo_number', 'supplier__name', 'total_amount', 
        'paid_amount', 'created_at', 'invoice_number'
    )
    
    outstanding = []
    for lpo in lpos:
        paid = lpo['paid_amount'] or Decimal('0.00')
        total = lpo['total_amount']
        balance = total - paid
        
        # Calculate days since invoice
        days_outstanding = (timezone.now().date() - lpo['created_at'].date()).days
        
        outstanding.append({
            'lpo_number': lpo['lpo_number'],
            'supplier_name': lpo['supplier__name'],
            'total_amount': total,
            'paid_amount': paid,
            'balance': balance,
            'invoice_number': lpo['invoice_number'],
            'days_outstanding': days_outstanding,
            'status': 'overdue' if days_outstanding > 30 else 'due' if days_outstanding > 14 else 'recent',
        })
    
    # Sort by days outstanding (most urgent first)
    outstanding.sort(key=lambda x: x['days_outstanding'], reverse=True)
    
    return outstanding


def get_project_unpaid_wages(project_id: str) -> List[Dict[str, Any]]:
    """
    Get unpaid wages for workers on a project.
    
    Note: This is a placeholder - actual implementation would depend on
    how worker payments are tracked in your system.
    """
    # Placeholder: Return empty list if worker payment tracking not yet implemented
    # TODO: Implement once worker payment model is available
    return []


def get_pending_lpo_approvals() -> List[Dict[str, Any]]:
    """
    Get all LPOs pending approval across all projects.
    """
    lpos = LocalPurchaseOrder.objects.filter(
        status='DRAFT'
    ).select_related('project', 'supplier').values(
        'id', 'lpo_number', 'project__project_code', 'project__name',
        'supplier__name', 'total_amount', 'created_at'
    ).order_by('-created_at')
    
    return [
        {
            'id': lpo['id'],
            'lpo_number': lpo['lpo_number'],
            'project_code': lpo['project__project_code'],
            'project_name': lpo['project__name'],
            'supplier_name': lpo['supplier__name'],
            'amount': lpo['total_amount'],
            'created_at': lpo['created_at'],
            'days_pending': (timezone.now().date() - lpo['created_at'].date()).days,
        }
        for lpo in lpos
    ]


def get_delivered_not_invoiced_lpos() -> List[Dict[str, Any]]:
    """
    Get LPOs that have been delivered but not yet invoiced.
    """
    lpos = LocalPurchaseOrder.objects.filter(
        status='DELIVERED'
    ).select_related('project', 'supplier').values(
        'id', 'lpo_number', 'project__project_code', 'project__name',
        'supplier__name', 'total_amount', 'delivery_date'
    ).order_by('delivery_date')
    
    return [
        {
            'id': lpo['id'],
            'lpo_number': lpo['lpo_number'],
            'project_code': lpo['project__project_code'],
            'project_name': lpo['project__name'],
            'supplier_name': lpo['supplier__name'],
            'amount': lpo['total_amount'],
            'delivery_date': lpo['delivery_date'],
            'days_since_delivery': (timezone.now().date() - lpo['delivery_date']).days if lpo['delivery_date'] else 0,
        }
        for lpo in lpos
    ]


def get_invoiced_not_paid_lpos() -> List[Dict[str, Any]]:
    """
    Get LPOs that have been invoiced but not fully paid.
    """
    lpos = LocalPurchaseOrder.objects.filter(
        status='INVOICED'
    ).select_related('project', 'supplier').annotate(
        paid_amount=Sum('supplier_payments__amount')
    ).values(
        'id', 'lpo_number', 'project__project_code', 'project__name',
        'supplier__name', 'total_amount', 'paid_amount', 'invoice_date', 'invoice_number'
    ).order_by('invoice_date')
    
    return [
        {
            'id': lpo['id'],
            'lpo_number': lpo['lpo_number'],
            'invoice_number': lpo['invoice_number'],
            'project_code': lpo['project__project_code'],
            'project_name': lpo['project__name'],
            'supplier_name': lpo['supplier__name'],
            'total_amount': lpo['total_amount'],
            'paid_amount': lpo['paid_amount'] or Decimal('0.00'),
            'balance': lpo['total_amount'] - (lpo['paid_amount'] or Decimal('0.00')),
            'invoice_date': lpo['invoice_date'],
            'days_overdue': (timezone.now().date() - lpo['invoice_date']).days if lpo['invoice_date'] else 0,
        }
        for lpo in lpos
    ]


def get_finance_summary() -> Dict[str, Any]:
    """
    Get organization-wide financial summary across all projects.
    """
    # Total revenue from all projects
    total_revenue = ClientPayment.objects.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Total expenses from all projects
    total_expenses = Expense.objects.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0.00')
    
    # Total supplier liabilities (invoiced but not paid)
    supplier_liabilities = LocalPurchaseOrder.objects.filter(
        status='INVOICED'
    ).annotate(
        paid=Sum('supplier_payments__amount')
    ).aggregate(
        total=Sum(F('total_amount') - F('paid'))
    )['total'] or Decimal('0.00')
    
    # Active projects count
    active_projects = Project.objects.filter(
        status__in=['ACTIVE', 'IN_PROGRESS']
    ).count()
    
    # Profit calculation
    profit = total_revenue - total_expenses
    profit_margin = (profit / total_revenue * 100) if total_revenue > 0 else Decimal('0.00')
    
    return {
        'total_revenue': total_revenue,
        'total_expenses': total_expenses,
        'profit': profit,
        'profit_margin': profit_margin,
        'supplier_liabilities': supplier_liabilities,
        'active_projects': active_projects,
        'average_project_profit': profit / active_projects if active_projects > 0 else Decimal('0.00'),
    }


def get_recent_project_activity(project_id: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get recent activity for a project.
    
    Returns list of recent ProjectActivity records.
    """
    activities = ProjectActivity.objects.filter(
        project_id=project_id
    ).select_related('performed_by').values(
        'id', 'activity_type', 'description', 'amount',
        'performed_by__first_name', 'performed_by__last_name',
        'performed_by__email', 'created_at'
    ).order_by('-created_at')[:limit]
    
    return [
        {
            'activity_type': activity['activity_type'],
            'description': activity['description'],
            'amount': activity['amount'],
            'performed_by': f"{activity['performed_by__first_name']} {activity['performed_by__last_name']}" if activity['performed_by__first_name'] else activity['performed_by__email'],
            'created_at': activity['created_at'],
        }
        for activity in activities
    ]
