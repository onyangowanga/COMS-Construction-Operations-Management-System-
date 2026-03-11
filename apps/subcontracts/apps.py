"""
App configuration for Subcontractor Management Module
"""

from django.apps import AppConfig


class SubcontractsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.subcontracts'
    verbose_name = 'Subcontractor Management'
