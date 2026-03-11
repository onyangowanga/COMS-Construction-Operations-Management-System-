"""
Workflow Models for COMS
Handles approvals and activity tracking
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.contrib.auth import get_user_model

User = get_user_model()


class Approval(models.Model):
    """
    Generic approval model for expenses, payments, and other transactions
    """
    
    class ApprovalType(models.TextChoices):
        EXPENSE = 'EXPENSE', _('Expense Approval')
        SUPPLIER_PAYMENT = 'SUPPLIER_PAYMENT', _('Supplier Payment')
        CONSULTANT_PAYMENT = 'CONSULTANT_PAYMENT', _('Consultant Payment')
        LPO = 'LPO', _('Local Purchase Order')
        BUDGET_OVERRIDE = 'BUDGET_OVERRIDE', _('Budget Override')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Approval')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    approval_type = models.CharField(
        max_length=25,
        choices=ApprovalType.choices
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    
    # Generic foreign keys for different approval types
    expense_id = models.UUIDField(null=True, blank=True)
    supplier_payment_id = models.UUIDField(null=True, blank=True)
    consultant_payment_id = models.UUIDField(null=True, blank=True)
    lpo_id = models.UUIDField(null=True, blank=True)
    
    # Approval details
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='approval_requests'
    )
    requested_at = models.DateTimeField(auto_now_add=True)
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvals_given'
    )
    approved_at = models.DateTimeField(null=True, blank=True)
    
    reason = models.TextField(
        blank=True,
        help_text=_("Reason for approval request or rejection")
    )
    notes = models.TextField(blank=True)
    
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Amount requiring approval")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'approvals'
        verbose_name = _('Approval')
        verbose_name_plural = _('Approvals')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['approval_type', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['requested_by']),
            models.Index(fields=['approved_by']),
        ]
    
    def __str__(self):
        return f"{self.approval_type} - {self.status}"


class ProjectActivity(models.Model):
    """
    Activity timeline for project events
    """
    
    class ActivityType(models.TextChoices):
        EXPENSE_CREATED = 'EXPENSE_CREATED', _('Expense Created')
        LPO_ISSUED = 'LPO_ISSUED', _('LPO Issued')
        LPO_APPROVED = 'LPO_APPROVED', _('LPO Approved')
        LPO_DELIVERED = 'LPO_DELIVERED', _('LPO Delivered')
        SUPPLIER_PAYMENT = 'SUPPLIER_PAYMENT', _('Supplier Payment')
        CONSULTANT_PAYMENT = 'CONSULTANT_PAYMENT', _('Consultant Payment')
        CLIENT_PAYMENT = 'CLIENT_PAYMENT', _('Client Payment Received')
        PHOTO_UPLOADED = 'PHOTO_UPLOADED', _('Photo Uploaded')
        STAGE_COMPLETED = 'STAGE_COMPLETED', _('Stage Completed')
        BUDGET_OVERRUN = 'BUDGET_OVERRUN', _('Budget Overrun Detected')
        APPROVAL_REQUESTED = 'APPROVAL_REQUESTED', _('Approval Requested')
        APPROVAL_GRANTED = 'APPROVAL_GRANTED', _('Approval Granted')
        APPROVAL_REJECTED = 'APPROVAL_REJECTED', _('Approval Rejected')
        PROJECT_CREATED = 'PROJECT_CREATED', _('Project Created')
        PROJECT_STARTED = 'PROJECT_STARTED', _('Project Started')
        PROJECT_COMPLETED = 'PROJECT_COMPLETED', _('Project Completed')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project_id = models.UUIDField(db_index=True)
    activity_type = models.CharField(
        max_length=25,
        choices=ActivityType.choices
    )
    
    # Generic reference to related object
    related_object_type = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Type of related object (Expense, LPO, etc.)")
    )
    related_object_id = models.UUIDField(null=True, blank=True)
    
    # Activity details
    description = models.TextField()
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Amount if applicable")
    )
    
    performed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='project_activities'
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Additional activity metadata")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_activities'
        verbose_name = _('Project Activity')
        verbose_name_plural = _('Project Activities')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project_id', '-created_at']),
            models.Index(fields=['activity_type']),
            models.Index(fields=['performed_by']),
        ]
    
    def __str__(self):
        return f"{self.activity_type} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
