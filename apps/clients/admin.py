"""
Django Admin configuration for Clients app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import ClientPayment, ClientReceipt


class ClientReceiptInline(admin.StackedInline):
    """Inline for client receipts"""
    model = ClientReceipt
    extra = 0
    fields = ['receipt_number', 'document_path', 'notes']


@admin.register(ClientPayment)
class ClientPaymentAdmin(admin.ModelAdmin):
    list_display = ['project', 'amount_display', 'payment_date', 'payment_method', 'reference_number', 'has_receipt']
    list_filter = ['payment_method', 'payment_date', 'created_at']
    search_fields = ['project__name', 'project__code', 'reference_number', 'description']
    autocomplete_fields = ['project']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    inlines = [ClientReceiptInline]
    
    fieldsets = (
        (_('Payment Information'), {
            'fields': ('project', 'payment_date')
        }),
        (_('Amount & Method'), {
            'fields': ('amount', 'payment_method', 'reference_number')
        }),
        (_('Description'), {
            'fields': ('description',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def amount_display(self, obj):
        return f"KES {obj.amount:,.2f}"
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'
    
    def has_receipt(self, obj):
        return "✓" if hasattr(obj, 'receipt') else "✗"
    has_receipt.short_description = _('Receipt Issued')
    has_receipt.boolean = True


@admin.register(ClientReceipt)
class ClientReceiptAdmin(admin.ModelAdmin):
    list_display = ['receipt_number', 'payment', 'issued_date', 'amount_display', 'created_at']
    list_filter = ['issued_date']
    search_fields = ['receipt_number', 'payment__project__name', 'payment__reference_number']
    autocomplete_fields = ['payment']
    date_hierarchy = 'issued_date'
    ordering = ['-issued_date']
    
    fieldsets = (
        (_('Receipt Information'), {
            'fields': ('receipt_number', 'payment', 'document_path')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('issued_date', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['issued_date', 'created_at', 'updated_at']
    
    def amount_display(self, obj):
        return f"KES {obj.payment.amount:,.2f}"
    amount_display.short_description = _('Amount')
