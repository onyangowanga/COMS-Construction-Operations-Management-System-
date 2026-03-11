from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator
from decimal import Decimal
import uuid


class DailySiteReport(models.Model):
    """Daily site report prepared by site engineers"""
    
    WEATHER_CHOICES = [
        ('SUNNY', 'Sunny'),
        ('CLOUDY', 'Cloudy'),
        ('RAINY', 'Rainy'),
        ('STORMY', 'Stormy'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='site_reports'
    )
    report_date = models.DateField()
    weather = models.CharField(max_length=20, choices=WEATHER_CHOICES, default='SUNNY')
    labour_summary = models.TextField(
        help_text="Summary of labour on site (e.g., '20 masons, 15 labourers, 5 carpenters')"
    )
    work_completed = models.TextField(
        help_text="Description of work completed during the day"
    )
    materials_delivered = models.TextField(
        blank=True,
        default='',
        help_text="Materials delivered to site today (if any)"
    )
    issues = models.TextField(
        blank=True,
        default='',
        help_text="Any issues or concerns noted"
    )
    prepared_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='site_reports_prepared'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'daily_site_reports'
        ordering = ['-report_date', '-created_at']
        unique_together = [['project', 'report_date']]
        indexes = [
            models.Index(fields=['project', '-report_date']),
            models.Index(fields=['report_date']),
            models.Index(fields=['prepared_by']),
        ]
        verbose_name = 'Daily Site Report'
        verbose_name_plural = 'Daily Site Reports'
    
    def __str__(self):
        return f"{self.project.name} - {self.report_date}"
    
    @property
    def has_issues(self):
        """Check if report has any issues noted"""
        return bool(self.issues.strip())


class MaterialDelivery(models.Model):
    """Track material deliveries to construction sites"""
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending Inspection'),
        ('ACCEPTED', 'Accepted'),
        ('REJECTED', 'Rejected'),
        ('PARTIAL', 'Partially Accepted'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='material_deliveries'
    )
    supplier = models.ForeignKey(
        'suppliers.Supplier',
        on_delete=models.PROTECT,
        related_name='material_deliveries',
        null=True,
        blank=True,
        help_text="Supplier who delivered the material"
    )
    supplier_name = models.CharField(
        max_length=255,
        blank=True,
        default='',
        help_text="Supplier name if not in system"
    )
    material_name = models.CharField(max_length=255)
    quantity = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    unit = models.CharField(
        max_length=50,
        default='units',
        help_text="Unit of measurement (e.g., bags, tons, m³, pieces)"
    )
    delivery_note_number = models.CharField(max_length=100)
    delivery_date = models.DateField()
    received_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='materials_received'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING'
    )
    notes = models.TextField(
        blank=True,
        default='',
        help_text="Additional notes or observations"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'material_deliveries'
        ordering = ['-delivery_date', '-created_at']
        indexes = [
            models.Index(fields=['project', '-delivery_date']),
            models.Index(fields=['supplier', '-delivery_date']),
            models.Index(fields=['delivery_date']),
            models.Index(fields=['status']),
            models.Index(fields=['delivery_note_number']),
        ]
        verbose_name = 'Material Delivery'
        verbose_name_plural = 'Material Deliveries'
    
    def __str__(self):
        return f"{self.material_name} - {self.delivery_note_number}"
    
    def save(self, *args, **kwargs):
        """Auto-populate supplier_name from supplier if not provided"""
        if self.supplier and not self.supplier_name:
            self.supplier_name = self.supplier.name
        super().save(*args, **kwargs)
    
    @property
    def supplier_display(self):
        """Get supplier name for display"""
        return self.supplier_name or (self.supplier.name if self.supplier else 'Unknown')


class SiteIssue(models.Model):
    """Track issues and concerns raised during site operations"""
    
    SEVERITY_CHOICES = [
        ('LOW', 'Low'),
        ('MEDIUM', 'Medium'),
        ('HIGH', 'High'),
        ('CRITICAL', 'Critical'),
    ]
    
    STATUS_CHOICES = [
        ('OPEN', 'Open'),
        ('IN_PROGRESS', 'In Progress'),
        ('RESOLVED', 'Resolved'),
        ('CLOSED', 'Closed'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.CASCADE,
        related_name='site_issues'
    )
    title = models.CharField(
        max_length=255,
        help_text="Brief title of the issue"
    )
    description = models.TextField(
        help_text="Detailed description of the issue"
    )
    severity = models.CharField(
        max_length=20,
        choices=SEVERITY_CHOICES,
        default='MEDIUM'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='OPEN'
    )
    reported_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name='site_issues_reported'
    )
    assigned_to = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        related_name='site_issues_assigned',
        null=True,
        blank=True
    )
    reported_date = models.DateTimeField(auto_now_add=True)
    resolved_date = models.DateTimeField(null=True, blank=True)
    resolution_notes = models.TextField(
        blank=True,
        default='',
        help_text="Notes on how the issue was resolved"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'site_issues'
        ordering = ['-severity', '-reported_date']
        indexes = [
            models.Index(fields=['project', 'status']),
            models.Index(fields=['project', '-reported_date']),
            models.Index(fields=['severity', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['status']),
        ]
        verbose_name = 'Site Issue'
        verbose_name_plural = 'Site Issues'
    
    def __str__(self):
        return f"{self.title} ({self.get_severity_display()})"
    
    @property
    def is_open(self):
        """Check if issue is still open"""
        return self.status in ['OPEN', 'IN_PROGRESS']
    
    @property
    def is_high_priority(self):
        """Check if issue requires urgent attention"""
        return self.severity in ['HIGH', 'CRITICAL']
