"""
Document Management System - Service Layer

Business logic for document operations including:
- Document upload
- Version management
- Generic object linking
- Transaction-safe operations
"""

import os
from typing import Optional
from django.db import transaction
from django.core.files.uploadedfile import UploadedFile
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ValidationError

from apps.documents.models import Document
from apps.authentication.models import User


class DocumentService:
    """
    Service layer for document operations.
    
    All operations are transaction-safe and include proper validation.
    """
    
    @staticmethod
    @transaction.atomic
    def upload_document(
        title: str,
        document_type: str,
        file: UploadedFile,
        uploaded_by: User,
        project=None,
        organization=None,
        description: str = '',
        tags: str = '',
        is_confidential: bool = False,
        reference_number: str = '',
        expiry_date=None,
        related_object=None,
        visibility: str = None
    ) -> Document:
        """
        Upload a new document.
        
        Args:
            title: Document title
            document_type: One of Document.DocumentType choices
            file: Uploaded file
            uploaded_by: User uploading the document
            project: Project instance (optional)
            organization: Organization instance (optional)
            description: Document description
            tags: Comma-separated tags
            is_confidential: Mark as confidential
            reference_number: External reference number
            expiry_date: Expiry date for permits/licenses
            related_object: Generic foreign key to any model instance
            visibility: Access control level (defaults to PROJECT_TEAM)
        
        Returns:
            Document instance
        
        Example:
            doc = DocumentService.upload_document(
                title="LPO-001 Cement Order",
                document_type=Document.DocumentType.LPO_ATTACHMENT,
                file=request.FILES['file'],
                uploaded_by=request.user,
                project=project,
                related_object=lpo_instance,
                visibility=Document.Visibility.PROJECT_TEAM
            )
        """
        # Validate document type
        if document_type not in Document.DocumentType.values:
            raise ValidationError(f"Invalid document type: {document_type}")
        
        # Create document
        document = Document(
            title=title,
            document_type=document_type,
            file=file,
            uploaded_by=uploaded_by,
            project=project,
            organization=organization,
            description=description,
            tags=tags,
            is_confidential=is_confidential,
            reference_number=reference_number,
            expiry_date=expiry_date,
            visibility=visibility or Document.Visibility.PROJECT_TEAM,
            version=1,
            is_latest=True
        )
        
        # Link to related object if provided
        if related_object:
            content_type = ContentType.objects.get_for_model(related_object)
            document.content_type = content_type
            document.object_id = related_object.id
        
        document.save()
        
        return document
    
    @staticmethod
    @transaction.atomic
    def create_new_version(
        document: Document,
        new_file: UploadedFile,
        uploaded_by: User,
        notes: str = ''
    ) -> Document:
        """
        Create a new version of an existing document.
        
        This implementation:
        1. Marks the old document as is_latest=False
        2. Creates a new Document instance with incremented version
        3. Links new version to previous version
        4. Preserves all metadata from original document
        
        Args:
            document: Existing document to version
            new_file: New file for updated version
            uploaded_by: User uploading the new version
            notes: Notes about changes in this version
        
        Returns:
            New Document instance (latest version)
        
        Example:
            new_doc = DocumentService.create_new_version(
                document=original_doc,
                new_file=request.FILES['file'],
                uploaded_by=request.user,
                notes="Updated pricing to reflect market changes"
            )
        """
        # Mark current version as not latest
        document.is_latest = False
        document.save(update_fields=['is_latest'])
        
        # Create new version
        new_version = Document(
            # Copy metadata from original
            title=document.title,
            document_type=document.document_type,
            project=document.project,
            organization=document.organization,
            description=document.description,
            tags=document.tags,
            is_confidential=document.is_confidential,
            reference_number=document.reference_number,
            expiry_date=document.expiry_date,
            
            # Link to related object
            content_type=document.content_type,
            object_id=document.object_id,
            
            # New version data
            file=new_file,
            uploaded_by=uploaded_by,
            version=document.version + 1,
            is_latest=True,
            previous_version=document,
            version_notes=notes
        )
        
        new_version.save()
        
        return new_version
    
    @staticmethod
    def get_latest_document(document_id: str) -> Optional[Document]:
        """
        Get the latest version of a document.
        
        Args:
            document_id: UUID of any version of the document
        
        Returns:
            Latest version of the document, or None if not found
        """
        try:
            document = Document.objects.get(id=document_id)
            
            # If this is already the latest, return it
            if document.is_latest:
                return document
            
            # Otherwise, walk forward to find latest
            current = document
            while current.next_versions.exists():
                current = current.next_versions.first()
            
            return current
        except Document.DoesNotExist:
            return None
    
    @staticmethod
    @transaction.atomic
    def link_document_to_object(
        document: Document,
        related_object
    ) -> Document:
        """
        Link an existing document to another object.
        
        This allows documents to be attached to multiple objects
        or re-linked if needed.
        
        Args:
            document: Document to link
            related_object: Model instance to link to
        
        Returns:
            Updated document
        
        Example:
            # Link document to variation order
            DocumentService.link_document_to_object(
                document=doc,
                related_object=variation_order
            )
        """
        content_type = ContentType.objects.get_for_model(related_object)
        document.content_type = content_type
        document.object_id = related_object.id
        document.save(update_fields=['content_type', 'object_id'])
        
        return document
    
    @staticmethod
    @transaction.atomic
    def delete_document(document_id: str, hard_delete: bool = False) -> bool:
        """
        Delete a document.
        
        By default, performs soft delete (marks as deleted).
        Set hard_delete=True to permanently delete file and database record.
        
        Args:
            document_id: UUID of document to delete
            hard_delete: If True, permanently delete. If False, soft delete.
        
        Returns:
            True if deleted successfully
        
        Note:
            For versioned documents, consider implications of deleting
            intermediate versions. This method only operates on the
            specified version.
        """
        try:
            document = Document.objects.get(id=document_id)
            
            if hard_delete:
                # Delete file from storage
                if document.file:
                    try:
                        document.file.delete(save=False)
                    except Exception:
                        pass  # File might already be deleted
                
                # Delete database record
                document.delete()
            else:
                # Soft delete - mark as not latest
                # (in future, could add is_deleted field)
                document.is_latest = False
                document.save(update_fields=['is_latest'])
            
            return True
        except Document.DoesNotExist:
            return False
    
    @staticmethod
    @transaction.atomic
    def update_document_metadata(
        document: Document,
        title: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[str] = None,
        is_confidential: Optional[bool] = None,
        reference_number: Optional[str] = None,
        expiry_date=None
    ) -> Document:
        """
        Update document metadata without changing the file.
        
        Args:
            document: Document to update
            title: New title (optional)
            description: New description (optional)
            tags: New tags (optional)
            is_confidential: New confidential status (optional)
            reference_number: New reference number (optional)
            expiry_date: New expiry date (optional)
        
        Returns:
            Updated document
        """
        update_fields = []
        
        if title is not None:
            document.title = title
            update_fields.append('title')
        
        if description is not None:
            document.description = description
            update_fields.append('description')
        
        if tags is not None:
            document.tags = tags
            update_fields.append('tags')
        
        if is_confidential is not None:
            document.is_confidential = is_confidential
            update_fields.append('is_confidential')
        
        if reference_number is not None:
            document.reference_number = reference_number
            update_fields.append('reference_number')
        
        if expiry_date is not None:
            document.expiry_date = expiry_date
            update_fields.append('expiry_date')
        
        if update_fields:
            document.save(update_fields=update_fields)
        
        return document
    
    @staticmethod
    def get_document_stats(project=None, organization=None) -> dict:
        """
        Get document statistics.
        
        Args:
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            Dictionary with statistics
        """
        queryset = Document.objects.filter(is_latest=True)
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        # Count by type
        type_counts = {}
        for doc_type in Document.DocumentType.values:
            count = queryset.filter(document_type=doc_type).count()
            if count > 0:
                type_counts[doc_type] = count
        
        # Calculate total size
        total_size = sum(
            doc.file_size for doc in queryset if doc.file_size
        )
        
        return {
            'total_documents': queryset.count(),
            'total_size_bytes': total_size,
            'total_size_mb': round(total_size / (1024 * 1024), 2),
            'counts_by_type': type_counts,
            'confidential_count': queryset.filter(is_confidential=True).count(),
        }
    
    @staticmethod
    @transaction.atomic
    def sign_document(
        document: Document,
        signed_by: User,
        signature_text: Optional[str] = None
    ) -> Document:
        """
        Digitally sign a document.
        
        Creates a cryptographic hash of the signature for verification.
        
        Args:
            document: Document to sign
            signed_by: User signing the document
            signature_text: Optional text to include in signature hash
        
        Returns:
            Signed document
        
        Example:
            signed_doc = DocumentService.sign_document(
                document=contract,
                signed_by=request.user,
                signature_text=f"{request.user.get_full_name()} - Approved"
            )
        """
        from django.utils import timezone
        
        # Generate signature text if not provided
        if signature_text is None:
            signature_text = f"{signed_by.id}:{signed_by.username}:{timezone.now().isoformat()}"
        
        # Generate signature hash
        signature_hash = document.generate_signature_hash(signature_text)
        
        # Update document
        document.signed_by = signed_by
        document.signed_at = timezone.now()
        document.signature_hash = signature_hash
        
        document.save(update_fields=['signed_by', 'signed_at', 'signature_hash'])
        
        return document
    
    @staticmethod
    @transaction.atomic
    def update_visibility(
        document: Document,
        visibility: str,
        updated_by: User
    ) -> Document:
        """
        Update document visibility/access control level.
        
        Args:
            document: Document to update
            visibility: New visibility level (from Document.Visibility choices)
            updated_by: User making the change
        
        Returns:
            Updated document
        
        Raises:
            ValidationError: If visibility level is invalid
        
        Example:
            DocumentService.update_visibility(
                document=contract,
                visibility=Document.Visibility.FINANCE_ONLY,
                updated_by=request.user
            )
        """
        if visibility not in Document.Visibility.values:
            raise ValidationError(f"Invalid visibility level: {visibility}")
        
        document.visibility = visibility
        document.save(update_fields=['visibility'])
        
        return document
    
    @staticmethod
    def verify_document_signature(
        document: Document,
        signature_text: str
    ) -> bool:
        """
        Verify the integrity of a document signature.
        
        Args:
            document: Document with signature to verify
            signature_text: Original signature text used during signing
        
        Returns:
            True if signature is valid and matches
        
        Example:
            is_valid = DocumentService.verify_document_signature(
                document=signed_doc,
                signature_text=original_signature_text
            )
        """
        return document.verify_signature(signature_text)

