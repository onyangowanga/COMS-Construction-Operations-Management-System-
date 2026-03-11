from django.apps import AppConfig


class VariationsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.variations'
    verbose_name = 'Variation Orders'
    
    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.variations.signals  # noqa
        except ImportError:
            pass
