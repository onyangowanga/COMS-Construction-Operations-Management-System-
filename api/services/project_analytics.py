"""
Project Analytics Services - Business logic for project analytics
"""
from decimal import Decimal
from django.db.models import Sum, Q
from datetime import date


def calculate_project_financial_summary(project):
    """
    Calculate comprehensive financial summary for a project
    
    Returns:
        dict: Financial summary with contract value, payments, expenses, profit, etc.
    """
    if not project:
        return None
    
    # Contract value
    contract_value = project.contract_value or Decimal('0')
    
    # Total client payments
    total_client_payments = project.clientpayment_set.aggregate(
        total=Sum('amount_paid')
    )['total'] or Decimal('0')
    
    # Total expenses
    total_expenses = project.expense_set.aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Supplier payments
    supplier_payments = project.expense_set.filter(
        expense_type='SUPPLIER'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Consultant payments
    consultant_payments = project.expense_set.filter(
        expense_type='CONSULTANT'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Labour cost
    labour_cost = project.expense_set.filter(
        expense_type='LABOUR'
    ).aggregate(
        total=Sum('amount')
    )['total'] or Decimal('0')
    
    # Remaining budget
    remaining_budget = contract_value - total_expenses
    
    # Profit (payments received - expenses)
    profit = total_client_payments - total_expenses
    
    # Profit margin
    profit_margin = (profit / contract_value * 100) if contract_value > 0 else Decimal('0')
    
    # Outstanding amount from client
    outstanding_from_client = contract_value - total_client_payments
    
    return {
        'project_id': str(project.id),
        'project_code': project.project_code,
        'project_name': project.project_name,
        'contract_value': float(contract_value),
        'total_client_payments': float(total_client_payments),
        'outstanding_from_client': float(outstanding_from_client),
        'total_expenses': float(total_expenses),
        'supplier_payments': float(supplier_payments),
        'consultant_payments': float(consultant_payments),
        'labour_cost': float(labour_cost),
        'remaining_budget': float(remaining_budget),
        'profit': float(profit),
        'profit_margin': float(profit_margin),
    }


def calculate_budget_variance(bq_items):
    """
    Calculate budget variance for BQ items
    
    Returns:
        list: BQ items with variance analysis
    """
    variance_data = []
    
    for item in bq_items:
        budgeted = item.budgeted_amount or Decimal('0')
        actual = item.actual_expenses or Decimal('0')
        variance = budgeted - actual
        
        # Determine status
        if variance >= 0:
            if variance > budgeted * Decimal('0.1'):  # More than 10% under budget
                status = 'SIGNIFICANTLY_UNDER_BUDGET'
            else:
                status = 'UNDER_BUDGET'
        else:
            if abs(variance) > budgeted * Decimal('0.1'):  # More than 10% over budget
                status = 'SIGNIFICANTLY_OVER_BUDGET'
            else:
                status = 'OVER_BUDGET'
        
        variance_percentage = (variance / budgeted * 100) if budgeted > 0 else Decimal('0')
        
        variance_data.append({
            'bq_item_id': str(item.id),
            'section': item.element.section.section_name,
            'element': item.element.element_name,
            'item_name': item.item_name,
            'item_number': f"{item.element.section.section_number}.{item.element.element_number}.{item.item_number}",
            'budgeted_amount': float(budgeted),
            'actual_expenses': float(actual),
            'variance': float(variance),
            'variance_percentage': float(variance_percentage),
            'status': status,
        })
    
    return variance_data


def calculate_project_health(health_data):
    """
    Calculate project health indicator based on multiple factors
    
    Returns:
        dict: Health status (GREEN, YELLOW, RED) with reasons
    """
    if not health_data:
        return None
    
    project = health_data['project']
    stages = health_data.get('stages', [])
    expenses = health_data.get('expenses', [])
    payments = health_data.get('payments', [])
    
    red_flags = []
    yellow_flags = []
    
    # Check budget health
    contract_value = project.contract_value or Decimal('0')
    total_expenses = sum(exp.amount for exp in expenses) if expenses else Decimal('0')
    budget_utilization = (total_expenses / contract_value * 100) if contract_value > 0 else Decimal('0')
    
    if budget_utilization > 100:
        red_flags.append('Budget exceeded')
    elif budget_utilization > 90:
        yellow_flags.append('Budget utilization above 90%')
    
    # Check payment collection
    total_payments = sum(pay.amount_paid for pay in payments) if payments else Decimal('0')
    payment_percentage = (total_payments / contract_value * 100) if contract_value > 0 else Decimal('0')
    
    if total_expenses > total_payments:
        deficit = total_expenses - total_payments
        if deficit > contract_value * Decimal('0.3'):  # Deficit more than 30% of contract
            red_flags.append(f'High deficit: {float(deficit):.2f}')
        elif deficit > contract_value * Decimal('0.15'):  # Deficit more than 15%
            yellow_flags.append(f'Moderate deficit: {float(deficit):.2f}')
    
    # Check milestone completion
    total_stages = len(stages) if stages else 0
    completed_stages = sum(1 for stage in stages if stage.is_completed) if stages else 0
    
    if total_stages > 0:
        completion_rate = (completed_stages / total_stages * 100)
        if completion_rate < 50 and budget_utilization > 60:
            yellow_flags.append('Low completion rate vs budget utilization')
    
    # Check for delayed milestones (stages past target date but not completed)
    today = date.today()
    delayed_stages = [
        stage for stage in stages 
        if not stage.is_completed and stage.target_end_date and stage.target_end_date < today
    ]
    
    if len(delayed_stages) > 3:
        red_flags.append(f'{len(delayed_stages)} delayed milestones')
    elif len(delayed_stages) > 0:
        yellow_flags.append(f'{len(delayed_stages)} delayed milestone(s)')
    
    # Determine overall health
    if red_flags:
        health_status = 'RED'
    elif yellow_flags:
        health_status = 'YELLOW'
    else:
        health_status = 'GREEN'
    
    return {
        'project_id': str(project.id),
        'project_code': project.project_code,
        'project_name': project.project_name,
        'health_status': health_status,
        'budget_utilization_percentage': float(budget_utilization),
        'payment_collection_percentage': float(payment_percentage),
        'completion_rate': float(completion_rate) if total_stages > 0 else 0,
        'delayed_milestones': len(delayed_stages),
        'red_flags': red_flags,
        'yellow_flags': yellow_flags,
        'summary': {
            'total_stages': total_stages,
            'completed_stages': completed_stages,
            'contract_value': float(contract_value),
            'total_expenses': float(total_expenses),
            'total_payments': float(total_payments),
        }
    }
