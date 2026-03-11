"""
Procurement Workflow Service
Handles LPO lifecycle state transitions
"""
from django.utils import timezone
from apps.suppliers.models import LocalPurchaseOrder
from apps.workflows.models import ProjectActivity
from .activity_service import log_activity


class ProcurementWorkflowError(Exception):
    """Custom exception for procurement workflow errors"""
    pass


def approve_lpo(lpo, approved_by):
    """
    Approve a draft LPO
    
    Args:
        lpo: LocalPurchaseOrder instance
        approved_by: User who approved
    
    Returns:
        dict: Updated LPO status
    """
    if lpo.status != LocalPurchaseOrder.Status.DRAFT:
        raise ProcurementWorkflowError(
            f"Cannot approve LPO with status {lpo.status}. Must be DRAFT."
        )
    
    lpo.status = LocalPurchaseOrder.Status.APPROVED
    lpo.save()
    
    # Log activity
    log_activity(
        project_id=lpo.project.id,
        activity_type=ProjectActivity.ActivityType.LPO_APPROVED,
        description=f"LPO {lpo.lpo_number} approved for {lpo.supplier.name}",
        amount=lpo.total_amount,
        performed_by=approved_by,
        related_object_type='LocalPurchaseOrder',
        related_object_id=lpo.id,
        metadata={
            'lpo_number': lpo.lpo_number,
            'supplier': lpo.supplier.name,
            'previous_status': 'DRAFT'
        }
    )
    
    return {
        'status': 'success',
        'message': f'LPO {lpo.lpo_number} approved successfully',
        'new_status': lpo.status,
        'lpo_id': str(lpo.id)
    }


def mark_lpo_delivered(lpo, delivered_by):
    """
    Mark LPO as delivered
    
    Args:
        lpo: LocalPurchaseOrder instance
        delivered_by: User who marked as delivered
    
    Returns:
        dict: Updated LPO status
    """
    allowed_statuses = [
        LocalPurchaseOrder.Status.APPROVED,
        LocalPurchaseOrder.Status.ISSUED,
        LocalPurchaseOrder.Status.PARTIALLY_DELIVERED
    ]
    
    if lpo.status not in allowed_statuses:
        raise ProcurementWorkflowError(
            f"Cannot mark as delivered. Current status: {lpo.status}"
        )
    
    previous_status = lpo.status
    lpo.status = LocalPurchaseOrder.Status.DELIVERED
    lpo.save()
    
    # Log activity
    log_activity(
        project_id=lpo.project.id,
        activity_type=ProjectActivity.ActivityType.LPO_DELIVERED,
        description=f"LPO {lpo.lpo_number} delivered by {lpo.supplier.name}",
        amount=lpo.total_amount,
        performed_by=delivered_by,
        related_object_type='LocalPurchaseOrder',
        related_object_id=lpo.id,
        metadata={
            'lpo_number': lpo.lpo_number,
            'supplier': lpo.supplier.name,
            'previous_status': previous_status
        }
    )
    
    return {
        'status': 'success',
        'message': f'LPO {lpo.lpo_number} marked as delivered',
        'new_status': lpo.status,
        'lpo_id': str(lpo.id)
    }


def mark_lpo_invoiced(lpo, invoiced_by, invoice_number=None):
    """
    Mark LPO as invoiced
    
    Args:
        lpo: LocalPurchaseOrder instance
        invoiced_by: User who marked as invoiced
        invoice_number: Optional invoice number
    
    Returns:
        dict: Updated LPO status
    """
    if lpo.status != LocalPurchaseOrder.Status.DELIVERED:
        raise ProcurementWorkflowError(
            f"Cannot mark as invoiced. Must be DELIVERED first. Current status: {lpo.status}"
        )
    
    lpo.status = LocalPurchaseOrder.Status.INVOICED
    lpo.save()
    
    # Log activity
    log_activity(
        project_id=lpo.project.id,
        activity_type=ProjectActivity.ActivityType.LPO_ISSUED,
        description=f"LPO {lpo.lpo_number} invoiced by {lpo.supplier.name}",
        amount=lpo.total_amount,
        performed_by=invoiced_by,
        related_object_type='LocalPurchaseOrder',
        related_object_id=lpo.id,
        metadata={
            'lpo_number': lpo.lpo_number,
            'supplier': lpo.supplier.name,
            'invoice_number': invoice_number,
            'previous_status': 'DELIVERED'
        }
    )
    
    return {
        'status': 'success',
        'message': f'LPO {lpo.lpo_number} marked as invoiced',
        'new_status': lpo.status,
        'lpo_id': str(lpo.id),
        'invoice_number': invoice_number
    }


def mark_lpo_paid(lpo, paid_by, payment_reference=None):
    """
    Mark LPO as paid
    
    Args:
        lpo: LocalPurchaseOrder instance
        paid_by: User who marked as paid
        payment_reference: Optional payment reference
    
    Returns:
        dict: Updated LPO status
    """
    if lpo.status != LocalPurchaseOrder.Status.INVOICED:
        raise ProcurementWorkflowError(
            f"Cannot mark as paid. Must be INVOICED first. Current status: {lpo.status}"
        )
    
    lpo.status = LocalPurchaseOrder.Status.PAID
    lpo.save()
    
    # Log activity
    log_activity(
        project_id=lpo.project.id,
        activity_type=ProjectActivity.ActivityType.SUPPLIER_PAYMENT,
        description=f"LPO {lpo.lpo_number} payment to {lpo.supplier.name}",
        amount=lpo.total_amount,
        performed_by=paid_by,
        related_object_type='LocalPurchaseOrder',
        related_object_id=lpo.id,
        metadata={
            'lpo_number': lpo.lpo_number,
            'supplier': lpo.supplier.name,
            'payment_reference': payment_reference,
            'previous_status': 'INVOICED'
        }
    )
    
    return {
        'status': 'success',
        'message': f'LPO {lpo.lpo_number} marked as paid',
        'new_status': lpo.status,
        'lpo_id': str(lpo.id),
        'payment_reference': payment_reference
    }
