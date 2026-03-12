"""
Event Logging App Configuration
"""

from django.apps import AppConfig


class EventsConfig(AppConfig):
    """Configuration for the Events app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.events'
    verbose_name = 'Event Logging'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import signal handlers if needed
        pass
