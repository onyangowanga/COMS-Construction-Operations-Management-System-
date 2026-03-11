"""
Reporting Engine - Models

Database models for report configuration, scheduling, and history.
"""

import uuid
import json
from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.contrib.postgres.fields import ArrayField

from apps.authentication.models import User, Organization
from apps.projects.models import Project


class Report(models.Model):
    """
    Report configuration and metadata.
    
    Stores report definitions, parameters, and settings for
    reusable report templates.
    """
    
    class ReportType(models.TextChoices):
        """Available report types"""
        PROJECT_FINANCIAL = 'PROJECT_FINANCIAL', _('Project Financial Summary')
        CASH_FLOW = 'CASH_FLOW', _('Cash Flow Forecast Report')
        VARIATION_IMPACT = 'VARIATION_IMPACT', _('Variation Impact Report')
        SUBCONTRACTOR_PAYMENT = 'SUBCONTRACTOR_PAYMENT', _('Subcontractor Payment Report')
        DOCUMENT_AUDIT = 'DOCUMENT_AUDIT', _('Document Audit Report')
        PROCUREMENT_SUMMARY = 'PROCUREMENT_SUMMARY', _('Procurement Summary')
        CUSTOM = 'CUSTOM', _('Custom Report')
    
    class ExportFormat(models.TextChoices):
        """Supported export formats"""
        PDF = 'PDF', _('PDF Document')
        EXCEL = 'EXCEL', _('Excel Spreadsheet')
        CSV = 'CSV', _('CSV File')
        JSON = 'JSON', _('JSON Data')
    
    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='reports',
        help_text=_("Organization that owns this report")
    )
    
    # Report configuration
    name = models.CharField(
        max_length=200,
        help_text=_("Report name")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Report description")
    )
    report_type = models.CharField(
        max_length=50,
        choices=ReportType.choices,
        help_text=_("Type of report")
    )
    
    # Parameters (stored as JSON)
    default_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Default report parameters")
    )
    
    # Settings
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether report is active")
    )
    is_public = models.BooleanField(
        default=False,
        help_text=_("Whether report is visible to all users in organization")
    )
    
    # Caching
    cache_duration = models.IntegerField(
        default=300,  # 5 minutes
        validators=[MinValueValidator(0)],
        help_text=_("Cache duration in seconds (0 = no cache)")
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_reports',
        help_text=_("User who created this report")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When report was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When report was last updated")
    )
    
    class Meta:
        db_table = 'reporting_report'
        verbose_name = _('Report')
        verbose_name_plural = _('Reports')
        ordering = ['name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['report_type']),
            models.Index(fields=['created_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_report_type_display()})"
    
    @property
    def total_executions(self):
        """Get total number of times this report has been executed"""
        return self.executions.count()
    
    @property
    def last_execution(self):
        """Get last execution timestamp"""
        last = self.executions.order_by('-created_at').first()
        return last.created_at if last else None


class ReportSchedule(models.Model):
    """
    Scheduled report configuration.
    
    Defines when and how often reports should be automatically
    generated and delivered.
    """
    
    class Frequency(models.TextChoices):
        """Schedule frequencies"""
        DAILY = 'DAILY', _('Daily')
        WEEKLY = 'WEEKLY', _('Weekly')
        MONTHLY = 'MONTHLY', _('Monthly')
        QUARTERLY = 'QUARTERLY', _('Quarterly')
        CUSTOM = 'CUSTOM', _('Custom (Cron)')
    
    class DeliveryMethod(models.TextChoices):
        """Delivery methods"""
        EMAIL = 'EMAIL', _('Email')
        DASHBOARD = 'DASHBOARD', _('Dashboard')
        STORAGE = 'STORAGE', _('File Storage')
        ALL = 'ALL', _('All Methods')
    
    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='schedules',
        help_text=_("Report to schedule")
    )
    
    # Schedule configuration
    name = models.CharField(
        max_length=200,
        help_text=_("Schedule name")
    )
    frequency = models.CharField(
        max_length=20,
        choices=Frequency.choices,
        default=Frequency.DAILY,
        help_text=_("Report frequency")
    )
    cron_expression = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Cron expression for CUSTOM frequency")
    )
    
    # Execution settings
    export_format = models.CharField(
        max_length=20,
        choices=Report.ExportFormat.choices,
        default=Report.ExportFormat.PDF,
        help_text=_("Export format for scheduled report")
    )
    
    # Parameters (override report defaults)
    parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Report parameters for this schedule")
    )
    
    # Delivery
    delivery_method = models.CharField(
        max_length=20,
        choices=DeliveryMethod.choices,
        default=DeliveryMethod.EMAIL,
        help_text=_("How to deliver the report")
    )
    recipients = ArrayField(
        models.EmailField(),
        default=list,
        blank=True,
        help_text=_("Email recipients (for EMAIL delivery)")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether schedule is active")
    )
    last_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Last execution time")
    )
    next_run = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("Next scheduled execution time")
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_schedules',
        help_text=_("User who created this schedule")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When schedule was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When schedule was last updated")
    )
    
    class Meta:
        db_table = 'reporting_schedule'
        verbose_name = _('Report Schedule')
        verbose_name_plural = _('Report Schedules')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', 'is_active']),
            models.Index(fields=['next_run']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.get_frequency_display()}"
    
    @property
    def is_due(self):
        """Check if schedule is due for execution"""
        if not self.is_active or not self.next_run:
            return False
        return timezone.now() >= self.next_run


class ReportExecution(models.Model):
    """
    Report execution history and results.
    
    Tracks each report generation with metadata, parameters,
    and output file references.
    """
    
    class Status(models.TextChoices):
        """Execution statuses"""
        PENDING = 'PENDING', _('Pending')
        PROCESSING = 'PROCESSING', _('Processing')
        COMPLETED = 'COMPLETED', _('Completed')
        FAILED = 'FAILED', _('Failed')
        CACHED = 'CACHED', _('Cached')
    
    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        related_name='executions',
        help_text=_("Report that was executed")
    )
    schedule = models.ForeignKey(
        ReportSchedule,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='executions',
        help_text=_("Schedule that triggered this execution (if any)")
    )
    
    # Execution details
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        help_text=_("Execution status")
    )
    export_format = models.CharField(
        max_length=20,
        choices=Report.ExportFormat.choices,
        help_text=_("Export format used")
    )
    
    # Parameters used for this execution
    parameters = models.JSONField(
        default=dict,
        help_text=_("Parameters used for this execution")
    )
    
    # Results
    file_path = models.CharField(
        max_length=500,
        blank=True,
        help_text=_("Path to generated report file")
    )
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("File size in bytes")
    )
    
    # Metadata
    row_count = models.IntegerField(
        null=True,
        blank=True,
        help_text=_("Number of data rows in report")
    )
    execution_time = models.FloatField(
        null=True,
        blank=True,
        help_text=_("Execution time in seconds")
    )
    
    # Error handling
    error_message = models.TextField(
        blank=True,
        help_text=_("Error message if failed")
    )
    stack_trace = models.TextField(
        blank=True,
        help_text=_("Stack trace if failed")
    )
    
    # Cache key for result caching
    cache_key = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Redis cache key for cached results")
    )
    
    # Audit fields
    executed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='executed_reports',
        help_text=_("User who executed this report")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When execution was initiated")
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When execution completed")
    )
    
    class Meta:
        db_table = 'reporting_execution'
        verbose_name = _('Report Execution')
        verbose_name_plural = _('Report Executions')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['report', 'status']),
            models.Index(fields=['created_at']),
            models.Index(fields=['cache_key']),
        ]
    
    def __str__(self):
        return f"{self.report.name} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"
    
    @property
    def is_cached(self):
        """Check if execution used cached results"""
        return self.status == self.Status.CACHED
    
    @property
    def was_successful(self):
        """Check if execution was successful"""
        return self.status in [self.Status.COMPLETED, self.Status.CACHED]
    
    @property
    def duration(self):
        """Get execution duration"""
        if self.completed_at and self.created_at:
            return (self.completed_at - self.created_at).total_seconds()
        return self.execution_time


class ReportWidget(models.Model):
    """
    Dashboard widget configuration.
    
    Defines mini-reports/KPIs for dashboard display.
    """
    
    class WidgetType(models.TextChoices):
        """Widget visualization types"""
        KPI = 'KPI', _('Key Performance Indicator')
        CHART = 'CHART', _('Chart')
        TABLE = 'TABLE', _('Data Table')
        GAUGE = 'GAUGE', _('Gauge')
        TREND = 'TREND', _('Trend Line')
    
    class ChartType(models.TextChoices):
        """Chart types for CHART widgets"""
        LINE = 'LINE', _('Line Chart')
        BAR = 'BAR', _('Bar Chart')
        PIE = 'PIE', _('Pie Chart')
        DONUT = 'DONUT', _('Donut Chart')
        AREA = 'AREA', _('Area Chart')
    
    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='report_widgets',
        help_text=_("Organization that owns this widget")
    )
    report = models.ForeignKey(
        Report,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='widgets',
        help_text=_("Associated report (optional)")
    )
    
    # Widget configuration
    name = models.CharField(
        max_length=200,
        help_text=_("Widget name")
    )
    widget_type = models.CharField(
        max_length=20,
        choices=WidgetType.choices,
        default=WidgetType.KPI,
        help_text=_("Widget visualization type")
    )
    chart_type = models.CharField(
        max_length=20,
        choices=ChartType.choices,
        blank=True,
        help_text=_("Chart type (for CHART widgets)")
    )
    
    # Data source
    data_source = models.CharField(
        max_length=100,
        help_text=_("Data source identifier (e.g., 'project_count', 'total_revenue')")
    )
    query_parameters = models.JSONField(
        default=dict,
        blank=True,
        help_text=_("Parameters for data query")
    )
    
    # Display settings
    display_order = models.IntegerField(
        default=0,
        help_text=_("Display order on dashboard")
    )
    refresh_interval = models.IntegerField(
        default=300,  # 5 minutes
        validators=[MinValueValidator(0)],
        help_text=_("Auto-refresh interval in seconds (0 = no refresh)")
    )
    
    # Styling
    icon = models.CharField(
        max_length=50,
        blank=True,
        help_text=_("Icon class (e.g., 'fa-dollar-sign')")
    )
    color = models.CharField(
        max_length=20,
        blank=True,
        help_text=_("Widget color (hex or color name)")
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text=_("Whether widget is active")
    )
    
    # Audit fields
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_widgets',
        help_text=_("User who created this widget")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text=_("When widget was created")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text=_("When widget was last updated")
    )
    
    class Meta:
        db_table = 'reporting_widget'
        verbose_name = _('Dashboard Widget')
        verbose_name_plural = _('Dashboard Widgets')
        ordering = ['display_order', 'name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['display_order']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_widget_type_display()})"
