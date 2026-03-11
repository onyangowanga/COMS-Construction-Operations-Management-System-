"""
Subcontractor Management - Admin Interface

Django admin configuration with:
- Status badges and visual indicators
- Advanced filters and search
- Inline editing for claims
- Bulk actions
"""

from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum, Count, Q
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import Subcontractor, SubcontractAgreement, SubcontractClaim


class SubcontractClaimInline(admin.TabularInline):
    """Inline display of claims within subcontract agreement"""
    model = SubcontractClaim
    extra = 0
    fields = (
        'claim_number', 'period_start', 'period_end',
        'claimed_amount', 'certified_amount', 'status', 'submitted_date'
    )
    readonly_fields = ('claim_number',)
    can_delete = False
    
    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Subcontractor)
class SubcontractorAdmin(admin.ModelAdmin):
    """
    Admin interface for Subcontractor model.
    
    Features:
    - Organization filtering
    - Specialization filtering
    - Active/inactive status badges
    - Contract count and value display
    - Search by name, contact, email
    """
    
    list_display = (
        'name', 'organization', 'specialization_badge',
        'contact_person', 'phone', 'email',
        'active_status', 'contracts_count', 'total_value',
        'created_at'
    )
    
    list_filter = (
        'is_active', 'specialization', 'organization',
        'created_at'
    )
    
    search_fields = (
        'name', 'company_registration', 'contact_person',
        'email', 'phone', 'specialization'
    )
    
    readonly_fields = ('id', 'created_at', 'updated_at', 'created_by')
    
    fieldsets = (
        ('Company Information', {
            'fields': (
                'organization', 'name', 'company_registration',
                'tax_number', 'specialization'
            )
        }),
        ('Contact Details', {
            'fields': (
                'contact_person', 'phone', 'email', 'address'
            )
        }),
        ('Status', {
            'fields': ('is_active', 'notes')
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by on creation"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    @admin.display(description='Active', boolean=True)
    def active_status(self, obj):
        """Display active status as boolean icon"""
        return obj.is_active
    
    @admin.display(description='Specialization')
    def specialization_badge(self, obj):
        """Display specialization with colored badge"""
        if not obj.specialization:
            return '-'
        
        colors = {
            'Mechanical': '#3498db',
            'Electrical': '#f39c12',
            'Civil': '#95a5a6',
            'Plumbing': '#1abc9c',
            'HVAC': '#9b59b6',
        }
        
        color = colors.get(obj.specialization, '#34495e')
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 3px 10px; border-radius: 3px; font-size: 11px;">{}</span>',
            color,
            obj.specialization
        )
    
    @admin.display(description='Contracts')
    def contracts_count(self, obj):
        """Display number of active contracts"""
        count = SubcontractAgreement.objects.filter(
            subcontractor=obj,
            status=SubcontractAgreement.Status.ACTIVE
        ).count()
        
        if count > 0:
            return format_html(
                '<strong style="color: #27ae60;">{}</strong>',
                count
            )
        return count
    
    @admin.display(description='Total Value')
    def total_value(self, obj):
        """Display total value of active contracts"""
        total = SubcontractAgreement.objects.filter(
            subcontractor=obj,
            status=SubcontractAgreement.Status.ACTIVE
        ).aggregate(total=Sum('contract_value'))['total']
        
        if total:
            return format_html(
                '<span style="color: #27ae60;">£{:,.2f}</span>',
                total
            )
        return '£0.00'


@admin.register(SubcontractAgreement)
class SubcontractAgreementAdmin(admin.ModelAdmin):
    """
    Admin interface for SubcontractAgreement model.
    
    Features:
    - Status badges with color coding
    - Project and subcontractor filtering
    - Contract value and completion display
    - Inline claims management
    - Bulk activation action
    """
    
    list_display = (
        'contract_reference', 'project', 'subcontractor_link',
        'contract_value', 'status_badge', 'start_date', 'end_date',
        'completion_display', 'total_certified', 'created_at'
    )
    
    list_filter = (
        'status', 'project__organization', 'project',
        'vat_applicable', 'performance_bond_required',
        'created_at', 'start_date'
    )
    
    search_fields = (
        'contract_reference', 'scope_of_work',
        'subcontractor__name', 'project__name'
    )
    
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'created_by',
        'activated_at', 'completed_at', 'duration_display',
        'retention_display', 'payment_summary_display'
    )
    
    autocomplete_fields = ['project', 'subcontractor']
    
    inlines = [SubcontractClaimInline]
    
    fieldsets = (
        ('Contract Details', {
            'fields': (
                'project', 'subcontractor', 'contract_reference',
                'scope_of_work', 'status'
            )
        }),
        ('Financial Terms', {
            'fields': (
                'contract_value', 'retention_percentage',
                'vat_applicable', 'payment_terms'
            )
        }),
        ('Performance Bond', {
            'fields': (
                'performance_bond_required',
                'performance_bond_percentage'
            ),
            'classes': ('collapse',)
        }),
        ('Timeline', {
            'fields': (
                'start_date', 'end_date', 'duration_display',
                'activated_at', 'completed_at'
            )
        }),
        ('Payment Summary', {
            'fields': ('payment_summary_display',),
            'classes': ('wide',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['activate_subcontracts', 'export_to_csv']
    
    def save_model(self, request, obj, form, change):
        """Set created_by on creation"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        """Display status with colored badge"""
        colors = {
            SubcontractAgreement.Status.DRAFT: '#95a5a6',
            SubcontractAgreement.Status.ACTIVE: '#27ae60',
            SubcontractAgreement.Status.COMPLETED: '#3498db',
            SubcontractAgreement.Status.TERMINATED: '#e74c3c',
        }
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 12px; border-radius: 4px; font-weight: bold; '
            'font-size: 11px;">{}</span>',
            colors.get(obj.status, '#34495e'),
            obj.get_status_display()
        )
    
    @admin.display(description='Subcontractor')
    def subcontractor_link(self, obj):
        """Display subcontractor with link"""
        url = reverse('admin:subcontracts_subcontractor_change', args=[obj.subcontractor.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.subcontractor.name
        )
    
    @admin.display(description='Completion')
    def completion_display(self, obj):
        """Display completion percentage with progress bar"""
        percentage = obj.completion_percentage
        
        if percentage >= 100:
            color = '#27ae60'
        elif percentage >= 75:
            color = '#3498db'
        elif percentage >= 50:
            color = '#f39c12'
        else:
            color = '#e74c3c'
        
        return format_html(
            '<div style="width: 100px; background-color: #ecf0f1; '
            'border-radius: 10px; height: 18px; position: relative;">'
            '<div style="width: {}%; background-color: {}; '
            'border-radius: 10px; height: 100%; display: flex; '
            'align-items: center; justify-content: center;">'
            '<span style="font-size: 10px; font-weight: bold; color: white;">'
            '{:.0f}%</span></div></div>',
            percentage, color, percentage
        )
    
    @admin.display(description='Total Certified')
    def total_certified(self, obj):
        """Display total certified amount"""
        return format_html(
            '<span style="color: #27ae60; font-weight: bold;">£{:,.2f}</span>',
            obj.total_certified
        )
    
    @admin.display(description='Duration')
    def duration_display(self, obj):
        """Display contract duration in days"""
        if obj.duration_days:
            return f'{obj.duration_days} days'
        return '-'
    
    @admin.display(description='Retention Amount')
    def retention_display(self, obj):
        """Display retention amount"""
        if obj.retention_amount:
            return f'£{obj.retention_amount:,.2f}'
        return '£0.00'
    
    @admin.display(description='Payment Summary')
    def payment_summary_display(self, obj):
        """Display comprehensive payment summary"""
        html = f'''
        <table style="width: 100%; border-collapse: collapse;">
            <tr>
                <td style="padding: 5px;"><strong>Contract Value:</strong></td>
                <td style="padding: 5px; text-align: right;">£{obj.contract_value:,.2f}</td>
                <td style="padding: 5px;"><strong>Total Claimed:</strong></td>
                <td style="padding: 5px; text-align: right;">£{obj.total_claimed:,.2f}</td>
            </tr>
            <tr>
                <td style="padding: 5px;"><strong>Total Certified:</strong></td>
                <td style="padding: 5px; text-align: right; color: #27ae60;">
                    <strong>£{obj.total_certified:,.2f}</strong>
                </td>
                <td style="padding: 5px;"><strong>Total Paid:</strong></td>
                <td style="padding: 5px; text-align: right; color: #3498db;">
                    £{obj.total_paid:,.2f}
                </td>
            </tr>
            <tr>
                <td style="padding: 5px;"><strong>Outstanding:</strong></td>
                <td style="padding: 5px; text-align: right; color: #e67e22;">
                    £{obj.outstanding_balance:,.2f}
                </td>
                <td style="padding: 5px;"><strong>Completion:</strong></td>
                <td style="padding: 5px; text-align: right;">
                    {obj.completion_percentage:.1f}%
                </td>
            </tr>
        </table>
        '''
        return mark_safe(html)
    
    @admin.action(description='Activate selected subcontracts')
    def activate_subcontracts(self, request, queryset):
        """Bulk activate draft subcontracts"""
        from .services import SubcontractService
        
        activated = 0
        for subcontract in queryset.filter(status=SubcontractAgreement.Status.DRAFT):
            try:
                SubcontractService.activate_subcontract(
                    subcontract=subcontract,
                    activated_by=request.user
                )
                activated += 1
            except Exception:
                pass
        
        self.message_user(
            request,
            f'Successfully activated {activated} subcontract(s).'
        )


@admin.register(SubcontractClaim)
class SubcontractClaimAdmin(admin.ModelAdmin):
    """
    Admin interface for SubcontractClaim model.
    
    Features:
    - Status badges with workflow visualization
    - Financial calculations display
    - Filters by status, date, project
    - Bulk certification actions
    """
    
    list_display = (
        'claim_number', 'subcontract_link', 'period_display',
        'claimed_amount_display', 'certified_amount_display',
        'status_badge', 'submission_date_display',
        'processing_time_display'
    )
    
    list_filter = (
        'status', 'subcontract__project__organization',
        'subcontract__project', 'submitted_date',
        'certified_date', 'paid_date'
    )
    
    search_fields = (
        'claim_number', 'description',
        'subcontract__contract_reference',
        'subcontract__subcontractor__name'
    )
    
    readonly_fields = (
        'id', 'created_at', 'updated_at', 'created_by',
        'submitted_date', 'certified_date', 'paid_date',
        'submitted_by', 'certified_by',
        'cumulative_display', 'net_payment_display',
        'variance_display', 'processing_time_display'
    )
    
    autocomplete_fields = ['subcontract']
    
    fieldsets = (
        ('Claim Details', {
            'fields': (
                'subcontract', 'claim_number', 'status',
                'period_start', 'period_end', 'description'
            )
        }),
        ('Financial Details', {
            'fields': (
                'previous_cumulative_amount', 'claimed_amount',
                'certified_amount', 'retention_amount',
                'cumulative_display', 'net_payment_display',
                'variance_display'
            )
        }),
        ('Workflow Tracking', {
            'fields': (
                'submitted_by', 'submitted_date',
                'certified_by', 'certified_date',
                'paid_date', 'processing_time_display'
            )
        }),
        ('Rejection Details', {
            'fields': ('rejection_reason',),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes',),
            'classes': ('collapse',)
        }),
        ('Metadata', {
            'fields': ('id', 'created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """Set created_by on creation"""
        if not change:
            obj.created_by = request.user
        super().save_model(request, obj, form, change)
    
    @admin.display(description='Status')
    def status_badge(self, obj):
        """Display status with colored badge and icon"""
        configs = {
            SubcontractClaim.Status.DRAFT: ('#95a5a6', '📝'),
            SubcontractClaim.Status.SUBMITTED: ('#3498db', '📤'),
            SubcontractClaim.Status.CERTIFIED: ('#27ae60', '✅'),
            SubcontractClaim.Status.REJECTED: ('#e74c3c', '❌'),
            SubcontractClaim.Status.PAID: ('#9b59b6', '💰'),
        }
        
        color, icon = configs.get(obj.status, ('#34495e', '•'))
        
        return format_html(
            '<span style="background-color: {}; color: white; '
            'padding: 4px 12px; border-radius: 4px; font-weight: bold; '
            'font-size: 11px;">{} {}</span>',
            color, icon, obj.get_status_display()
        )
    
    @admin.display(description='Subcontract')
    def subcontract_link(self, obj):
        """Display subcontract with link"""
        url = reverse('admin:subcontracts_subcontractagreement_change', 
                     args=[obj.subcontract.id])
        return format_html(
            '<a href="{}">{}</a>',
            url,
            obj.subcontract.contract_reference
        )
    
    @admin.display(description='Period')
    def period_display(self, obj):
        """Display claim period"""
        return f'{obj.period_start} to {obj.period_end}'
    
    @admin.display(description='Claimed')
    def claimed_amount_display(self, obj):
        """Display claimed amount"""
        return format_html(
            '<span style="color: #3498db; font-weight: bold;">£{:,.2f}</span>',
            obj.claimed_amount
        )
    
    @admin.display(description='Certified')
    def certified_amount_display(self, obj):
        """Display certified amount"""
        if obj.certified_amount:
            return format_html(
                '<span style="color: #27ae60; font-weight: bold;">£{:,.2f}</span>',
                obj.certified_amount
            )
        return '-'
    
    @admin.display(description='Submitted')
    def submission_date_display(self, obj):
        """Display submission date"""
        if obj.submitted_date:
            return obj.submitted_date.strftime('%d %b %Y')
        return '-'
    
    @admin.display(description='Cumulative Certified')
    def cumulative_display(self, obj):
        """Display cumulative certified amount"""
        if obj.cumulative_certified_amount:
            return f'£{obj.cumulative_certified_amount:,.2f}'
        return '£0.00'
    
    @admin.display(description='Net Payment')
    def net_payment_display(self, obj):
        """Display net payment after retention"""
        if obj.net_payment_amount:
            return f'£{obj.net_payment_amount:,.2f}'
        return '£0.00'
    
    @admin.display(description='Variance')
    def variance_display(self, obj):
        """Display variance between claimed and certified"""
        variance = obj.variance_amount
        if variance is None:
            return '-'
        
        color = '#e74c3c' if variance < 0 else '#27ae60'
        
        return format_html(
            '<span style="color: {}; font-weight: bold;">£{:,.2f}</span>',
            color, variance
        )
    
    @admin.display(description='Processing Time')
    def processing_time_display(self, obj):
        """Display processing time"""
        days = obj.processing_time_days
        if days is not None:
            if days > 14:
                color = '#e74c3c'
            elif days > 7:
                color = '#f39c12'
            else:
                color = '#27ae60'
            
            return format_html(
                '<span style="color: {}; font-weight: bold;">{} days</span>',
                color, days
            )
        return '-'
