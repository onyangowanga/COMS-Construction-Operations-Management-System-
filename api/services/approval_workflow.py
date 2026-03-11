"""
Approval Workflow Service
Handles approval processes for expenses, payments, and LPOs
"""
from django.utils import timezone
from apps.workflows.models import Approval, ProjectActivity
from .activity_service import log_activity


class ApprovalWorkflowError(Exception):
    """Custom exception for approval workflow errors"""
    pass


def create_approval_request(
    approval_type,
    amount,
    requested_by,
    reason='',
    expense_id=None,
    supplier_payment_id=None,
    consultant_payment_id=None,
    lpo_id=None
):
    """
    Create an approval request
    
    Args:
        approval_type: Type from Approval.ApprovalType
        amount: Amount requiring approval
        requested_by: User requesting approval
        reason: Reason for approval request
        expense_id: Optional expense UUID
        supplier_payment_id: Optional supplier payment UUID
        consultant_payment_id: Optional consultant payment UUID
        lpo_id: Optional LPO UUID
    
    Returns:
        Approval instance
    """
    approval = Approval.objects.create(
        approval_type=approval_type,
        amount=amount,
        requested_by=requested_by,
        reason=reason,
        expense_id=expense_id,
        supplier_payment_id=supplier_payment_id,
        consultant_payment_id=consultant_payment_id,
        lpo_id=lpo_id,
        status=Approval.Status.PENDING
    )
    
    return approval


def approve_request(approval, approved_by, notes=''):
    """
    Approve an approval request
    
    Args:
        approval: Approval instance
        approved_by: User approving
        notes: Optional approval notes
    
    Returns:
        dict: Approval result
    """
    if approval.status != Approval.Status.PENDING:
        raise ApprovalWorkflowError(
            f"Cannot approve. Current status: {approval.status}"
        )
    
    approval.status = Approval.Status.APPROVED
    approval.approved_by = approved_by
    approval.approved_at = timezone.now()
    approval.notes = notes
    approval.save()
    
    # Update related object if expense
    if approval.expense_id:
        from apps.ledger.models import Expense
        try:
            expense = Expense.objects.get(id=approval.expense_id)
            expense.approval_status = Expense.ApprovalStatus.APPROVED
            expense.save()
            
            # Log activity
            log_activity(
                project_id=expense.project.id,
                activity_type=ProjectActivity.ActivityType.APPROVAL_GRANTED,
                description=f"Expense approval granted: {expense.get_expense_type_display()} - {expense.amount}",
                amount=expense.amount,
                performed_by=approved_by,
                related_object_type='Expense',
                related_object_id=expense.id,
                metadata={
                    'approval_type': approval.approval_type,
                    'approver': approved_by.email if approved_by else 'System'
                }
            )
        except Expense.DoesNotExist:
            pass
    
    return {
        'status': 'success',
        'message': 'Approval granted successfully',
        'approval_id': str(approval.id),
        'approved_by': approved_by.email if approved_by else None,
        'approved_at': approval.approved_at.isoformat()
    }


def reject_request(approval, rejected_by, reason=''):
    """
    Reject an approval request
    
    Args:
        approval: Approval instance
        rejected_by: User rejecting
        reason: Reason for rejection
    
    Returns:
        dict: Rejection result
    """
    if approval.status != Approval.Status.PENDING:
        raise ApprovalWorkflowError(
            f"Cannot reject. Current status: {approval.status}"
        )
    
    approval.status = Approval.Status.REJECTED
    approval.approved_by = rejected_by
    approval.approved_at = timezone.now()
    approval.notes = reason
    approval.save()
    
    # Update related object if expense
    if approval.expense_id:
        from apps.ledger.models import Expense
        try:
            expense = Expense.objects.get(id=approval.expense_id)
            expense.approval_status = Expense.ApprovalStatus.REJECTED
            expense.save()
            
            # Log activity
            log_activity(
                project_id=expense.project.id,
                activity_type=ProjectActivity.ActivityType.APPROVAL_REJECTED,
                description=f"Expense approval rejected: {expense.get_expense_type_display()} - {expense.amount}",
                amount=expense.amount,
                performed_by=rejected_by,
                related_object_type='Expense',
                related_object_id=expense.id,
                metadata={
                    'approval_type': approval.approval_type,
                    'rejector': rejected_by.email if rejected_by else 'System',
                    'reason': reason
                }
            )
        except Expense.DoesNotExist:
            pass
    
    return {
        'status': 'success',
        'message': 'Approval rejected',
        'approval_id': str(approval.id),
        'rejected_by': rejected_by.email if rejected_by else None,
        'rejected_at': approval.approved_at.isoformat(),
        'reason': reason
    }


def get_pending_approvals(user=None, approval_type=None):
    """
    Get pending approvals
    
    Args:
        user: Optional user filter
        approval_type: Optional approval type filter
    
    Returns:
        QuerySet of Approval instances
    """
    approvals = Approval.objects.filter(status=Approval.Status.PENDING)
    
    if user:
        approvals = approvals.filter(requested_by=user)
    
    if approval_type:
        approvals = approvals.filter(approval_type=approval_type)
    
    return approvals.select_related('requested_by', 'approved_by').order_by('-requested_at')
