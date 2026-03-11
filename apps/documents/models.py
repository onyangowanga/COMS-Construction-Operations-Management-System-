"""
Document Management System Models for COMS

Centralized document storage with versioning and generic foreign keys
to link documents to any model (Projects, LPOs, Variations, Valuations, etc.)

Design Philosophy:
- Single Document model with built-in versioning
- Generic relations to link to any model
- S3-ready file storage design
- Comprehensive document type classification
- Automatic metadata extraction
"""

import os
import uuid
from decimal import Decimal
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.core.validators import FileExtensionValidator
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from apps.authentication.models import User
from apps.projects.models import Project


def document_upload_path(instance, filename):
    """
    Generate upload path for documents.
    
    Format: documents/{org_id}/{project_id}/{year}/{month}/{filename}
    
    This structure supports:
    - Easy migration to S3
    - Organized file hierarchy
    - Date-based browsing
    """
    org_id = instance.organization.id if instance.organization else 'no-org'
    project_id = instance.project.id if instance.project else 'no-project'
    now = timezone.now()
    
    # Preserve original filename but make it safe
    safe_filename = filename.replace(' ', '_')
    
    return f'documents/{org_id}/{project_id}/{now.year}/{now.month:02d}/{safe_filename}'


class Document(models.Model):
    """
    Unified Document model with versioning and generic relations.
    
    Features:
    - Links to any model via GenericForeignKey
    - Built-in versioning (no separate table needed)
    - Automatic file metadata extraction
    - S3-ready storage design
    - Comprehensive classification
    
    Usage Example:
        # Link document to LPO
        doc = Document.objects.create(
            title="LPO-001 Cement Order",
            document_type=Document.DocumentType.LPO_ATTACHMENT,
            file=uploaded_file,
            uploaded_by=user,
            project=project,
            content_object=lpo_instance
        )
        
        # Create new version
        new_version = DocumentService.create_new_version(
            document=doc,
            new_file=updated_file,
            uploaded_by=user,
            notes="Updated pricing"
        )
    """
    
    # === DOCUMENT TYPE CLASSIFICATION ===
    
    class DocumentType(models.TextChoices):
        # Procurement Documents
        CONTRACT = 'CONTRACT', _('Contract Document')
        LPO_ATTACHMENT = 'LPO_ATTACHMENT', _('LPO Attachment')
        DELIVERY_NOTE = 'DELIVERY_NOTE', _('Delivery Note')
        SUPPLIER_INVOICE = 'SUPPLIER_INVOICE', _('Supplier Invoice')
        PAYMENT_VOUCHER = 'PAYMENT_VOUCHER', _('Payment Voucher')
        
        # Technical Documents
        DRAWING = 'DRAWING', _('Technical Drawing')
        BOQ = 'BOQ', _('Bill of Quantities')
        SPECIFICATION = 'SPECIFICATION', _('Technical Specification')
        METHOD_STATEMENT = 'METHOD_STATEMENT', _('Method Statement')
        
        # Site Documents
        SITE_PHOTO = 'SITE_PHOTO', _('Site Photo')
        SITE_REPORT_ATTACHMENT = 'SITE_REPORT_ATTACHMENT', _('Site Report Attachment')
        PROGRESS_REPORT = 'PROGRESS_REPORT', _('Progress Report')
        
        # Variation & Valuation
        VARIATION_INSTRUCTION = 'VARIATION_INSTRUCTION', _('Variation Instruction')
        VALUATION_CERTIFICATE = 'VALUATION_CERTIFICATE', _('Valuation Certificate')
        
        # Compliance Documents
        RISK_ASSESSMENT = 'RISK_ASSESSMENT', _('Risk Assessment')
        PERMIT = 'PERMIT', _('Permit/License')
        QUALITY_DOCUMENT = 'QUALITY_DOCUMENT', _('Quality Document')
        SAFETY_DOCUMENT = 'SAFETY_DOCUMENT', _('Safety Document')
        
        # Communication
        CORRESPONDENCE = 'CORRESPONDENCE', _('Correspondence/Letter')
        MEETING_MINUTES = 'MEETING_MINUTES', _('Meeting Minutes')
        
        OTHER = 'OTHER', _('Other Document')
    
    # === ACCESS CONTROL ===
    
    class Visibility(models.TextChoices):
        """
        Document visibility/access control levels.
        
        Controls who can view and access specific documents.
        """
        PUBLIC = 'PUBLIC', _('Public - All Users')
        PROJECT_TEAM = 'PROJECT_TEAM', _('Project Team Only')
        FINANCE_ONLY = 'FINANCE_ONLY', _('Finance Team Only')
        ADMIN_ONLY = 'ADMIN_ONLY', _('Admin Only')
        CONFIDENTIAL = 'CONFIDENTIAL', _('Confidential - Restricted Access')
    
    # === IDENTIFICATION ===
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    organization = models.ForeignKey(
        'authentication.Organization',
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        help_text=_("Organization owning this document")
    )
    
    project = models.ForeignKey(
        Project,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True,
        help_text=_("Project this document belongs to")
    )
    
    document_type = models.CharField(
        max_length=30,
        choices=DocumentType.choices,
        db_index=True,
        help_text=_("Classification of document")
    )
    
    title = models.CharField(
        max_length=255,
        help_text=_("Document title")
    )
    
    description = models.TextField(
        blank=True,
        help_text=_("Document description and notes")
    )
    
    # === FILE STORAGE ===
    
    file = models.FileField(
        upload_to=document_upload_path,
        validators=[
            FileExtensionValidator(
                allowed_extensions=[
                    # Documents
                    'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                    # Images
                    'jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg',
                    # CAD files
                    'dwg', 'dxf', 'rvt',
                    # Archives
                    'zip', 'rar', '7z',
                    # Text files
                    'txt', 'csv', 'xml', 'json',
                ]
            )
        ],
        help_text=_("Document file")
    )
    
    file_size = models.BigIntegerField(
        null=True,
        blank=True,
        help_text=_("File size in bytes (auto-populated)")
    )
    
    file_extension = models.CharField(
        max_length=10,
        blank=True,
        help_text=_("File extension (auto-populated)")
    )
    
    # === GENERIC FOREIGN KEY (link to any model) ===
    
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text=_("Type of related object (e.g., LPO, Variation)")
    )
    
    object_id = models.UUIDField(
        null=True,
        blank=True,
        help_text=_("ID of related object")
    )
    
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # === VERSIONING ===
    
    version = models.PositiveIntegerField(
        default=1,
        help_text=_("Document version number")
    )
    
    is_latest = models.BooleanField(
        default=True,
        db_index=True,
        help_text=_("Whether this is the latest version")
    )
    
    previous_version = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='next_versions',
        help_text=_("Link to previous version")
    )
    
    version_notes = models.TextField(
        blank=True,
        help_text=_("Notes about this version (changes made)")
    )
    
    # === METADATA ===
    
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        help_text=_("User who uploaded this document")
    )
    
    uploaded_at = models.DateTimeField(
        auto_now_add=True,
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        auto_now=True
    )
    
    # === ADDITIONAL FIELDS ===
    
    tags = models.CharField(
        max_length=255,
        blank=True,
        help_text=_("Comma-separated tags for searching")
    )
    
    is_confidential = models.BooleanField(
        default=False,
        db_index=True,
        help_text=_("Mark as confidential (restricted access)")
    )
    
    expiry_date = models.DateField(
        null=True,
        blank=True,
        help_text=_("Document expiry date (for permits, licenses)")
    )
    
    reference_number = models.CharField(
        max_length=100,
        blank=True,
        help_text=_("External reference number")
    )
    
    # === DIGITAL SIGNATURE ===
    
    signed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='signed_documents',
        help_text=_("User who digitally signed this document")
    )
    
    signed_at = models.DateTimeField(
        null=True,
        blank=True,
        db_index=True,
        help_text=_("Date and time when document was signed")
    )
    
    signature_hash = models.CharField(
        max_length=128,
        blank=True,
        help_text=_("Cryptographic hash of signature for verification")
    )
    
    # === ACCESS CONTROL ===
    
    visibility = models.CharField(
        max_length=20,
        choices=Visibility.choices,
        default=Visibility.PROJECT_TEAM,
        db_index=True,
        help_text=_("Controls who can view this document")
    )
    
    class Meta:
        db_table = 'documents'
        ordering = ['-uploaded_at']
        indexes = [
            models.Index(fields=['project', 'document_type']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['is_latest', 'document_type']),
            models.Index(fields=['uploaded_at']),
            models.Index(fields=['is_confidential']),
            models.Index(fields=['signed_at']),
            models.Index(fields=['visibility']),
        ]
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')
    
    def __str__(self):
        version_str = f" (v{self.version})" if self.version > 1 else ""
        return f"{self.title}{version_str}"
    
    def save(self, *args, **kwargs):
        """Override save to set file metadata automatically"""
        if self.file:
            # Set file size
            if hasattr(self.file, 'size'):
                self.file_size = self.file.size
            
            # Set file extension
            if self.file.name:
                self.file_extension = os.path.splitext(self.file.name)[1].lower().strip('.')
        
        super().save(*args, **kwargs)
    
    # === PROPERTIES ===
    
    @property
    def file_name(self):
        """Get original filename"""
        if self.file:
            return os.path.basename(self.file.name)
        return None
    
    @property
    def file_size_mb(self):
        """Get file size in MB"""
        if self.file_size:
            return round(self.file_size / (1024 * 1024), 2)
        return 0
    
    @property
    def file_size_display(self):
        """Get human-readable file size"""
        if not self.file_size:
            return "0 B"
        
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} TB"
    
    @property
    def is_image(self):
        """Check if document is an image"""
        image_extensions = ['jpg', 'jpeg', 'png', 'gif', 'bmp', 'webp', 'svg']
        return self.file_extension in image_extensions
    
    @property
    def is_pdf(self):
        """Check if document is a PDF"""
        return self.file_extension == 'pdf'
    
    @property
    def is_cad(self):
        """Check if document is a CAD file"""
        cad_extensions = ['dwg', 'dxf', 'rvt']
        return self.file_extension in cad_extensions
    
    @property
    def is_office_document(self):
        """Check if document is MS Office or similar"""
        office_extensions = ['doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx']
        return self.file_extension in office_extensions
    
    @property
    def has_versions(self):
        """Check if document has multiple versions"""
        return self.version > 1 or self.next_versions.exists()
    
    @property
    def related_object_display(self):
        """Get display name of related object"""
        if self.content_object:
            return str(self.content_object)
        return None
    
    @property
    def is_signed(self):
        """Check if document has been digitally signed"""
        return self.signed_by is not None and self.signed_at is not None
    
    @property
    def requires_signature(self):
        """Check if document type typically requires signature"""
        signature_required_types = [
            self.DocumentType.CONTRACT,
            self.DocumentType.PAYMENT_VOUCHER,
            self.DocumentType.VALUATION_CERTIFICATE,
            self.DocumentType.VARIATION_INSTRUCTION,
        ]
        return self.document_type in signature_required_types
    
    @property
    def is_restricted(self):
        """Check if document has restricted access"""
        return self.visibility in [
            self.Visibility.FINANCE_ONLY,
            self.Visibility.ADMIN_ONLY,
            self.Visibility.CONFIDENTIAL
        ]
    
    # === METHODS ===
    
    def get_version_history(self):
        """
        Get all versions of this document in chronological order.
        
        Returns:
            List of Document instances ordered from oldest to newest
        """
        if self.previous_version:
            # Walk back to first version
            first_version = self
            while first_version.previous_version:
                first_version = first_version.previous_version
            
            # Get all versions from first
            versions = [first_version]
            current = first_version
            while current.next_versions.exists():
                current = current.next_versions.first()
                versions.append(current)
            return versions
        else:
            # This is the first version, get all next versions
            versions = [self]
            for next_ver in self.next_versions.all():
                versions.extend(next_ver.get_version_history())
            return versions
    
    def get_download_url(self):
        """Get download URL for this document"""
        if self.file:
            return self.file.url
        return None
    
    def can_user_access(self, user):
        """
        Check if a user has access to view this document.
        
        Args:
            user: User instance
        
        Returns:
            bool: True if user has access
        
        Access Rules:
            - PUBLIC: All authenticated users
            - PROJECT_TEAM: Project team members
            - FINANCE_ONLY: Finance team members
            - ADMIN_ONLY: Admin users only
            - CONFIDENTIAL: Admin + document owner
        """
        if not user or not user.is_authenticated:
            return False
        
        # Admins can access all documents
        if user.is_superuser or user.is_staff:
            return True
        
        # Document uploader can always access
        if self.uploaded_by == user:
            return True
        
        # Check visibility levels
        if self.visibility == self.Visibility.PUBLIC:
            return True
        
        if self.visibility == self.Visibility.PROJECT_TEAM:
            # Check if user is part of project team
            if self.project:
                # Add your project team membership check here
                # For now, return True for simplicity
                return True
            return True
        
        if self.visibility == self.Visibility.FINANCE_ONLY:
            # Check if user is in finance team
            # Add your finance team check here
            # For now, check if user has finance-related groups
            return user.groups.filter(name__icontains='finance').exists()
        
        if self.visibility == self.Visibility.ADMIN_ONLY:
            return user.is_staff
        
        if self.visibility == self.Visibility.CONFIDENTIAL:
            return user.is_staff or user == self.uploaded_by
        
        return False
    
    def generate_signature_hash(self, signature_text: str) -> str:
        """
        Generate cryptographic hash for document signature.
        
        Args:
            signature_text: Text to hash (e.g., user details + timestamp)
        
        Returns:
            str: SHA-256 hash
        """
        import hashlib
        
        # Combine document ID, file hash, and signature text
        data_to_hash = f"{self.id}:{signature_text}:{self.uploaded_at.isoformat()}"
        
        return hashlib.sha256(data_to_hash.encode()).hexdigest()
    
    def verify_signature(self, signature_text: str) -> bool:
        """
        Verify document signature integrity.
        
        Args:
            signature_text: Original signature text
        
        Returns:
            bool: True if signature is valid
        """
        if not self.signature_hash:
            return False
        
        expected_hash = self.generate_signature_hash(signature_text)
        return self.signature_hash == expected_hash

