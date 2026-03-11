"""
Project Selectors - Optimized database queries for project analytics
"""
from django.db.models import Q, Sum, Count, F, DecimalField, Case, When, Value
from django.db.models.functions import Coalesce
from apps.projects.models import Project, ProjectStage
from apps.ledger.models import Expense, ExpenseAllocation
from apps.clients.models import ClientPayment
from apps.bq.models import BQSection, BQElement, BQItem


def get_project_financial_data(project_id):
    """
    Get all financial data for a project with optimized queries
    """
    try:
        project = Project.objects.select_related('client').prefetch_related(
            'clientpayment_set',
            'expense_set',
            'expense_set__supplier_payment',
            'expense_set__consultant_payment',
            'expense_set__daily_labour_record',
        ).get(id=project_id)
        
        return project
    except Project.DoesNotExist:
        return None


def get_project_budget_variance(project_id):
    """
    Get budget variance data for all BQ items in a project
    """
    bq_items = BQItem.objects.filter(
        element__section__project_id=project_id
    ).select_related(
        'element__section'
    ).prefetch_related(
        'expense_allocations'
    ).annotate(
        budgeted_amount=F('total_amount'),
        actual_expenses=Coalesce(
            Sum('expense_allocations__allocated_amount'),
            Value(0),
            output_field=DecimalField()
        ),
        variance=F('total_amount') - F('actual_expenses')
    ).order_by('element__section__section_number', 'element__element_number', 'item_number')
    
    return bq_items


def get_project_health_data(project_id):
    """
    Get data needed to calculate project health indicator
    """
    try:
        project = Project.objects.select_related('client').prefetch_related(
            'projectstage_set',
            'expense_set',
            'clientpayment_set',
        ).get(id=project_id)
        
        return {
            'project': project,
            'stages': project.projectstage_set.all(),
            'expenses': project.expense_set.all(),
            'payments': project.clientpayment_set.all(),
        }
    except Project.DoesNotExist:
        return None
