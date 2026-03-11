"""
Budget Control Engine
Validates expenses against BQ item budgets
"""
from decimal import Decimal
from django.db.models import Sum
from apps.ledger.models import Expense
from apps.bq.models import BQItem


def check_budget_overrun(expense, bq_item_id=None):
    """
    Check if an expense will exceed the allocated BQ item budget
    
    Args:
        expense: Expense instance
        bq_item_id: Optional BQ item ID to check against
    
    Returns:
        dict: {
            'is_overrun': bool,
            'budget': Decimal,
            'allocated': Decimal,
            'new_total': Decimal,
            'variance': Decimal,
            'message': str
        }
    """
    if not bq_item_id:
        # If no BQ item specified, cannot check budget
        return {
            'is_overrun': False,
            'budget': Decimal('0'),
            'allocated': Decimal('0'),
            'new_total': expense.amount,
            'variance': Decimal('0'),
            'message': 'No BQ item specified for budget check'
        }
    
    try:
        bq_item = BQItem.objects.get(id=bq_item_id)
    except BQItem.DoesNotExist:
        return {
            'is_overrun': False,
            'budget': Decimal('0'),
            'allocated': Decimal('0'),
            'new_total': expense.amount,
            'variance': Decimal('0'),
            'message': 'BQ item not found'
        }
    
    # Get budget for this BQ item
    budget = bq_item.total_amount or Decimal('0')
    
    # Get currently allocated amount (excluding this expense if it already exists)
    allocated_query = bq_item.expense_allocations.all()
    if expense.id:
        # Exclude existing allocations for this expense
        allocated_query = allocated_query.exclude(expense_id=expense.id)
    
    allocated = allocated_query.aggregate(
        total=Sum('allocated_amount')
    )['total'] or Decimal('0')
    
    # Calculate new total if this expense is added
    new_total = allocated + expense.amount
    variance = budget - new_total
    
    is_overrun = new_total > budget
    
    message = ''
    if is_overrun:
        overrun_amount = new_total - budget
        overrun_percentage = (overrun_amount / budget * 100) if budget > 0 else 0
        message = f'Budget overrun: {overrun_amount:.2f} ({overrun_percentage:.1f}% over budget)'
    else:
        message = f'Within budget. Remaining: {variance:.2f}'
    
    return {
        'is_overrun': is_overrun,
        'budget': float(budget),
        'allocated': float(allocated),
        'new_total': float(new_total),
        'variance': float(variance),
        'message': message,
        'bq_item': {
            'id': str(bq_item.id),
            'item_name': bq_item.item_name,
            'item_number': f"{bq_item.element.section.section_number}.{bq_item.element.element_number}.{bq_item.item_number}"
        }
    }


def validate_expense_budget(expense, allocations):
    """
    Validate expense against multiple BQ item allocations
    
    Args:
        expense: Expense instance
        allocations: List of dicts [{'bq_item_id': uuid, 'amount': Decimal}]
    
    Returns:
        dict: {
            'requires_approval': bool,
            'overruns': list of overrun details,
            'total_budget': Decimal,
            'total_allocated': Decimal,
            'warnings': list of warning messages
        }
    """
    overruns = []
    warnings = []
    total_budget = Decimal('0')
    total_allocated = Decimal('0')
    
    for allocation in allocations:
        # Create temporary expense with allocated amount
        temp_expense = Expense(
            id=expense.id,
            project=expense.project,
            amount=allocation['amount'],
            expense_type=expense.expense_type,
            date=expense.date,
            description=expense.description
        )
        
        result = check_budget_overrun(temp_expense, allocation['bq_item_id'])
        
        total_budget += Decimal(str(result['budget']))
        total_allocated += Decimal(str(result['new_total']))
        
        if result['is_overrun']:
            overruns.append(result)
            warnings.append(result['message'])
    
    requires_approval = len(overruns) > 0
    
    return {
        'requires_approval': requires_approval,
        'overruns': overruns,
        'total_budget': float(total_budget),
        'total_allocated': float(total_allocated),
        'total_variance': float(total_budget - total_allocated),
        'warnings': warnings
    }
