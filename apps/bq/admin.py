"""
Django Admin configuration for Bill of Quantities (BQ) app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import BQSection, BQElement, BQItem


class BQItemInline(admin.TabularInline):
    """Inline for BQ Items under Elements"""
    model = BQItem
    extra = 0
    fields = ['description', 'quantity', 'unit', 'rate', 'total_display']
    readonly_fields = ['total_display']
    ordering = ['id']
    
    def total_display(self, obj):
        """Display calculated total"""
        if obj.pk:
            return f"KES {obj.total_amount:,.2f}"
        return "-"
    total_display.short_description = _('Total')


class BQElementInline(admin.TabularInline):
    """Inline for BQ Elements under Sections"""
    model = BQElement
    extra = 0
    fields = ['name', 'order', 'total_display']
    readonly_fields = ['total_display']
    ordering = ['order']
    show_change_link = True
    
    def total_display(self, obj):
        """Display element total"""
        if obj.pk:
            return f"KES {obj.total_amount:,.2f}"
        return "-"
    total_display.short_description = _('Total')


@admin.register(BQSection)
class BQSectionAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'order', 'element_count', 'total_display', 'created_at']
    list_filter = ['project', 'created_at']
    search_fields = ['name', 'project__name', 'project__code', 'description']
    autocomplete_fields = ['project']
    ordering = ['project', 'order']
    inlines = [BQElementInline]
    
    fieldsets = (
        (_('Section Information'), {
            'fields': ('project', 'name', 'order', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def element_count(self, obj):
        """Display number of elements"""
        return obj.elements.count()
    element_count.short_description = _('Elements')
    
    def total_display(self, obj):
        """Display section total"""
        total = obj.total_amount
        return format_html('<strong>KES {:,.2f}</strong>', total)
    total_display.short_description = _('Total Amount')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('project').prefetch_related('elements')


@admin.register(BQElement)
class BQElementAdmin(admin.ModelAdmin):
    list_display = ['name', 'section', 'project_code', 'order', 'item_count', 'total_display']
    list_filter = ['section__project', 'created_at']
    search_fields = ['name', 'section__name', 'section__project__code', 'description']
    autocomplete_fields = ['section']
    ordering = ['section', 'order']
    inlines = [BQItemInline]
    
    fieldsets = (
        (_('Element Information'), {
            'fields': ('section', 'name', 'order', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def project_code(self, obj):
        """Display project code"""
        return obj.section.project.code
    project_code.short_description = _('Project')
    
    def item_count(self, obj):
        """Display number of items"""
        return obj.items.count()
    item_count.short_description = _('Items')
    
    def total_display(self, obj):
        """Display element total"""
        total = obj.total_amount
        return format_html('<strong>KES {:,.2f}</strong>', total)
    total_display.short_description = _('Total Amount')
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('section__project').prefetch_related('items')


@admin.register(BQItem)
class BQItemAdmin(admin.ModelAdmin):
    list_display = ['description', 'element', 'project_code', 'quantity', 'unit', 'rate', 'total_display']
    list_filter = ['element__section__project', 'unit']
    search_fields = ['description', 'element__name', 'element__section__project__code']
    autocomplete_fields = ['element']
    
    fieldsets = (
        (_('Item Information'), {
            'fields': ('element', 'description')
        }),
        (_('Quantities & Rates'), {
            'fields': ('quantity', 'unit', 'rate')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def project_code(self, obj):
        """Display project code"""
        return obj.element.section.project.code
    project_code.short_description = _('Project')
    
    def total_display(self, obj):
        """Display item total"""
        return format_html('<strong>KES {:,.2f}</strong>', obj.total_amount)
    total_display.short_description = _('Total')
    total_display.admin_order_field = 'rate'
    
    def get_queryset(self, request):
        """Optimize queryset"""
        qs = super().get_queryset(request)
        return qs.select_related('element__section__project')
