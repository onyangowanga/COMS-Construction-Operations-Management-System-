"""
Django Admin configuration for Media app
"""
from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import ProjectPhoto


@admin.register(ProjectPhoto)
class ProjectPhotoAdmin(admin.ModelAdmin):
    list_display = ['project', 'stage', 'image_thumbnail', 'uploaded_by', 'uploaded_at']
    list_filter = ['uploaded_at', 'project', 'stage']
    search_fields = ['project__name', 'project__code', 'description', 'stage__name']
    autocomplete_fields = ['project', 'stage', 'uploaded_by']
    date_hierarchy = 'uploaded_at'
    ordering = ['-uploaded_at']
    
    fieldsets = (
        (_('Photo Information'), {
            'fields': ('project', 'stage')
        }),
        (_('Image'), {
            'fields': ('image_path', 'description')
        }),
        (_('Upload Details'), {
            'fields': ('uploaded_by', 'uploaded_at'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['uploaded_at']
    
    def image_thumbnail(self, obj):
        """Display image thumbnail if path exists"""
        if obj.image_path:
            # This would need proper media URL setup
            return format_html(
                '<img src="{}" style="max-height: 50px; max-width: 100px;" />',
                obj.image_path
            )
        return "-"
    image_thumbnail.short_description = _('Preview')
