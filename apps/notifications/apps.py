"""
App configuration for Notification Engine
"""

from django.apps import AppConfig


class NotificationsConfig(AppConfig):
    """Configuration for the Notifications app"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.notifications'
    verbose_name = 'Notification Engine'
    
    def ready(self):
        """Import signal handlers when app is ready"""
        # Import signals here to avoid circular imports
        # from . import signals  # Uncomment when signals are implemented
        pass
