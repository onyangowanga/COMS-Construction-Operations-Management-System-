"""
Supplier Analytics Services - Business logic for supplier analytics
"""
from decimal import Decimal


def calculate_supplier_outstanding_payments(suppliers):
    """
    Calculate outstanding payments for suppliers
    
    Returns:
        list: Suppliers with outstanding balances
    """
    outstanding_data = []
    
    for supplier in suppliers:
        total_invoiced = supplier.total_invoiced or Decimal('0')
        total_paid = supplier.total_paid or Decimal('0')
        balance = total_invoiced - total_paid
        
        if balance > 0:
            outstanding_data.append({
                'supplier_id': str(supplier.id),
                'supplier_name': supplier.supplier_name,
                'contact_person': supplier.contact_person,
                'phone': supplier.phone,
                'email': supplier.email,
                'total_invoiced': float(total_invoiced),
                'total_paid': float(total_paid),
                'outstanding_balance': float(balance),
                'payment_completion_percentage': float((total_paid / total_invoiced * 100) if total_invoiced > 0 else 0),
            })
    
    return outstanding_data
