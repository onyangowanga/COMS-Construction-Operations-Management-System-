"""
Admin configuration for Valuations
"""
from django.contrib import admin
from .models import Valuation, BQItemProgress


class BQItemProgressInline(admin.TabularInline):
    """Inline admin for BQ item progress within valuations"""
    model = BQItemProgress
    extra = 0
    fields = (
        'bq_item',
        'previous_quantity',
        'this_quantity',
        'cumulative_quantity',
        'this_value',
        'cumulative_value',
        'notes'
    )
    readonly_fields = ('cumulative_quantity', 'previous_value', 'this_value', 'cumulative_value')


@admin.register(Valuation)
class ValuationAdmin(admin.ModelAdmin):
    list_display = (
        'valuation_number',
        'project',
        'valuation_date',
        'work_completed_value',
        'amount_due',
        'status',
        'created_at'
    )
    list_filter = ('status', 'valuation_date', 'project')
    search_fields = ('valuation_number', 'project__name', 'project__code')
    readonly_fields = (
        'work_completed_value',
        'retention_amount',
        'previous_payments',
        'amount_due',
        'created_at',
        'updated_at'
    )
    fieldsets = (
        ('Basic Information', {
            'fields': (
                'project',
                'valuation_number',
                'valuation_date',
                'status'
            )
        }),
        ('Financial Details', {
            'fields': (
                'work_completed_value',
                'retention_percentage',
                'retention_amount',
                'previous_payments',
                'amount_due'
            )
        }),
        ('Approval Information', {
            'fields': (
                'submitted_by',
                'approved_by',
                'approved_date',
                'payment_date'
            )
        }),
        ('Additional Info', {
            'fields': (
                'notes',
                'created_at',
                'updated_at'
            )
        })
    )
    inlines = [BQItemProgressInline]
    date_hierarchy = 'valuation_date'


@admin.register(BQItemProgress)
class BQItemProgressAdmin(admin.ModelAdmin):
    list_display = (
        'valuation',
        'bq_item',
        'cumulative_quantity',
        'cumulative_value',
        'percentage_complete'
    )
    list_filter = ('valuation__project', 'valuation')
    search_fields = (
        'valuation__valuation_number',
        'bq_item__description'
    )
    readonly_fields = (
        'cumulative_quantity',
        'previous_value',
        'this_value',
        'cumulative_value',
        'percentage_complete',
        'created_at',
        'updated_at'
    )
