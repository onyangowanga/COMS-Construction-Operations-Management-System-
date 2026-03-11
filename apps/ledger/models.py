"""
Ledger Models for COMS
Manages financial expenses and allocation to BQ items for variance tracking
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project
from apps.bq.models import BQItem


class Expense(models.Model):
    """
    Project expenses for tracking actual costs against BQ
    """
    
    class ExpenseType(models.TextChoices):
        MATERIALS = 'MATERIALS', _('Materials')
        LABOUR = 'LABOUR', _('Labour')
        CASUAL_LABOUR = 'CASUAL_LABOUR', _('Casual Labour')
        CONSULTANT = 'CONSULTANT', _('Consultant Fees')
        EQUIPMENT = 'EQUIPMENT', _('Equipment Hire')
        TRANSPORT = 'TRANSPORT', _('Transport')
        UTILITIES = 'UTILITIES', _('Utilities (Water, Power)')
        STATUTORY = 'STATUTORY', _('Statutory Fees (NCA, County)')
        INSURANCE = 'INSURANCE', _('Insurance')
        MISCELLANEOUS = 'MISCELLANEOUS', _('Miscellaneous')
    
    class ApprovalStatus(models.TextChoices):
        APPROVED = 'APPROVED', _('Approved')
        PENDING_APPROVAL = 'PENDING_APPROVAL', _('Pending Approval')
        REQUIRES_APPROVAL = 'REQUIRES_APPROVAL', _('Requires Approval')
        REJECTED = 'REJECTED', _('Rejected')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='expenses'
    )
    expense_type = models.CharField(
        max_length=20,
        choices=ExpenseType.choices
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Expense amount")
    )
    date = models.DateField(help_text=_("Expense date"))
    description = models.TextField(help_text=_("Expense description"))
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Receipt/Invoice number")
    )
    approval_status = models.CharField(
        max_length=25,
        choices=ApprovalStatus.choices,
        default=ApprovalStatus.APPROVED,
        help_text=_("Approval status for budget control")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'expenses'
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-date']
        indexes = [
            models.Index(fields=['project', 'expense_type']),
            models.Index(fields=['date']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.get_expense_type_display()} - {self.amount}"
    
    @property
    def allocated_amount(self):
        """Calculate total amount allocated to BQ items"""
        return self.allocations.aggregate(
            total=models.Sum('allocated_amount')
        )['total'] or 0
    
    @property
    def unallocated_amount(self):
        """Calculate amount not yet allocated"""
        return self.amount - self.allocated_amount


class ExpenseAllocation(models.Model):
    """
    Allocates expenses to specific BQ items for variance analysis
    Enables BQ vs Actual Cost tracking
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    expense = models.ForeignKey(
        Expense,
        on_delete=models.CASCADE,
        related_name='allocations'
    )
    bq_item = models.ForeignKey(
        BQItem,
        on_delete=models.CASCADE,
        related_name='expense_allocations',
        help_text=_("BQ item this expense is allocated to")
    )
    allocated_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Amount allocated to this BQ item")
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'expense_allocations'
        verbose_name = _('Expense Allocation')
        verbose_name_plural = _('Expense Allocations')
        ordering = ['expense', 'bq_item']
        indexes = [
            models.Index(fields=['expense']),
            models.Index(fields=['bq_item']),
        ]
    
    def __str__(self):
        return f"{self.expense.description[:30]} → {self.bq_item.description[:30]} ({self.allocated_amount})"
