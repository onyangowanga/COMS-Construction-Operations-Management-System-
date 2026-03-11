"""
Django Admin configuration for Workers app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Worker, DailyLabourRecord


class DailyLabourRecordInline(admin.TabularInline):
    """Inline for daily labour records"""
    model = DailyLabourRecord
    extra = 0
    fields = ['project', 'date', 'hours_worked', 'daily_wage', 'paid', 'payment_date']
    autocomplete_fields = ['project']
    ordering = ['-date']


@admin.register(Worker)
class WorkerAdmin(admin.ModelAdmin):
    list_display = ['name', 'role', 'phone', 'id_number', 'wage_display', 'is_active', 'created_at']
    list_filter = ['role', 'is_active', 'created_at']
    search_fields = ['name', 'phone', 'id_number']
    autocomplete_fields = ['organization']
    ordering = ['name']
    inlines = [DailyLabourRecordInline]
    
    fieldsets = (
        (_('Worker Information'), {
            'fields': ('organization', 'name', 'role')
        }),
        (_('Contact & ID'), {
            'fields': ('phone', 'id_number')
        }),
        (_('Wages'), {
            'fields': ('default_daily_wage',)
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
    
    def wage_display(self, obj):
        if obj.default_daily_wage:
            return f"KES {obj.default_daily_wage:,.2f}/day"
        return "-"
    wage_display.short_description = _('Daily Wage')
    wage_display.admin_order_field = 'default_daily_wage'


@admin.register(DailyLabourRecord)
class DailyLabourRecordAdmin(admin.ModelAdmin):
    list_display = ['worker', 'project', 'date', 'hours_worked', 'wage_display', 'paid', 'payment_date']
    list_filter = ['paid', 'date', 'project']
    search_fields = ['worker__name', 'project__name', 'project__code', 'notes']
    autocomplete_fields = ['worker', 'project']
    date_hierarchy = 'date'
    ordering = ['-date']
    
    fieldsets = (
        (_('Record Information'), {
            'fields': ('worker', 'project', 'date')
        }),
        (_('Work Details'), {
            'fields': ('hours_worked', 'daily_wage')
        }),
        (_('Payment'), {
            'fields': ('paid', 'payment_date')
        }),
        (_('Notes'), {
            'fields': ('notes',)
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def wage_display(self, obj):
        return f"KES {obj.daily_wage:,.2f}"
    wage_display.short_description = _('Daily Wage')
    wage_display.admin_order_field = 'daily_wage'
