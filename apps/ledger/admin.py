"""
Django Admin configuration for Ledger app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Expense, ExpenseAllocation


class ExpenseAllocationInline(admin.TabularInline):
    """Inline for expense allocations to BQ items"""
    model = ExpenseAllocation
    extra = 1
    fields = ['bq_item', 'allocated_amount', 'notes']
    autocomplete_fields = ['bq_item']


@admin.register(Expense)
class ExpenseAdmin(admin.ModelAdmin):
    list_display = ['project', 'expense_type', 'amount_display', 'date', 'allocated_status', 'reference_number']
    list_filter = ['expense_type', 'date', 'project']
    search_fields = ['project__name', 'project__code', 'description', 'reference_number']
    autocomplete_fields = ['project']
    date_hierarchy = 'date'
    ordering = ['-date']
    inlines = [ExpenseAllocationInline]
    
    fieldsets = (
        (_('Expense Information'), {
            'fields': ('project', 'expense_type', 'date')
        }),
        (_('Amount & Reference'), {
            'fields': ('amount', 'reference_number')
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
    
    def allocated_status(self, obj):
        allocated = obj.allocated_amount
        unallocated = obj.unallocated_amount
        if unallocated == 0:
            return "✓ Fully Allocated"
        elif allocated > 0:
            return f"⚠ Partial ({allocated:,.2f} / {obj.amount:,.2f})"
        return "✗ Not Allocated"
    allocated_status.short_description = _('Allocation Status')


@admin.register(ExpenseAllocation)
class ExpenseAllocationAdmin(admin.ModelAdmin):
    list_display = ['expense', 'bq_item', 'amount_display', 'created_at']
    list_filter = ['created_at']
    search_fields = ['expense__description', 'bq_item__description', 'notes']
    autocomplete_fields = ['expense', 'bq_item']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    
    fieldsets = (
        (_('Allocation Details'), {
            'fields': ('expense', 'bq_item', 'allocated_amount')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at']
    
    def amount_display(self, obj):
        return f"KES {obj.allocated_amount:,.2f}"
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'allocated_amount'
