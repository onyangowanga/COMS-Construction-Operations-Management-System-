"""
Variation Order Admin Interface
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum
from apps.variations.models import VariationOrder


@admin.register(VariationOrder)
class VariationOrderAdmin(admin.ModelAdmin):
    """Admin interface for variation orders"""
    
    list_display = [
        'reference_number',
        'project_name',
        'title',
        'variation_type_badge',
        'status_badge',
        'estimated_value_display',
        'approved_value_display',
        'certified_amount_display',
        'instruction_date',
        'priority_badge',
    ]
    
    list_filter = [
        'status',
        'priority',
        'change_type',
        'variation_type',
        'instruction_date',
        'project',
    ]
    
    search_fields = [
        'reference_number',
        'title',
        'description',
        'project__name',
        'project__project_code',
        'client_reference',
    ]
    
    readonly_fields = [
        'created_at',
        'updated_at',
        'submitted_date',
        'approved_date',
        'certified_date',
        'value_variance_display',
        'outstanding_amount_display',
        'certification_variance_display',
    ]
    
    fieldsets = (
        ('Identification', {
            'fields': (
                'project',
                'reference_number',
                'variation_type',
                'title',
                'change_type',
                'priority',
            )
        }),
        ('Description', {
            'fields': (
                'description',
                'justification',
                'technical_notes',
                'impact_on_schedule',
            )
        }),
        ('Dates', {
            'fields': (
                'instruction_date',
                'required_by_date',
                'submitted_date',
                'certified_date',
            )
        }),
        ('Financial', {
            'fields': (
                'estimated_value',
                'approved_value',
                'certified_amount',
                'invoiced_value',
                'paid_value',
                'value_variance_display',
                'certification_variance_display',
                'outstanding_amount_display',
            )
        }),
        ('Workflow', {
            'fields': (
                'status',
                'rejection_reason',
            )
        }),
        ('Responsible Parties', {
            'fields': (
                'created_by',
                'submitted_by',
                'approved_by',
                'certified_by',
            )
        }),
        ('References', {
            'fields': (
                'client_reference',
            ),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': (
                'created_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    actions = [
        'mark_as_submitted',
        'mark_as_approved',
        'export_to_csv',
    ]
    
    def project_name(self, obj):
        """Display project name"""
        return obj.project.name
    project_name.short_description = 'Project'
    
    def status_badge(self, obj):
        """Display status as colored badge"""
        colors = {
            'DRAFT': 'gray',
            'SUBMITTED': 'blue',
            'APPROVED': 'green',
            'REJECTED': 'red',
            'INVOICED': 'purple',
            'PAID': 'darkgreen',
        }
        color = colors.get(obj.status, 'gray')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def priority_badge(self, obj):
        """Display priority as colored badge"""
        colors = {
            'LOW': '#95a5a6',
            'MEDIUM': '#f39c12',
            'HIGH': '#e67e22',
            'URGENT': '#e74c3c',
        }
        color = colors.get(obj.priority, '#95a5a6')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.85em;">{}</span>',
            color,
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Priority'
    
    def estimated_value_display(self, obj):
        """Display estimated value"""
        return f"KES {obj.estimated_value:,.2f}"
    estimated_value_display.short_description = 'Estimated'
    
    def approved_value_display(self, obj):
        """Display approved value"""
        if obj.approved_value > 0:
            return format_html(
                '<strong>KES {:,.2f}</strong>',
                obj.approved_value
            )
        return '-'
    approved_value_display.short_description = 'Approved'
    
    def certified_amount_display(self, obj):
        """Display certified amount"""
        if obj.certified_amount and obj.certified_amount > 0:
            return format_html(
                '<strong style="color: #2980b9;">KES {:,.2f}</strong>',
                obj.certified_amount
            )
        return '-'
    certified_amount_display.short_description = 'Certified'
    
    def variation_type_badge(self, obj):
        """Display variation type as colored badge"""
        colors = {
            'CLIENT_INSTRUCTION': '#3498db',
            'DESIGN_CHANGE': '#9b59b6',
            'ADDITIONAL_WORK': '#27ae60',
            'OMISSION': '#e67e22',
            'ERROR_CORRECTION': '#e74c3c',
            'UNFORESEEN_CONDITION': '#f39c12',
        }
        color = colors.get(obj.variation_type, '#95a5a6')
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.75em;">{}</span>',
            color,
            obj.get_variation_type_display()
        )
    variation_type_badge.short_description = 'Type'
    
    def value_variance_display(self, obj):
        """Display variance between estimated and approved"""
        variance = obj.value_variance
        if variance != 0:
            color = 'red' if variance > 0 else 'green'
            return format_html(
                '<span style="color: {};">KES {:,.2f}</span>',
                color,
                variance
            )
        return 'KES 0.00'
    value_variance_display.short_description = 'Variance'
    
    def certification_variance_display(self, obj):
        """Display variance between certified and approved"""
        variance = obj.certification_variance
        if variance != 0:
            color = 'red' if variance > 0 else 'green'
            return format_html(
                '<span style="color: {};">KES {:,.2f}</span>',
                color,
                variance
            )
        return 'KES 0.00'
    certification_variance_display.short_description = 'Certification Variance'
    
    def outstanding_amount_display(self, obj):
        """Display outstanding amount"""
        outstanding = obj.outstanding_amount
        if outstanding > 0:
            return format_html(
                '<strong style="color: #e67e22;">KES {:,.2f}</strong>',
                outstanding
            )
        return 'KES 0.00'
    outstanding_amount_display.short_description = 'Outstanding'
    
    def mark_as_submitted(self, request, queryset):
        """Bulk action: Mark variations as submitted"""
        updated = queryset.filter(
            status=VariationOrder.Status.DRAFT
        ).update(
            status=VariationOrder.Status.SUBMITTED,
            submitted_by=request.user
        )
        self.message_user(
            request,
            f'{updated} variation(s) marked as submitted.'
        )
    mark_as_submitted.short_description = 'Mark as Submitted'
    
    def mark_as_approved(self, request, queryset):
        """Bulk action: Approve variations"""
        from apps.variations.services import VariationService
        
        approved_count = 0
        for variation in queryset.filter(status=VariationOrder.Status.SUBMITTED):
            try:
                VariationService.approve_variation(
                    variation_id=str(variation.id),
                    approved_by=request.user,
                    approved_value=variation.estimated_value
                )
                approved_count += 1
            except Exception as e:
                self.message_user(
                    request,
                    f'Error approving {variation.reference_number}: {e}',
                    level='error'
                )
        
        self.message_user(
            request,
            f'{approved_count} variation(s) approved successfully.'
        )
    mark_as_approved.short_description = 'Approve Variations'
    
    def export_to_csv(self, request, queryset):
        """Export variations to CSV"""
        import csv
        from django.http import HttpResponse
        
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="variations.csv"'
        
        writer = csv.writer(response)
        writer.writerow([
            'Reference',
            'Project',
            'Title',
            'Status',
            'Priority',
            'Type',
            'Estimated Value',
            'Approved Value',
            'Instruction Date',
        ])
        
        for vo in queryset:
            writer.writerow([
                vo.reference_number,
                vo.project.name,
                vo.title,
                vo.get_status_display(),
                vo.get_priority_display(),
                vo.get_change_type_display(),
                vo.estimated_value,
                vo.approved_value,
                vo.instruction_date,
            ])
        
        return response
    export_to_csv.short_description = 'Export to CSV'
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        qs = super().get_queryset(request)
        return qs.select_related(
            'project',
            'project__organization',
            'created_by',
            'submitted_by',
            'approved_by',
        )
