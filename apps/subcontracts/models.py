"""
Subcontractor Management - Models

Database models for managing subcontractors, subcontract agreements,
and payment claims with financial integration.
"""

import uuid
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from apps.authentication.models import User
from apps.authentication.models import Organization
from apps.projects.models import Project


class Subcontractor(models.Model):
    """
    Subcontractor/vendor entity that can execute work packages.
    
    Represents external companies that perform specialized work
    on construction projects under subcontract agreements.
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='subcontractors',
        help_text=_("Organization that manages this subcontractor")
    )
    
    # === COMPANY INFORMATION ===
    
    name = models.CharField(
        max_length=255,
        help_text=_("Subcontractor company name")
    )
    
    company_registration = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Company registration number")
    )
    
    tax_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Tax identification number / VAT number")
    )
    
    # === CONTACT INFORMATION ===
    
    contact_person = models.CharField(
        max_length=255,
        help_text=_("Primary contact person name")
    )
    
    phone = models.CharField(
        max_length=20,
        help_text=_("Contact phone number")
    )
    
    email = models.EmailField(
        help_text=_("Contact email address")
    )
    
    address = models.TextField(
        help_text=_("Physical address")
    )
    
    # === ADDITIONAL INFORMATION ===
    
    specialization = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Area of specialization (e.g., Electrical, Plumbing, Masonry)")
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether this subcontractor is active for new contracts")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about the subcontractor")
    )
    
    # === METADATA ===
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_subcontractors',
        help_text=_("User who created this subcontractor record")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("Date and time when subcontractor was created")
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        db_table = 'subcontractors'
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['name']),
        ]
        verbose_name = _('Subcontractor')
        verbose_name_plural = _('Subcontractors')
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'name'],
                name='unique_subcontractor_per_org'
            )
        ]
    
    def __str__(self):
        return self.name
    
    @property
    def active_contracts_count(self):
        """Count of active subcontracts"""
        return self.subcontracts.filter(status=SubcontractAgreement.Status.ACTIVE).count()
    
    @property
    def total_contract_value(self):
        """Total value of all active contracts"""
        from django.db.models import Sum
        result = self.subcontracts.filter(
            status=SubcontractAgreement.Status.ACTIVE
        ).aggregate(total=Sum('contract_value'))
        return result['total'] or Decimal('0.00')


class SubcontractAgreement(models.Model):
    """
    Subcontract agreement for a specific work package within a project.
    
    Represents the contractual agreement between the main contractor
    and a subcontractor for performing specific work.
    """
    
    class Status(models.TextChoices):
        """Subcontract lifecycle statuses"""
        DRAFT = 'DRAFT', _('Draft - Under Preparation')
        ACTIVE = 'ACTIVE', _('Active - Work in Progress')
        COMPLETED = 'COMPLETED', _('Completed')
        TERMINATED = 'TERMINATED', _('Terminated')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # === RELATIONSHIPS ===
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='subcontracts',
        help_text=_("Project this subcontract belongs to")
    )
    
    subcontractor = models.ForeignKey(
        Subcontractor,
        on_delete=models.PROTECT,
        related_name='subcontracts',
        help_text=_("Subcontractor performing the work")
    )
    
    # === CONTRACT DETAILS ===
    
    contract_reference = models.CharField(
        max_length=100,
        unique=True,
        help_text=_("Unique contract reference number (e.g., SC-2026-001)")
    )
    
    scope_of_work = models.TextField(
        help_text=_("Detailed description of work to be performed")
    )
    
    contract_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))],
        help_text=_("Total contract value (excluding VAT)")
    )
    
    retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        help_text=_("Retention percentage to withhold from payments")
    )
    
    # === TIMELINE ===
    
    start_date = models.DateField(
        help_text=_("Contract start date")
    )
    
    end_date = models.DateField(
        help_text=_("Contract end date")
    )
    
    # === STATUS ===
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text=_("Current status of the subcontract")
    )
    
    # === ADDITIONAL TERMS ===
    
    payment_terms = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Payment terms (e.g., Net 30 days)")
    )
    
    vat_applicable = models.BooleanField(
        default=True,
        help_text=_("Whether VAT is applicable to this contract")
    )
    
    performance_bond_required = models.BooleanField(
        default=False,
        help_text=_("Whether a performance bond is required")
    )
    
    performance_bond_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[
            MinValueValidator(Decimal('0.00')),
            MaxValueValidator(Decimal('100.00'))
        ],
        help_text=_("Performance bond percentage if required")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Additional contract notes")
    )
    
    # === METADATA ===
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_subcontracts',
        help_text=_("User who created this subcontract")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    activated_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time when contract was activated")
    )
    
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time when contract was completed")
    )
    
    class Meta:
        db_table = 'subcontract_agreements'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['subcontractor']),
            models.Index(fields=['status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
        verbose_name = _('Subcontract Agreement')
        verbose_name_plural = _('Subcontract Agreements')
    
    def __str__(self):
        return f"{self.contract_reference} - {self.subcontractor.name}"
    
    @property
    def duration_days(self):
        """Calculate contract duration in days"""
        if self.start_date and self.end_date:
            return (self.end_date - self.start_date).days
        return 0
    
    @property
    def is_active(self):
        """Check if contract is currently active"""
        return self.status == self.Status.ACTIVE
    
    @property
    def retention_amount(self):
        """Calculate total retention amount"""
        return (self.contract_value * self.retention_percentage) / Decimal('100')
    
    @property
    def total_claimed(self):
        """Total amount claimed across all claims"""
        from django.db.models import Sum
        result = self.claims.aggregate(total=Sum('claimed_amount'))
        return result['total'] or Decimal('0.00')
    
    @property
    def total_certified(self):
        """Total amount certified across all claims"""
        from django.db.models import Sum
        result = self.claims.filter(
            status__in=[
                SubcontractClaim.Status.CERTIFIED,
                SubcontractClaim.Status.PAID
            ]
        ).aggregate(total=Sum('certified_amount'))
        return result['total'] or Decimal('0.00')
    
    @property
    def total_paid(self):
        """Total amount paid across all claims"""
        from django.db.models import Sum
        result = self.claims.filter(
            status=SubcontractClaim.Status.PAID
        ).aggregate(total=Sum('certified_amount'))
        return result['total'] or Decimal('0.00')
    
    @property
    def completion_percentage(self):
        """Calculate completion percentage based on certified amounts"""
        if self.contract_value > 0:
            return (self.total_certified / self.contract_value) * Decimal('100')
        return Decimal('0.00')
    
    @property
    def outstanding_balance(self):
        """Calculate outstanding balance (certified but not paid)"""
        return self.total_certified - self.total_paid


class SubcontractClaim(models.Model):
    """
    Payment claim submitted by subcontractor for work performed.
    
    Represents a claim for payment for work completed during a specific period,
    following the certification and payment workflow.
    """
    
    class Status(models.TextChoices):
        """Claim lifecycle statuses"""
        DRAFT = 'DRAFT', _('Draft - Being Prepared')
        SUBMITTED = 'SUBMITTED', _('Submitted - Awaiting Certification')
        CERTIFIED = 'CERTIFIED', _('Certified - Approved for Payment')
        REJECTED = 'REJECTED', _('Rejected')
        PAID = 'PAID', _('Paid')
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    # === RELATIONSHIPS ===
    
    subcontract = models.ForeignKey(
        SubcontractAgreement,
        on_delete=models.CASCADE,
        related_name='claims',
        help_text=_("Subcontract agreement this claim belongs to")
    )
    
    # === CLAIM DETAILS ===
    
    claim_number = models.CharField(
        max_length=50,
        help_text=_("Sequential claim number (e.g., SC-001-C001)")
    )
    
    period_start = models.DateField(
        help_text=_("Start date of claim period")
    )
    
    period_end = models.DateField(
        help_text=_("End date of claim period")
    )
    
    # === FINANCIAL AMOUNTS ===
    
    claimed_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Amount claimed by subcontractor")
    )
    
    certified_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Amount certified by project team")
    )
    
    retention_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Retention amount withheld from payment")
    )
    
    previous_cumulative_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))],
        help_text=_("Cumulative certified amount from previous claims")
    )
    
    # === STATUS & WORKFLOW ===
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT,
        db_index=True,
        help_text=_("Current status of the claim")
    )
    
    # === DATES ===
    
    submitted_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time claim was submitted")
    )
    
    certified_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time claim was certified")
    )
    
    paid_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time payment was made")
    )
    
    # === SUPPORTING INFORMATION ===
    
    description = models.TextField(
        blank=True,
        help_text=_("Description of work performed in this period")
    )
    
    rejection_reason = models.TextField(
        blank=True,
        help_text=_("Reason for rejection if claim was rejected")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes about this claim")
    )
    
    # === USER TRACKING ===
    
    submitted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='submitted_subcontract_claims',
        help_text=_("User who submitted the claim")
    )
    
    certified_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='certified_subcontract_claims',
        help_text=_("User who certified the claim")
    )
    
    # === METADATA ===
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_subcontract_claims',
        help_text=_("User who created this claim")
    )
    
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    class Meta:
        db_table = 'subcontract_claims'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['subcontract', 'status']),
            models.Index(fields=['status']),
            models.Index(fields=['submitted_date']),
            models.Index(fields=['certified_date']),
        ]
        verbose_name = _('Subcontract Claim')
        verbose_name_plural = _('Subcontract Claims')
        constraints = [
            models.UniqueConstraint(
                fields=['subcontract', 'claim_number'],
                name='unique_claim_number_per_subcontract'
            )
        ]
    
    def __str__(self):
        return f"{self.claim_number} - {self.subcontract.contract_reference}"
    
    @property
    def cumulative_certified_amount(self):
        """Calculate cumulative certified amount including this claim"""
        return self.previous_cumulative_amount + self.certified_amount
    
    @property
    def net_payment_amount(self):
        """Calculate net payment amount (certified - retention)"""
        return self.certified_amount - self.retention_amount
    
    @property
    def is_pending_certification(self):
        """Check if claim is awaiting certification"""
        return self.status == self.Status.SUBMITTED
    
    @property
    def is_pending_payment(self):
        """Check if claim is certified but not paid"""
        return self.status == self.Status.CERTIFIED
    
    @property
    def period_days(self):
        """Calculate claim period duration in days"""
        if self.period_start and self.period_end:
            return (self.period_end - self.period_start).days
        return 0
    
    @property
    def variance_amount(self):
        """Calculate variance between claimed and certified amounts"""
        return self.certified_amount - self.claimed_amount
    
    @property
    def processing_time_days(self):
        """Calculate time taken from submission to certification"""
        if self.submitted_date and self.certified_date:
            return (self.certified_date - self.submitted_date).days
        return None
