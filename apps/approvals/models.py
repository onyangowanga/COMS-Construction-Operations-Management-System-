"""
Approvals Models for COMS
Manages statutory project approvals from County Government, NCA, etc.
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.projects.models import Project
from apps.documents.models import Document


class ProjectApproval(models.Model):
    """
    Statutory approvals for construction projects
    """
    
    class Authority(models.TextChoices):
        COUNTY = 'COUNTY', _('County Government')
        NCA = 'NCA', _('National Construction Authority')
        NEMA = 'NEMA', _('National Environment Management Authority')
        FIRE_DEPT = 'FIRE_DEPT', _('Fire Department')
        PUBLIC_HEALTH = 'PUBLIC_HEALTH', _('Public Health Department')
        OTHER = 'OTHER', _('Other Authority')
    
    class ApprovalType(models.TextChoices):
        PLANNING_PERMIT = 'PLANNING_PERMIT', _('Planning Permit')
        BUILDING_PERMIT = 'BUILDING_PERMIT', _('Building Permit')
        OCCUPANCY_CERTIFICATE = 'OCCUPANCY_CERTIFICATE', _('Occupancy Certificate')
        NCA_REGISTRATION = 'NCA_REGISTRATION', _('NCA Project Registration')
        ENVIRONMENTAL_IMPACT = 'ENVIRONMENTAL_IMPACT', _('Environmental Impact Assessment')
        FIRE_CERTIFICATE = 'FIRE_CERTIFICATE', _('Fire Safety Certificate')
        HEALTH_CERTIFICATE = 'HEALTH_CERTIFICATE', _('Public Health Certificate')
        OTHER = 'OTHER', _('Other Approval')
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        APPROVED = 'APPROVED', _('Approved')
        REJECTED = 'REJECTED', _('Rejected')
        EXPIRED = 'EXPIRED', _('Expired')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='approvals'
    )
    authority = models.CharField(
        max_length=20,
        choices=Authority.choices
    )
    approval_type = models.CharField(
        max_length=30,
        choices=ApprovalType.choices
    )
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDING
    )
    application_date = models.DateField(null=True, blank=True)
    approval_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date approval was granted")
    )
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Date approval expires")
    )
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("Official approval reference number")
    )
    document = models.ForeignKey(
        Document,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approvals',
        help_text=_("Scanned approval document")
    )
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'project_approvals'
        verbose_name = _('Project Approval')
        verbose_name_plural = _('Project Approvals')
        ordering = ['-approval_date']
        indexes = [
            models.Index(fields=['project', 'authority']),
            models.Index(fields=['status']),
            models.Index(fields=['approval_type']),
        ]
    
    def __str__(self):
        return f"{self.project.code} - {self.get_approval_type_display()} ({self.get_authority_display()})"
