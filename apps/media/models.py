"""
Media Models for COMS
Manages project progress photos
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import User
from apps.projects.models import Project, ProjectStage


class ProjectPhoto(models.Model):
    """
    Progress photos for construction projects
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='photos'
    )
    stage = models.ForeignKey(
        ProjectStage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='photos',
        help_text=_("Associated construction stage")
    )
    image_path = models.CharField(
        max_length=500,
        help_text=_("Path to image file")
    )
    description = models.TextField(blank=True)
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_photos'
    )
    
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_photos'
        verbose_name = _('Project Photo')
        verbose_name_plural = _('Project Photos')
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', 'uploaded_at']),
            models.Index(fields=['stage']),
        ]
    
    def __str__(self):
        stage_name = self.stage.name if self.stage else "General"
        return f"{self.project.code} - {stage_name} - {self.uploaded_at.date()}"
