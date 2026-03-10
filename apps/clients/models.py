"""
Client Models for COMS
Handles client payments and receipts
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project


class ClientPayment(models.Model):
    """
    Payments received from project clients
    """
    
    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CHEQUE = 'CHEQUE', _('Cheque')
        CASH = 'CASH', _('Cash')
        MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
        OTHER = 'OTHER', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='client_payments'
    )
    amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Payment amount received")
    )
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Transaction reference, cheque number, or receipt number")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Payment description or notes")
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_payments'
        verbose_name = _('Client Payment')
        verbose_name_plural = _('Client Payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['project', 'payment_date']),
            models.Index(fields=['reference_number']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.amount} on {self.payment_date}"


class ClientReceipt(models.Model):
    """
    Official receipts issued to clients for payments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    payment = models.OneToOneField(
        ClientPayment,
        on_delete=models.CASCADE,
        related_name='receipt'
    )
    receipt_number = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Official receipt number")
    )
    document_path = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Path to receipt document file")
    )
    issued_date = models.DateField(auto_now_add=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'client_receipts'
        verbose_name = _('Client Receipt')
        verbose_name_plural = _('Client Receipts')
        ordering = ['-issued_date']
        indexes = [
            models.Index(fields=['receipt_number']),
            models.Index(fields=['issued_date']),
        ]
    
    def __str__(self):
        return f"Receipt {self.receipt_number} - {self.payment.amount}"
