"""
Valuation Models for COMS
Manages construction valuations and Interim Payment Certificates (IPC)
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.projects.models import Project
from apps.bq.models import BQItem


class Valuation(models.Model):
    """
    Interim Payment Certificate (IPC) for construction projects
    Tracks work completed, retention, and payments due
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        SUBMITTED = 'SUBMITTED', _('Submitted')
        APPROVED = 'APPROVED', _('Approved')
        PAID = 'PAID', _('Paid')
        REJECTED = 'REJECTED', _('Rejected')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='valuations'
    )
    valuation_number = models.CharField(
        max_length=50,
        help_text=_("Unique valuation number (e.g., IPC-001)")
    )
    valuation_date = models.DateField(
        help_text=_("Date of valuation")
    )
    
    # Financial calculations
    work_completed_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total value of work completed to date")
    )
    retention_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Retention percentage (typically 5-10%)")
    )
    retention_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Retention amount held back")
    )
    previous_payments = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total of all previous payments")
    )
    amount_due = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Amount due this valuation")
    )
    
    # Status and approvals
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DRAFT
    )
    
    # Additional fields
    notes = models.TextField(
        blank=True,
        help_text=_("Additional notes or comments")
    )
    submitted_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='valuations_submitted'
    )
    approved_by = models.ForeignKey(
        'authentication.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='valuations_approved'
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Date and time of approval")
    )
    payment_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date payment was made")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'valuations'
        verbose_name = _('Valuation')
        verbose_name_plural = _('Valuations')
        ordering = ['-valuation_date', '-valuation_number']
        unique_together = [['project', 'valuation_number']]
        indexes = [
            models.Index(fields=['project', '-valuation_date']),
            models.Index(fields=['status']),
            models.Index(fields=['valuation_number']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.valuation_number}"
    
    @property
    def gross_amount(self):
        """Amount before retention"""
        return self.work_completed_value - self.previous_payments
    
    @property
    def net_amount(self):
        """Amount after retention (same as amount_due)"""
        return self.amount_due


class BQItemProgress(models.Model):
    """
    Tracks work progress on individual BQ items for each valuation
    Records quantity completed to calculate work value
    """
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    valuation = models.ForeignKey(
        Valuation,
        on_delete=models.CASCADE,
        related_name='item_progress'
    )
    bq_item = models.ForeignKey(
        BQItem,
        on_delete=models.CASCADE,
        related_name='progress_records'
    )
    
    # Progress tracking
    previous_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Quantity completed in previous valuations")
    )
    this_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Quantity completed this period")
    )
    cumulative_quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total quantity completed to date")
    )
    
    # Value calculations
    previous_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Value from previous valuations")
    )
    this_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Value of work this period")
    )
    cumulative_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total value to date")
    )
    
    notes = models.TextField(
        blank=True,
        help_text=_("Notes about this item's progress")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'bq_item_progress'
        verbose_name = _('BQ Item Progress')
        verbose_name_plural = _('BQ Item Progress')
        ordering = ['valuation', 'bq_item']
        unique_together = [['valuation', 'bq_item']]
        indexes = [
            models.Index(fields=['valuation']),
            models.Index(fields=['bq_item']),
        ]
    
    def __str__(self):
        return f"{self.valuation.valuation_number} - {self.bq_item.description[:50]}"
    
    @property
    def percentage_complete(self):
        """Calculate percentage of BQ item completed"""
        if self.bq_item.quantity == 0:
            return Decimal('0.00')
        return (self.cumulative_quantity / self.bq_item.quantity) * 100
    
    def save(self, *args, **kwargs):
        """Auto-calculate cumulative values and this period's value"""
        # Calculate cumulative quantity
        self.cumulative_quantity = self.previous_quantity + self.this_quantity
        
        # Calculate values based on BQ item rate
        self.previous_value = self.previous_quantity * self.bq_item.rate
        self.this_value = self.this_quantity * self.bq_item.rate
        self.cumulative_value = self.cumulative_quantity * self.bq_item.rate
        
        super().save(*args, **kwargs)
