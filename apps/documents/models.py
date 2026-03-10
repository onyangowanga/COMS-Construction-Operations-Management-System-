"""
Document Models for COMS
Manages project documents with version control
"""
import uuid
from django.db import models
from django.utils.translation import gettext_lazy as _
from apps.authentication.models import User
from apps.projects.models import Project


class Document(models.Model):
    """
    Project documents (drawings, approvals, invoices, etc.)
    """
    
    class DocumentType(models.TextChoices):
        DRAWINGS = 'DRAWINGS', _('Architectural Drawings')
        STRUCTURAL_DRAWINGS = 'STRUCTURAL_DRAWINGS', _('Structural Drawings')
        MECHANICAL_DRAWINGS = 'MECHANICAL_DRAWINGS', _('Mechanical Drawings')
        ELECTRICAL_DRAWINGS = 'ELECTRICAL_DRAWINGS', _('Electrical Drawings')
        APPROVALS = 'APPROVALS', _('Approval Documents')
        INVOICES = 'INVOICES', _('Invoices')
        RECEIPTS = 'RECEIPTS', _('Receipts')
        BQ = 'BQ', _('Bill of Quantities')
        CONTRACT = 'CONTRACT', _('Contract Documents')
        REPORTS = 'REPORTS', _('Progress Reports')
        OTHER = 'OTHER', _('Other')
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents'
    )
    name = models.CharField(max_length=200, help_text=_("Document name"))
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        default=DocumentType.OTHER
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents'
    )
    description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'documents'
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['project', 'document_type']),
            models.Index(fields=['document_type']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.project.code})"
    
    @property
    def latest_version(self):
        """Get the latest version of this document"""
        return self.versions.filter(is_latest=True).first()


class DocumentVersion(models.Model):
    """
    Version control for documents (especially construction drawings)
    """
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='versions'
    )
    version_number = models.CharField(
        max_length=20,
        help_text=_("Version number (e.g., v1.0, Rev A)")
    )
    file_path = models.CharField(
        max_length=500,
        help_text=_("Path to document file")
    )
    is_latest = models.BooleanField(
        default=True,
        help_text=_("Is this the current version?")
    )
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_versions'
    )
    notes = models.TextField(blank=True, help_text=_("Version notes/changelog"))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'document_versions'
        verbose_name = _('Document Version')
        verbose_name_plural = _('Document Versions')
        ordering = ['-created_at']
        unique_together = [['document', 'version_number']]
        indexes = [
            models.Index(fields=['document', 'is_latest']),
        ]
    
    def __str__(self):
        return f"{self.document.name} - {self.version_number}"
    
    def save(self, *args, **kwargs):
        """Mark all other versions as not latest when saving a new latest version"""
        if self.is_latest:
            # Mark all other versions of this document as not latest
            DocumentVersion.objects.filter(
                document=self.document
            ).update(is_latest=False)
        super().save(*args, **kwargs)
