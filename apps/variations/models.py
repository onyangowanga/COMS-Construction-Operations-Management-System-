"""
Variation Order Models

Manages variation orders (change orders) throughout their lifecycle.
"""

from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils import timezone
from apps.projects.models import Project
from apps.authentication.models import User


class VariationOrder(models.Model):
    """
    Variation Order (Change Order) for construction projects.
    
    Tracks contract modifications, scope changes, and additional works.
    Includes approval workflow and financial impact tracking.
    """
    
    # Status Workflow
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', 'Draft'
        SUBMITTED = 'SUBMITTED', 'Submitted for Approval'
        APPROVED = 'APPROVED', 'Approved'
        REJECTED = 'REJECTED', 'Rejected'
        INVOICED = 'INVOICED', 'Invoiced'
        PAID = 'PAID', 'Paid'
    
    # Priority levels
    class Priority(models.TextChoices):
        LOW = 'LOW', 'Low Priority'
        MEDIUM = 'MEDIUM', 'Medium Priority'
        HIGH = 'HIGH', 'High Priority'
        URGENT = 'URGENT', 'Urgent'
    
    # Change Type
    class ChangeType(models.TextChoices):
        SCOPE_CHANGE = 'SCOPE_CHANGE', 'Scope Change'
        DESIGN_CHANGE = 'DESIGN_CHANGE', 'Design Change'
        SITE_CONDITION = 'SITE_CONDITION', 'Site Condition'
        CLIENT_REQUEST = 'CLIENT_REQUEST', 'Client Request'
        REGULATORY = 'REGULATORY', 'Regulatory/Compliance'
        OTHER = 'OTHER', 'Other'
    
    # Variation Type (Classification for analysis)
    class VariationType(models.TextChoices):
        CLIENT_INSTRUCTION = 'CLIENT_INSTRUCTION', 'Client Instruction'
        DESIGN_CHANGE = 'DESIGN_CHANGE', 'Design Change'
        ADDITIONAL_WORK = 'ADDITIONAL_WORK', 'Additional Work'
        OMISSION = 'OMISSION', 'Omission/Deduction'
        ERROR_CORRECTION = 'ERROR_CORRECTION', 'Error Correction'
        UNFORESEEN_CONDITION = 'UNFORESEEN_CONDITION', 'Unforeseen Site Condition'
    
    # === IDENTIFICATION ===
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='variation_orders'
    )
    
    reference_number = models.CharField(
        max_length=50,
        help_text="Unique variation order reference (e.g., VO-2026-001)"
    )
    sequence = models.IntegerField(
        help_text="Sequence component used for variation reference generation"
    )
    
    title = models.CharField(
        max_length=200,
        help_text="Brief description of the variation"
    )
    
    description = models.TextField(
        help_text="Detailed description of the variation and justification"
    )
    
    change_type = models.CharField(
        max_length=20,
        choices=ChangeType.choices,
        default=ChangeType.SCOPE_CHANGE
    )
    
    variation_type = models.CharField(
        max_length=25,
        choices=VariationType.choices,
        default=VariationType.ADDITIONAL_WORK,
        help_text="Classification of variation for cost analysis"
    )
    
    priority = models.CharField(
        max_length=10,
        choices=Priority.choices,
        default=Priority.MEDIUM
    )
    
    # === DATES ===
    
    instruction_date = models.DateField(
        help_text="Date of instruction/request",
        default=timezone.now
    )
    
    required_by_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date by which variation must be completed"
    )
    
    submitted_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date variation was submitted for approval"
    )
    
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date variation was approved"
    )
    
    # === FINANCIAL VALUES ===
    
    estimated_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Estimated cost of variation (initial quote)"
    )
    
    approved_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Final approved value (may differ from estimate)"
    )
    
    invoiced_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount invoiced for this variation"
    )
    
    paid_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount paid for this variation"
    )
    
    # === WORKFLOW & STATUS ===
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # === RESPONSIBLE PARTIES ===
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='variations_created',
        help_text="User who created this variation"
    )
    
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variations_submitted',
        help_text="User who submitted for approval"
    )
    
    approved_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variations_approved',
        help_text="User who approved this variation"
    )
    
    certified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='variations_certified',
        help_text="Consultant who certified this variation (QS, Architect, Engineer)"
    )
    
    # === CONSULTANT CERTIFICATION ===
    
    certified_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text="Amount certified by consultant (may differ from approved value)"
    )
    
    certified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Date variation was certified by consultant"
    )
    
    # === ADDITIONAL INFO ===
    
    justification = models.TextField(
        blank=True,
        help_text="Business justification for the variation"
    )
    
    client_reference = models.CharField(
        max_length=100,
        blank=True,
        help_text="Client's reference number for this variation"
    )
    
    impact_on_schedule = models.TextField(
        blank=True,
        help_text="Impact on project timeline"
    )
    
    technical_notes = models.TextField(
        blank=True,
        help_text="Technical specifications and notes"
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text="Reason for rejection (if status is REJECTED)"
    )
    
    # === METADATA ===
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'variation_orders'
        ordering = ['-instruction_date', '-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['reference_number']),
            models.Index(fields=['project', 'sequence']),
            models.Index(fields=['status']),
            models.Index(fields=['instruction_date']),
        ]
        constraints = [
            models.UniqueConstraint(
                fields=['project', 'sequence'],
                name='unique_variation_sequence_per_project',
            )
        ]
        verbose_name = 'Variation Order'
        verbose_name_plural = 'Variation Orders'
    @property
    def certification_variance(self):
        """Difference between certified and approved amounts"""
        if self.certified_amount and self.approved_value:
            return self.certified_amount - self.approved_value
        return Decimal('0.00')
    
    @property
    def is_certified(self):
        """Check if variation has been certified by consultant"""
        return self.certified_amount is not None and self.certified_by is not None
    
    def can_approve(self):
        """Check if variation can be approved"""
        return self.status == self.Status.SUBMITTED
    
    def can_reject(self):
        """Check if variation can be rejected"""
        return self.status == self.Status.SUBMITTED
    
    def can_submit(self):
        """Check if variation can be submitted"""
        return self.status == self.Status.DRAFT
    
    def can_invoice(self):
        """Check if variation can be invoiced"""
        return self.status == self.Status.APPROVED
    
    def can_certify(self):
        """Check if variation can be certified by consultant"""
        # Can certify if submitted or approved
        return self.status in [self.Status.SUBMITTED, self.Status.APPROVED]
    def value_variance(self):
        """Difference between estimated and approved value"""
        if self.approved_value > 0:
            return self.approved_value - self.estimated_value
        return Decimal('0.00')
    
    @property
    def outstanding_amount(self):
        """Amount approved but not yet paid"""
        return self.approved_value - self.paid_value
    
    def can_approve(self):
        """Check if variation can be approved"""
        return self.status == self.Status.SUBMITTED
    
    def can_reject(self):
        """Check if variation can be rejected"""
        return self.status == self.Status.SUBMITTED
    
    def can_submit(self):
        """Check if variation can be submitted"""
        return self.status == self.Status.DRAFT
    
    def can_invoice(self):
        """Check if variation can be invoiced"""
        return self.status == self.Status.APPROVED
