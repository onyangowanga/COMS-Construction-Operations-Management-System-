"""Reporting Engine Configuration"""

from django.apps import AppConfig


class ReportingConfig(AppConfig):
    """Configuration for the reporting engine module"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reporting'
    verbose_name = 'Reporting Engine'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.reporting.signals  # noqa
        except ImportError:
            pass
