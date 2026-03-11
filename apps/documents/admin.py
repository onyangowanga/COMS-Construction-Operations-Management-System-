"""
Document Management System - Django Admin

Comprehensive admin interface for document management with:
- Advanced filtering and search
- Version history display
- File preview links
- Document type badges
- Size and extension display
- Confidential document marking
"""

from django.contrib import admin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from django.db.models import Count, Sum
from django.urls import reverse

from apps.documents.models import Document


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """
    Django admin for Document model.
    
    Features:
    - Color-coded document type badges
    - File size display in human-readable format
    - Version tracking
    - Confidential document highlighting
    - Advanced search and filters
    - Expiry date warnings
    """
    
    list_display = [
        'title',
        'document_type_badge',
        'project_link',
        'file_info',
        'version_display',
        'confidential_badge',
        'uploaded_by_name',
        'uploaded_at',
    ]
    
    list_filter = [
        'document_type',
        'is_latest',
        'is_confidential',
        'file_extension',
        'uploaded_at',
        'project',
        'organization',
    ]
    
    search_fields = [
        'title',
        'description',
        'tags',
        'reference_number',
        'file_name',
        'project__code',
        'project__name',
    ]
    
    autocomplete_fields = ['project', 'uploaded_by', 'previous_version']
    
    date_hierarchy = 'uploaded_at'
    
    ordering = ['-uploaded_at']
    
    list_per_page = 50
    
    fieldsets = (
        (_('Document Identification'), {
            'fields': (
                'title',
                'document_type',
                'reference_number',
                'description',
            )
        }),
        (_('Organization & Project'), {
            'fields': (
                'organization',
                'project',
            )
        }),
        (_('File'), {
            'fields': (
                'file',
                'file_size',
                'file_extension',
                'file_size_mb',
            )
        }),
        (_('Generic Relation'), {
            'fields': (
                'content_type',
                'object_id',
                'related_object_display',
            ),
            'classes': ('collapse',)
        }),
        (_('Versioning'), {
            'fields': (
                'version',
                'is_latest',
                'previous_version',
                'version_notes',
            )
        }),
        (_('Classification'), {
            'fields': (
                'tags',
                'is_confidential',
                'expiry_date',
            )
        }),
        (_('Metadata'), {
            'fields': (
                'uploaded_by',
                'uploaded_at',
                'updated_at',
            ),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = [
        'file_size',
        'file_extension',
        'file_size_mb',
        'uploaded_at',
        'updated_at',
        'related_object_display',
        'version',
    ]
    
    # === CUSTOM DISPLAY METHODS ===
    
    def document_type_badge(self, obj):
        """Display document type as colored badge"""
        colors = {
            'CONTRACT': '#2c3e50',
            'LPO_ATTACHMENT': '#3498db',
            'DELIVERY_NOTE': '#1abc9c',
            'SUPPLIER_INVOICE': '#e74c3c',
            'PAYMENT_VOUCHER': '#e67e22',
            'DRAWING': '#9b59b6',
            'BOQ': '#34495e',
            'SPECIFICATION': '#16a085',
            'METHOD_STATEMENT': '#27ae60',
            'SITE_PHOTO': '#f39c12',
            'SITE_REPORT_ATTACHMENT': '#d35400',
            'PROGRESS_REPORT': '#c0392b',
            'VARIATION_INSTRUCTION': '#8e44ad',
            'VALUATION_CERTIFICATE': '#2980b9',
            'RISK_ASSESSMENT': '#c0392b',
            'PERMIT': '#27ae60',
            'QUALITY_DOCUMENT': '#16a085',
            'SAFETY_DOCUMENT': '#e74c3c',
            'CORRESPONDENCE': '#95a5a6',
            'MEETING_MINUTES': '#7f8c8d',
            'OTHER': '#bdc3c7',
        }
        
        color = colors.get(obj.document_type, '#95a5a6')
        
        return format_html(
            '<span style="background: {}; color: white; padding: 3px 8px; '
            'border-radius: 3px; font-size: 0.75em; white-space: nowrap;">{}</span>',
            color,
            obj.get_document_type_display()
        )
    document_type_badge.short_description = _('Type')
    document_type_badge.admin_order_field = 'document_type'
    
    def project_link(self, obj):
        """Display project as clickable link"""
        if obj.project:
            url = reverse('admin:projects_project_change', args=[obj.project.id])
            return format_html(
                '<a href="{}">{}</a>',
                url,
                obj.project.code
            )
        return '-'
    project_link.short_description = _('Project')
    project_link.admin_order_field = 'project__code'
    
    def file_info(self, obj):
        """Display file name, type, and size"""
        if obj.file:
            icon_map = {
                'pdf': '📄',
                'doc': '📝',
                'docx': '📝',
                'xls': '📊',
                'xlsx': '📊',
                'jpg': '🖼️',
                'jpeg': '🖼️',
                'png': '🖼️',
                'dwg': '📐',
                'dxf': '📐',
                'zip': '📦',
            }
            
            icon = icon_map.get(obj.file_extension, '📎')
            
            return format_html(
                '{} <strong>{}</strong><br>'
                '<span style="color: #666; font-size: 0.85em;">'
                '{} &middot; {}'
                '</span>',
                icon,
                obj.file_name,
                obj.file_extension.upper(),
                obj.file_size_display
            )
        return '-'
    file_info.short_description = _('File')
    
    def version_display(self, obj):
        """Display version with badge"""
        if obj.version > 1:
            badge_color = '#3498db' if obj.is_latest else '#95a5a6'
            status = 'Latest' if obj.is_latest else 'Old'
            
            return format_html(
                '<span style="background: {}; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 0.75em;">v{} &middot; {}</span>',
                badge_color,
                obj.version,
                status
            )
        return format_html(
            '<span style="color: #95a5a6; font-size: 0.85em;">v1</span>'
        )
    version_display.short_description = _('Version')
    version_display.admin_order_field = 'version'
    
    def confidential_badge(self, obj):
        """Display confidential badge if applicable"""
        if obj.is_confidential:
            return format_html(
                '<span style="background: #e74c3c; color: white; padding: 2px 6px; '
                'border-radius: 3px; font-size: 0.75em;">🔒 CONFIDENTIAL</span>'
            )
        return ''
    confidential_badge.short_description = _('Status')
    confidential_badge.admin_order_field = 'is_confidential'
    
    def uploaded_by_name(self, obj):
        """Display uploader name"""
        if obj.uploaded_by:
            return obj.uploaded_by.get_full_name()
        return '-'
    uploaded_by_name.short_description = _('Uploaded By')
    uploaded_by_name.admin_order_field = 'uploaded_by__first_name'
    
    # === ADMIN ACTIONS ===
    
    @admin.action(description=_('Mark selected as confidential'))
    def mark_confidential(self, request, queryset):
        """Mark documents as confidential"""
        updated = queryset.update(is_confidential=True)
        self.message_user(
            request,
            _('%(count)d document(s) marked as confidential.') % {'count': updated}
        )
    
    @admin.action(description=_('Remove confidential marking'))
    def unmark_confidential(self, request, queryset):
        """Remove confidential marking"""
        updated = queryset.update(is_confidential=False)
        self.message_user(
            request,
            _('%(count)d document(s) unmarked as confidential.') % {'count': updated}
        )
    
    @admin.action(description=_('Mark as latest version'))
    def mark_as_latest(self, request, queryset):
        """Mark selected documents as latest version"""
        updated = queryset.update(is_latest=True)
        self.message_user(
            request,
            _('%(count)d document(s) marked as latest version.') % {'count': updated}
        )
    
    actions = [
        'mark_confidential',
        'unmark_confidential',
        'mark_as_latest',
    ]
    
    # === QUERYSET OPTIMIZATION ===
    
    def get_queryset(self, request):
        """Optimize queryset with select_related"""
        queryset = super().get_queryset(request)
        return queryset.select_related(
            'project',
            'organization',
            'uploaded_by',
            'content_type',
            'previous_version'
        )
    
    # === CUSTOM CHANGELIST VIEW ===
    
    def changelist_view(self, request, extra_context=None):
        """Add statistics to changelist"""
        extra_context = extra_context or {}
        
        # Calculate statistics
        queryset = self.get_queryset(request)
        
        # Apply filters if any
        from django.contrib.admin.views.main import ChangeList
        cl = ChangeList(
            request, self.model, self.list_display,
            self.list_display_links, self.list_filter,
            self.date_hierarchy, self.search_fields,
            self.list_select_related, self.list_per_page,
            self.list_max_show_all, self.list_editable, self
        )
        filtered_queryset = cl.get_queryset(request)
        
        stats = {
            'total_documents': filtered_queryset.count(),
            'total_size': sum(
                doc.file_size for doc in filtered_queryset if doc.file_size
            ),
            'confidential_count': filtered_queryset.filter(is_confidential=True).count(),
        }
        
        extra_context['stats'] = stats
        
        return super().changelist_view(request, extra_context)

