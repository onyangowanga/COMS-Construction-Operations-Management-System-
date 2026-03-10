"""
Projects Models for COMS
Handles project management, budgets, and milestones
"""
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _


class Project(models.Model):
    """
    Main Project model - will be fully implemented in Phase 2
    Basic structure for Phase 1 authentication relationships
    """
    
    class Status(models.TextChoices):
        PLANNING = 'PLANNING', _('Planning')
        IN_PROGRESS = 'IN_PROGRESS', _('In Progress')
        ON_HOLD = 'ON_HOLD', _('On Hold')
        COMPLETED = 'COMPLETED', _('Completed')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    name = models.CharField(max_length=200, help_text=_("Project name"))
    code = models.CharField(max_length=50, unique=True, help_text=_("Unique project code"))
    description = models.TextField(blank=True, help_text=_("Project description"))
    
    contractor = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='owned_projects',
        help_text=_("Project owner/contractor")
    )
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PLANNING
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['code']),
            models.Index(fields=['contractor', 'status']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"

