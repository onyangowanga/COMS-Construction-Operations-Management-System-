"""
Notification Service
Handles alerts and notifications for various events
"""
from datetime import date, timedelta
from decimal import Decimal
from django.db.models import Sum, Q
from apps.suppliers.models import SupplierInvoice
from apps.approvals.models import ProjectApproval
from api.selectors.project_selectors import get_project_budget_variance


def check_budget_overruns(project_id=None):
    """
    Check for budget overruns across projects
    
    Args:
        project_id: Optional specific project to check
    
    Returns:
        list: Budget overrun alerts
    """
    from api.services.project_analytics import calculate_budget_variance
    from api.selectors.project_selectors import get_project_budget_variance
    
    alerts = []
    
    if project_id:
        bq_items = get_project_budget_variance(project_id)
        variance_data = calculate_budget_variance(bq_items)
        
        for item in variance_data:
            if item['status'] in ['OVER_BUDGET', 'SIGNIFICANTLY_OVER_BUDGET']:
                alerts.append({
                    'type': 'budget_overrun',
                    'severity': 'high' if item['status'] == 'SIGNIFICANTLY_OVER_BUDGET' else 'medium',
                    'project_id': project_id,
                    'bq_item': item['item_name'],
                    'message': f"{item['item_name']}: Over budget by {abs(item['variance']):.2f}",
                    'variance': item['variance'],
                    'variance_percentage': item['variance_percentage']
                })
    
    return alerts


def check_unpaid_supplier_invoices(days_overdue=30):
    """
    Check for unpaid supplier invoices
    
    Args:
        days_overdue: Number of days past due date to flag
    
    Returns:
        list: Unpaid invoice alerts
    """
    alerts = []
    today = date.today()
    
    unpaid_invoices = SupplierInvoice.objects.filter(
        status__in=['PENDING', 'PARTIAL']
    ).select_related('supplier', 'project')
    
    for invoice in unpaid_invoices:
        if invoice.due_date and invoice.due_date < today:
            days_past_due = (today - invoice.due_date).days
            
            if days_past_due >= days_overdue:
                # Calculate outstanding amount
                paid_amount = invoice.supplierpayment_set.aggregate(
                    total=Sum('amount_paid')
                )['total'] or Decimal('0')
                outstanding = invoice.amount - paid_amount
                
                alerts.append({
                    'type': 'unpaid_invoice',
                    'severity': 'high' if days_past_due > 60 else 'medium',
                    'invoice_id': str(invoice.id),
                    'invoice_number': invoice.invoice_number,
                    'supplier': invoice.supplier.name,
                    'project_id': str(invoice.project.id),
                    'amount': float(outstanding),
                    'due_date': invoice.due_date.isoformat(),
                    'days_past_due': days_past_due,
                    'message': f"Invoice {invoice.invoice_number} from {invoice.supplier.name} is {days_past_due} days overdue"
                })
    
    return alerts


def check_expiring_approvals(days_ahead=30):
    """
    Check for expiring project approvals
    
    Args:
        days_ahead: Number of days ahead to check for expiring approvals
    
    Returns:
        list: Expiring approval alerts
    """
    alerts = []
    today = date.today()
    future_date = today + timedelta(days=days_ahead)
    
    expiring_approvals = ProjectApproval.objects.filter(
        Q(expiry_date__lte=future_date) & Q(expiry_date__gte=today)
    ).select_related('project')
    
    for approval in expiring_approvals:
        days_until_expiry = (approval.expiry_date - today).days
        
        alerts.append({
            'type': 'expiring_approval',
            'severity': 'high' if days_until_expiry <= 7 else 'medium',
            'approval_id': str(approval.id),
            'approval_type': approval.approval_type,
            'project_id': str(approval.project.id),
            'project_code': approval.project.project_code,
            'expiry_date': approval.expiry_date.isoformat(),
            'days_until_expiry': days_until_expiry,
            'message': f"{approval.approval_type} approval for {approval.project.project_code} expires in {days_until_expiry} days"
        })
    
    return alerts


def get_all_notifications(project_id=None):
    """
    Get all notifications for a project or system-wide
    
    Args:
        project_id: Optional project ID to filter notifications
    
    Returns:
        dict: All notifications organized by type
    """
    budget_alerts = check_budget_overruns(project_id)
    invoice_alerts = check_unpaid_supplier_invoices()
    approval_alerts = check_expiring_approvals()
    
    # Filter by project if specified
    if project_id:
        invoice_alerts = [a for a in invoice_alerts if a.get('project_id') == str(project_id)]
        approval_alerts = [a for a in approval_alerts if a.get('project_id') == str(project_id)]
    
    return {
        'budget_overruns': budget_alerts,
        'unpaid_invoices': invoice_alerts,
        'expiring_approvals': approval_alerts,
        'total_count': len(budget_alerts) + len(invoice_alerts) + len(approval_alerts),
        'high_severity_count': sum(
            1 for alerts in [budget_alerts, invoice_alerts, approval_alerts]
            for alert in alerts
            if alert.get('severity') == 'high'
        )
    }
