"""
Signals for automatic activity tracking
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.ledger.models import Expense
from apps.suppliers.models import LocalPurchaseOrder
from apps.clients.models import ClientPayment
from apps.media.models import ProjectPhoto
from apps.projects.models import ProjectStage
from api.services.activity_service import log_activity
from apps.workflows.models import ProjectActivity


@receiver(post_save, sender=Expense)
def log_expense_created(sender, instance, created, **kwargs):
    """Log activity when expense is created"""
    if created:
        log_activity(
            project_id=instance.project.id,
            activity_type=ProjectActivity.ActivityType.EXPENSE_CREATED,
            description=f"Expense created: {instance.get_expense_type_display()} - {instance.amount}",
            amount=instance.amount,
            performed_by=None,  # Can be set from request context if available
            related_object_type='Expense',
            related_object_id=instance.id,
            metadata={
                'expense_type': instance.expense_type,
                'reference_number': instance.reference_number
            }
        )


@receiver(post_save, sender=LocalPurchaseOrder)
def log_lpo_issued(sender, instance, created, **kwargs):
    """Log activity when LPO is issued"""
    if created:
        log_activity(
            project_id=instance.project.id,
            activity_type=ProjectActivity.ActivityType.LPO_ISSUED,
            description=f"LPO {instance.lpo_number} issued to {instance.supplier.name}",
            amount=instance.total_amount,
            performed_by=None,
            related_object_type='LocalPurchaseOrder',
            related_object_id=instance.id,
            metadata={
                'lpo_number': instance.lpo_number,
                'supplier': instance.supplier.name,
                'status': instance.status
            }
        )


@receiver(post_save, sender=ClientPayment)
def log_client_payment(sender, instance, created, **kwargs):
    """Log activity when client payment is received"""
    if created:
        log_activity(
            project_id=instance.project.id,
            activity_type=ProjectActivity.ActivityType.CLIENT_PAYMENT,
            description=f"Client payment received: {instance.amount_paid}",
            amount=instance.amount_paid,
            performed_by=None,
            related_object_type='ClientPayment',
            related_object_id=instance.id,
            metadata={
                'payment_date': instance.payment_date.isoformat(),
                'payment_method': instance.payment_method
            }
        )


@receiver(post_save, sender=ProjectPhoto)
def log_photo_uploaded(sender, instance, created, **kwargs):
    """Log activity when photo is uploaded"""
    if created:
        log_activity(
            project_id=instance.project.id,
            activity_type=ProjectActivity.ActivityType.PHOTO_UPLOADED,
            description=f"Photo uploaded: {instance.caption or 'Project photo'}",
            amount=None,
            performed_by=instance.uploaded_by,
            related_object_type='ProjectPhoto',
            related_object_id=instance.id,
            metadata={
                'stage': instance.stage.name if instance.stage else None,
                'caption': instance.caption
            }
        )


@receiver(pre_save, sender=ProjectStage)
def log_stage_completion(sender, instance, **kwargs):
    """Log activity when stage is completed"""
    if instance.pk:
        try:
            old_instance = ProjectStage.objects.get(pk=instance.pk)
            # Check if stage was just completed
            if not old_instance.is_completed and instance.is_completed:
                log_activity(
                    project_id=instance.project.id,
                    activity_type=ProjectActivity.ActivityType.STAGE_COMPLETED,
                    description=f"Stage completed: {instance.name}",
                    amount=None,
                    performed_by=None,
                    related_object_type='ProjectStage',
                    related_object_id=instance.id,
                    metadata={
                        'stage_name': instance.name,
                        'target_end_date': instance.target_end_date.isoformat() if instance.target_end_date else None,
                        'actual_end_date': instance.actual_end_date.isoformat() if instance.actual_end_date else None
                    }
                )
        except ProjectStage.DoesNotExist:
            pass
