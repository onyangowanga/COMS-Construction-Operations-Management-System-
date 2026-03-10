"""
Worker Models for COMS
Handles casual labour management and daily manning records
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import Organization
from apps.projects.models import Project


class Worker(models.Model):
    """
    Casual labour workers employed on construction sites
    """
    
    class WorkerRole(models.TextChoices):
        MASON = 'MASON', _('Mason')
        CARPENTER = 'CARPENTER', _('Carpenter')
        ELECTRICIAN = 'ELECTRICIAN', _('Electrician')
        PLUMBER = 'PLUMBER', _('Plumber')
        PAINTER = 'PAINTER', _('Painter')
        WELDER = 'WELDER', _('Welder')
        LABOURER = 'LABOURER', _('General Labourer')
        STEEL_FIXER = 'STEEL_FIXER', _('Steel Fixer')
        TILE_SETTER = 'TILE_SETTER', _('Tile Setter')
        FOREMAN = 'FOREMAN', _('Foreman')
        OTHER = 'OTHER', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='workers'
    )
    name = models.CharField(max_length=200, help_text=_("Worker name"))
    phone = models.CharField(max_length=20, blank=True)
    id_number = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("National ID or identification number")
    )
    role = models.CharField(
        max_length=20,
        choices=WorkerRole.choices,
        default=WorkerRole.LABOURER
    )
    
    default_daily_wage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Standard daily wage for this worker")
    )
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'workers'
        verbose_name = _('Worker')
        verbose_name_plural = _('Workers')
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'role']),
            models.Index(fields=['name']),
            models.Index(fields=['is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"


class DailyLabourRecord(models.Model):
    """
    Daily manning records tracking casual labour work and payments
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='daily_labour_records'
    )
    worker = models.ForeignKey(
        Worker,
        on_delete=models.PROTECT,
        related_name='daily_records'
    )
    date = models.DateField(help_text=_("Work date"))
    daily_wage = models.DecimalField(
        max_digits=8,
        decimal_places=2,
        help_text=_("Amount paid for this day")
    )
    hours_worked = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        default=8.0,
        help_text=_("Hours worked")
    )
    paid = models.BooleanField(
        default=False,
        help_text=_("Whether payment has been made")
    )
    payment_date = models.DateField(null=True, blank=True)
    notes = models.TextField(blank=True, help_text=_("Work notes or comments"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_labour_records'
        verbose_name = _('Daily Labour Record')
        verbose_name_plural = _('Daily Labour Records')
        ordering = ['-date', 'project']
        unique_together = [['project', 'worker', 'date']]
        indexes = [
            models.Index(fields=['project', 'date']),
            models.Index(fields=['worker', 'date']),
            models.Index(fields=['paid']),
        ]
    
    def __str__(self):
        return f"{self.worker.name} - {self.project.code} - {self.date}"
