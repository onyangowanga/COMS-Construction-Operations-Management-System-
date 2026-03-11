"""
Portfolio Analytics Models for COMS
Manages project performance metrics, risk indicators, and earned value metrics
"""
import uuid
from decimal import Decimal
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.projects.models import Project


class ProjectMetrics(models.Model):
    """
    Stores computed metrics for project performance tracking
    Updated periodically (daily/weekly) or on-demand
    """
    
    class RiskLevel(models.TextChoices):
        LOW = 'LOW', _('Low Risk')
        MEDIUM = 'MEDIUM', _('Medium Risk')
        HIGH = 'HIGH', _('High Risk')
        CRITICAL = 'CRITICAL', _('Critical Risk')
    
    class ProjectHealth(models.TextChoices):
        EXCELLENT = 'EXCELLENT', _('Excellent')
        GOOD = 'GOOD', _('Good')
        WARNING = 'WARNING', _('Warning')
        CRITICAL = 'CRITICAL', _('Critical')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.OneToOneField(
        Project,
        on_delete=models.CASCADE,
        related_name='metrics'
    )
    
    # Financial Metrics
    total_contract_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total project contract value")
    )
    total_expenses = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total approved expenses to date")
    )
    total_revenue = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Total client payments received")
    )
    total_profit = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Revenue minus expenses")
    )
    
    # Performance Indicators
    budget_utilization = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(999.99)],
        help_text=_("Percentage of budget used (expenses / contract_value * 100)")
    )
    profit_margin = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(-999.99), MaxValueValidator(999.99)],
        help_text=_("Profit margin percentage (profit / revenue * 100)")
    )
    
    # Risk Assessment
    project_health = models.CharField(
        max_length=20,
        choices=ProjectHealth.choices,
        default=ProjectHealth.GOOD
    )
    risk_level = models.CharField(
        max_length=20,
        choices=RiskLevel.choices,
        default=RiskLevel.LOW
    )
    
    # Earned Value Management (EVM) Metrics
    planned_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("PV - Budgeted cost of work scheduled")
    )
    earned_value = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("EV - Budgeted cost of work performed (based on valuations)")
    )
    actual_cost = models.DecimalField(
        max_digits=15,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("AC - Actual expenses incurred")
    )
    
    # EVM Indices
    cost_performance_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text=_("CPI = EV / AC (>1 is good, <1 is over budget)")
    )
    schedule_performance_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('1.00'),
        help_text=_("SPI = EV / PV (>1 is ahead, <1 is behind schedule)")
    )
    
    # Schedule Metrics
    days_elapsed = models.IntegerField(
        default=0,
        help_text=_("Days since project start")
    )
    days_remaining = models.IntegerField(
        default=0,
        help_text=_("Days until project end date")
    )
    schedule_variance_days = models.IntegerField(
        default=0,
        help_text=_("Schedule variance in days (negative = behind)")
    )
    
    # Flags
    is_over_budget = models.BooleanField(
        default=False,
        help_text=_("True if expenses exceed contract value")
    )
    is_behind_schedule = models.BooleanField(
        default=False,
        help_text=_("True if SPI < 1.0")
    )
    
    # Metadata
    last_updated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'project_metrics'
        verbose_name = _('Project Metrics')
        verbose_name_plural = _('Project Metrics')
        ordering = ['-last_updated']
        indexes = [
            models.Index(fields=['project', 'last_updated']),
            models.Index(fields=['risk_level']),
            models.Index(fields=['project_health']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - Metrics (Updated: {self.last_updated.strftime('%Y-%m-%d')})"
