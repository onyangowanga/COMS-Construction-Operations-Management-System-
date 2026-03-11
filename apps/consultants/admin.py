"""
Django Admin configuration for Consultants app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Consultant, ProjectConsultant, ConsultantFee, ConsultantPayment


class ConsultantFeeInline(admin.TabularInline):
    """Inline for consultant fees"""
    model = ConsultantFee
    extra = 0
    fields = ['project', 'fee_type', 'contract_amount']
    autocomplete_fields = ['project']


class ConsultantPaymentInline(admin.TabularInline):
    """Inline for consultant payments"""
    model = ConsultantPayment
    extra = 0
    fields = ['amount', 'payment_date', 'payment_method', 'reference_number']


@admin.register(Consultant)
class ConsultantAdmin(admin.ModelAdmin):
    list_display = ['name', 'consultant_type', 'company', 'phone', 'email', 'is_active', 'created_at']
    list_filter = ['consultant_type', 'is_active', 'created_at']
    search_fields = ['name', 'company', 'phone', 'email']
    autocomplete_fields = ['organization']
    ordering = ['name']
    inlines = [ConsultantFeeInline]
    
    fieldsets = (
        (_('Consultant Information'), {
            'fields': ('organization', 'name', 'consultant_type', 'company')
        }),
        (_('Contact Details'), {
            'fields': ('phone', 'email', 'address')
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


@admin.register(ProjectConsultant)
class ProjectConsultantAdmin(admin.ModelAdmin):
    list_display = ['consultant', 'project', 'role', 'assigned_date']
    list_filter = ['assigned_date']
    search_fields = ['consultant__name', 'project__name', 'project__code', 'role']
    autocomplete_fields = ['project', 'consultant']
    date_hierarchy = 'assigned_date'


@admin.register(ConsultantFee)
class ConsultantFeeAdmin(admin.ModelAdmin):
    list_display = ['consultant', 'project', 'fee_type', 'contract_amount_display', 'created_at']
    list_filter = ['fee_type', 'created_at']
    search_fields = ['consultant__name', 'project__name', 'project__code']
    autocomplete_fields = ['consultant', 'project']
    date_hierarchy = 'created_at'
    inlines = [ConsultantPaymentInline]
    
    fieldsets = (
        (_('Fee Information'), {
            'fields': ('consultant', 'project', 'fee_type')
        }),
        (_('Amount & Schedule'), {
            'fields': ('contract_amount', 'payment_schedule')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def contract_amount_display(self, obj):
        return f"KES {obj.contract_amount:,.2f}"
    contract_amount_display.short_description = _('Contract Amount')
    contract_amount_display.admin_order_field = 'contract_amount'


@admin.register(ConsultantPayment)
class ConsultantPaymentAdmin(admin.ModelAdmin):
    list_display = ['consultant_fee', 'amount_display', 'payment_date', 'payment_method', 'reference_number']
    list_filter = ['payment_method', 'payment_date']
    search_fields = ['consultant_fee__consultant__name', 'reference_number', 'notes']
    autocomplete_fields = ['consultant_fee']
    date_hierarchy = 'payment_date'
    
    readonly_fields = ['created_at', 'updated_at']
    
    def amount_display(self, obj):
        return f"KES {obj.amount:,.2f}"
    amount_display.short_description = _('Amount')
    amount_display.admin_order_field = 'amount'
