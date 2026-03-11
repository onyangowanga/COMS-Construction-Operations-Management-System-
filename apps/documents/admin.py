"""
Django Admin configuration for Documents app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Document, DocumentVersion


class DocumentVersionInline(admin.TabularInline):
    """Inline for document versions"""
    model = DocumentVersion
    extra = 0
    fields = ['version_number', 'file_path', 'is_latest', 'description', 'uploaded_at']
    readonly_fields = ['uploaded_at']
    ordering = ['-version_number']


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    list_display = ['name', 'project', 'document_type', 'version_count', 'uploaded_by', 'created_at']
    list_filter = ['document_type', 'created_at']
    search_fields = ['name', 'project__name', 'project__code', 'description']
    autocomplete_fields = ['project', 'uploaded_by']
    date_hierarchy = 'created_at'
    ordering = ['-created_at']
    inlines = [DocumentVersionInline]
    
    fieldsets = (
        (_('Document Information'), {
            'fields': ('project', 'name', 'document_type')
        }),
        (_('Upload Details'), {
            'fields': ('uploaded_by', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def version_count(self, obj):
        return obj.versions.count()
    version_count.short_description = _('Versions')


@admin.register(DocumentVersion)
class DocumentVersionAdmin(admin.ModelAdmin):
    list_display = ['document', 'version_number', 'is_latest', 'file_path', 'uploaded_at']
    list_filter = ['is_latest', 'uploaded_at']
    search_fields = ['document__name', 'description', 'file_path']
    autocomplete_fields = ['document']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']
    
    fieldsets = (
        (_('Version Information'), {
            'fields': ('document', 'version_number', 'is_latest')
        }),
        (_('File'), {
            'fields': ('file_path', 'description')
        }),
        (_('Timestamps'), {
            'fields': ('uploaded_at',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['uploaded_at']
