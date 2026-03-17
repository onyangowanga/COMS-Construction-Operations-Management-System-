"""
Projects Models for COMS
Handles project management, budgets, and milestones
"""
import uuid
from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Organization


class Project(models.Model):
    """
    Main Project model representing construction projects
    """
    
    class ProjectType(models.TextChoices):
        NEW_CONSTRUCTION = 'NEW_CONSTRUCTION', _('New Construction')
        RENOVATION = 'RENOVATION', _('Renovation')
    
    class ContractType(models.TextChoices):
        LABOUR_ONLY = 'LABOUR_ONLY', _('Labour Only Contract')
        FULL_CONTRACT = 'FULL_CONTRACT', _('Full Contract')
    
    class Status(models.TextChoices):
        DESIGN = 'DESIGN', _('Design')
        APPROVAL = 'APPROVAL', _('Approval')
        IMPLEMENTATION = 'IMPLEMENTATION', _('Implementation')
        COMPLETED = 'COMPLETED', _('Completed')
        ON_HOLD = 'ON_HOLD', _('On Hold')
        CANCELLED = 'CANCELLED', _('Cancelled')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.PROTECT,
        related_name='projects',
        null=True,
        blank=True,
        help_text=_("Organization owning this project")
    )
    name = models.CharField(max_length=200, help_text=_("Project name"))
    code = models.CharField(max_length=50, help_text=_("Unique project code"))
    year = models.IntegerField(help_text=_("Year component used for code generation"))
    sequence = models.IntegerField(help_text=_("Sequence component used for code generation"))
    client_name = models.CharField(max_length=200, blank=True, help_text=_("Client name"))
    location = models.TextField(blank=True, help_text=_("Project location"))
    
    project_type = models.CharField(
        max_length=20,
        choices=ProjectType.choices,
        default=ProjectType.NEW_CONSTRUCTION
    )
    contract_type = models.CharField(
        max_length=20,
        choices=ContractType.choices,
        default=ContractType.FULL_CONTRACT
    )
    
    project_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Total project contract value")
    )
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DESIGN
    )
    
    description = models.TextField(blank=True, help_text=_("Project description"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'projects'
        verbose_name = _('Project')
        verbose_name_plural = _('Projects')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['code']),
            models.Index(fields=['organization', 'year', 'sequence']),
            models.Index(fields=['client_name']),
        ]
        unique_together = [['organization', 'code']]
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'year', 'sequence'],
                name='unique_project_sequence_per_org_year',
            )
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"


class ProjectStage(models.Model):
    """
    Construction implementation stages
    """
    
    class StageName(models.TextChoices):
        PRELIMINARY = 'PRELIMINARY', _('Preliminary Works')
        SHELL = 'SHELL', _('Shell')
        FINISHES = 'FINISHES', _('Finishes')
        EXTERNAL_WORKS = 'EXTERNAL_WORKS', _('External Works')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='stages'
    )
    name = models.CharField(
        max_length=30,
        choices=StageName.choices
    )
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(help_text=_("Stage sequence order"))
    
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    is_completed = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_stages'
        verbose_name = _('Project Stage')
        verbose_name_plural = _('Project Stages')
        ordering = ['project', 'order']
        unique_together = [['project', 'name']]
        indexes = [
            models.Index(fields=['project', 'order']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.get_name_display()}"

