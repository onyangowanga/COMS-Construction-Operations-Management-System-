"""
Supplier Models for COMS
Handles supplier management, LPOs, invoices, and payments
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Organization
from apps.projects.models import Project


class Supplier(models.Model):
    """
    Material and equipment suppliers
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='suppliers'
    )
    name = models.CharField(max_length=200, help_text=_("Supplier name"))
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    address = models.TextField(blank=True)
    tax_pin = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Tax PIN/VAT number")
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'suppliers'
        verbose_name = _('Supplier')
        verbose_name_plural = _('Suppliers')
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['name']),
        ]
    
    def __str__(self):
        return self.name


class LocalPurchaseOrder(models.Model):
    """
    Local Purchase Order (LPO) for material procurement
    """
    
    class Status(models.TextChoices):
        DRAFT = 'DRAFT', _('Draft')
        ISSUED = 'ISSUED', _('Issued')
        PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED', _('Partially Delivered')
        DELIVERED = 'DELIVERED', _('Delivered')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='lpos'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='lpos'
    )
    lpo_number = models.CharField(
        max_length=50,
        unique=True,
        help_text=_("Unique LPO number")
    )
    issue_date = models.DateField()
    total_amount = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        help_text=_("Total LPO value")
    )
    status = models.CharField(
        max_length=25,
        choices=Status.choices,
        default=Status.DRAFT
    )
    delivery_deadline = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'local_purchase_orders'
        verbose_name = _('Local Purchase Order')
        verbose_name_plural = _('Local Purchase Orders')
        ordering = ['-issue_date']
        indexes = [
            models.Index(fields=['lpo_number']),
            models.Index(fields=['supplier', 'project']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"LPO {self.lpo_number} - {self.supplier.name}"


class LPOItem(models.Model):
    """
    Individual items in a Local Purchase Order
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    lpo = models.ForeignKey(
        LocalPurchaseOrder,
        on_delete=models.CASCADE,
        related_name='items'
    )
    item_name = models.CharField(max_length=200, help_text=_("Material/Item description"))
    quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Quantity ordered")
    )
    unit = models.CharField(max_length=50, help_text=_("Unit of measurement"))
    unit_price = models.DecimalField(max_digits=12, decimal_places=2)
    total_price = models.DecimalField(max_digits=15, decimal_places=2)
    
    delivered_quantity = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text=_("Quantity delivered so far")
    )
    
    notes = models.TextField(blank=True)
    
    class Meta:
        db_table = 'lpo_items'
        verbose_name = _('LPO Item')
        verbose_name_plural = _('LPO Items')
        ordering = ['lpo', 'id']
        indexes = [
            models.Index(fields=['lpo']),
        ]
    
    def __str__(self):
        return f"{self.item_name} - {self.quantity} {self.unit}"


class SupplierInvoice(models.Model):
    """
    Invoices received from suppliers for materials delivered
    """
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending Payment')
        PARTIALLY_PAID = 'PARTIALLY_PAID', _('Partially Paid')
        PAID = 'PAID', _('Fully Paid')
        DISPUTED = 'DISPUTED', _('Disputed')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier = models.ForeignKey(
        Supplier,
        on_delete=models.PROTECT,
        related_name='invoices'
    )
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='supplier_invoices'
    )
    lpo = models.ForeignKey(
        LocalPurchaseOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='invoices',
        help_text=_("Linked LPO if applicable")
    )
    invoice_number = models.CharField(max_length=100)
    invoice_date = models.DateField()
    total_amount = models.DecimalField(max_digits=15, decimal_places=2)
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING
    )
    due_date = models.DateField(null=True, blank=True)
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier_invoices'
        verbose_name = _('Supplier Invoice')
        verbose_name_plural = _('Supplier Invoices')
        ordering = ['-invoice_date']
        unique_together = [['supplier', 'invoice_number']]
        indexes = [
            models.Index(fields=['supplier', 'project']),
            models.Index(fields=['status']),
            models.Index(fields=['invoice_date']),
        ]
    
    def __str__(self):
        return f"{self.supplier.name} - Invoice {self.invoice_number}"
    
    @property
    def total_paid(self):
        """Calculate total amount paid"""
        return self.payments.aggregate(
            total=models.Sum('amount')
        )['total'] or 0
    
    @property
    def outstanding_balance(self):
        """Calculate remaining balance"""
        return self.total_amount - self.total_paid


class SupplierPayment(models.Model):
    """
    Payments made to suppliers
    """
    
    class PaymentMethod(models.TextChoices):
        BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
        CHEQUE = 'CHEQUE', _('Cheque')
        CASH = 'CASH', _('Cash')
        MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
        OTHER = 'OTHER', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    supplier_invoice = models.ForeignKey(
        SupplierInvoice,
        on_delete=models.PROTECT,
        related_name='payments'
    )
    amount = models.DecimalField(max_digits=15, decimal_places=2)
    payment_date = models.DateField()
    payment_method = models.CharField(
        max_length=20,
        choices=PaymentMethod.choices,
        default=PaymentMethod.BANK_TRANSFER
    )
    reference_number = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'supplier_payments'
        verbose_name = _('Supplier Payment')
        verbose_name_plural = _('Supplier Payments')
        ordering = ['-payment_date']
        indexes = [
            models.Index(fields=['supplier_invoice', 'payment_date']),
        ]
    
    def __str__(self):
        return f"{self.supplier_invoice.supplier.name} - {self.amount} on {self.payment_date}"
