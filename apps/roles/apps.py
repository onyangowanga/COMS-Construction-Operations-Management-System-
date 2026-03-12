"""
Role-Based Access Control App Configuration
"""

from django.apps import AppConfig


class RolesConfig(AppConfig):
    """Configuration for the Roles and Permissions app"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.roles'
    verbose_name = 'Role-Based Access Control'
    
    def ready(self):
        """Initialize app when Django starts"""
        # Import signal handlers if needed
        pass
