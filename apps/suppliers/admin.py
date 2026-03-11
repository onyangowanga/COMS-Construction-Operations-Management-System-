"""
Django Admin configuration for Suppliers app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Supplier, LocalPurchaseOrder, LPOItem, SupplierInvoice, SupplierPayment


class LPOItemInline(admin.TabularInline):
    """Inline for LPO items"""
    model = LPOItem
    extra = 1
    fields = ['description', 'quantity', 'unit_price', 'total_display']
    readonly_fields = ['total_display']
    
    def total_display(self, obj):
        if obj.pk:
            return f"KES {obj.total_price:,.2f}"
        return "-"
    total_display.short_description = _('Total')


class SupplierPaymentInline(admin.TabularInline):
    """Inline for supplier payments"""
    model = SupplierPayment
    extra = 0
    fields = ['amount', 'payment_date', 'payment_method', 'reference_number']


@admin.register(Supplier)
class SupplierAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'tax_pin', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'phone', 'email', 'tax_pin', 'address']
    autocomplete_fields = ['organization']
    ordering = ['name']
    
    fieldsets = (
        (_('Supplier Information'), {
            'fields': ('organization', 'name')
        }),
        (_('Contact Details'), {
            'fields': ('phone', 'email', 'address')
        }),
        (_('Tax Information'), {
            'fields': ('tax_pin',)
        }),
        (_('Status'), {
            'fields': ('is_active',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']


@admin.register(LocalPurchaseOrder)
class LocalPurchaseOrderAdmin(admin.ModelAdmin):
    list_display = ['lpo_number', 'supplier', 'project', 'issue_date', 'total_display', 'status']
    list_filter = ['status', 'issue_date', 'created_at']
    search_fields = ['lpo_number', 'supplier__name', 'project__name', 'project__code']
    autocomplete_fields = ['supplier', 'project']
    date_hierarchy = 'issue_date'
    ordering = ['-issue_date']
    inlines = [LPOItemInline]
    
    fieldsets = (
        (_('LPO Information'), {
            'fields': ('lpo_number', 'supplier', 'project')
        }),
        (_('Details'), {
            'fields': ('issue_date', 'total_amount', 'status')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def total_display(self, obj):
        return f"KES {obj.total_amount:,.2f}"
    total_display.short_description = _('Total Amount')
    total_display.admin_order_field = 'total_amount'


@admin.register(LPOItem)
class LPOItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'lpo', 'quantity', 'unit_price', 'total_display']
    list_filter = ['lpo__status']
    search_fields = ['description', 'lpo__lpo_number', 'lpo__supplier__name']
    autocomplete_fields = ['lpo']
    
    def total_display(self, obj):
        return f"KES {obj.total_price:,.2f}"
    total_display.short_description = _('Total')


@admin.register(SupplierInvoice)
class SupplierInvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'supplier', 'lpo', 'invoice_date', 'total_display', 'payment_status']
    list_filter = ['payment_status', 'invoice_date']
    search_fields = ['invoice_number', 'supplier__name', 'lpo__lpo_number']
    autocomplete_fields = ['supplier', 'lpo']
    date_hierarchy = 'invoice_date'
    inlines = [SupplierPaymentInline]
    
    fieldsets = (
        (_('Invoice Information'), {
            'fields': ('invoice_number', 'supplier', 'lpo')
        }),
        (_('Amount & Status'), {
            'fields': ('invoice_date', 'total_amount', 'payment_status')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def total_display(self, obj):
        return f"KES {obj.total_amount:,.2f}"
    total_display.short_description = _('Amount')
    total_display.admin_order_field = 'total_amount'


@admin.register(SupplierPayment)
class SupplierPaymentAdmin(admin.ModelAdmin):
    list_display = ['invoice', 'amount_display', 'payment_date', 'payment_method', 'reference_number']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['invoice__invoice_number', 'invoice__supplier__name', 'reference_number']
    autocomplete_fields = ['invoice']
    date_hierarchy = 'payment_date'
    ordering = ['-payment_date']
    
    readonly_fields = ['created_at', 'updated_at']
    
    def amount_display(self, obj):
        return f"KES {obj.amount:,.2f}"
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'
