"""
Supplier Selectors - Optimized queries for supplier analytics
"""
from django.db.models import Sum, F, DecimalField
from django.db.models.functions import Coalesce
from apps.suppliers.models import Supplier, SupplierInvoice, SupplierPayment


def get_suppliers_outstanding_payments():
    """
    Get all suppliers with their outstanding payment balances
    """
    suppliers = Supplier.objects.prefetch_related(
        'supplierinvoice_set',
        'supplierinvoice_set__supplierpayment_set'
    ).annotate(
        total_invoiced=Coalesce(
            Sum('supplierinvoice__amount'),
            0,
            output_field=DecimalField()
        ),
        total_paid=Coalesce(
            Sum('supplierinvoice__supplierpayment__amount_paid'),
            0,
            output_field=DecimalField()
        )
    ).filter(
        total_invoiced__gt=F('total_paid')
    ).order_by('-total_invoiced')
    
    return suppliers
