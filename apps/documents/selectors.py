"""
Document Management System - Selector Layer

Optimized database queries for document retrieval.
All selectors use select_related and prefetch_related for efficiency.
"""

from typing import List, Optional
from django.db.models import Q, QuerySet, Prefetch
from django.contrib.contenttypes.models import ContentType

from apps.documents.models import Document


class DocumentSelector:
    """
    Optimized selectors for document queries.
    
    All methods return QuerySets with proper prefetching to avoid N+1 queries.
    """
    
    @staticmethod
    def get_base_queryset() -> QuerySet:
        """
        Get base queryset with common select_related optimizations.
        
        Returns:
            Optimized QuerySet
        """
        return Document.objects.select_related(
            'project',
            'organization',
            'uploaded_by',
            'content_type',
            'previous_version'
        )
    
    @staticmethod
    def get_project_documents(
        project,
        document_type: Optional[str] = None,
        latest_only: bool = True,
        include_confidential: bool = True
    ) -> QuerySet:
        """
        Get all documents for a project.
        
        Args:
            project: Project instance
            document_type: Filter by document type (optional)
            latest_only: Only return latest versions
            include_confidential: Include confidential documents
        
        Returns:
            QuerySet of Document instances
        
        Example:
            # Get all latest drawings for a project
            drawings = DocumentSelector.get_project_documents(
                project=my_project,
                document_type=Document.DocumentType.DRAWING,
                latest_only=True
            )
        """
        queryset = DocumentSelector.get_base_queryset().filter(
            project=project
        )
        
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        if latest_only:
            queryset = queryset.filter(is_latest=True)
        
        if not include_confidential:
            queryset = queryset.filter(is_confidential=False)
        
        return queryset.order_by('-uploaded_at')
    
    @staticmethod
    def get_documents_by_type(
        document_type: str,
        project=None,
        organization=None,
        latest_only: bool = True
    ) -> QuerySet:
        """
        Get documents filtered by type.
        
        Args:
            document_type: Document type to filter by
            project: Filter by project (optional)
            organization: Filter by organization (optional)
            latest_only: Only return latest versions
        
        Returns:
            QuerySet of Document instances
        
        Example:
            # Get all LPO attachments for organization
            lpo_docs = DocumentSelector.get_documents_by_type(
                document_type=Document.DocumentType.LPO_ATTACHMENT,
                organization=my_org
            )
        """
        queryset = DocumentSelector.get_base_queryset().filter(
            document_type=document_type
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        if latest_only:
            queryset = queryset.filter(is_latest=True)
        
        return queryset.order_by('-uploaded_at')
    
    @staticmethod
    def get_object_documents(
        related_object,
        document_type: Optional[str] = None,
        latest_only: bool = True
    ) -> QuerySet:
        """
        Get all documents linked to a specific object.
        
        This method uses generic foreign keys to retrieve documents
        linked to any model instance (LPO, Variation, Valuation, etc.)
        
        Args:
            related_object: Any model instance
            document_type: Filter by document type (optional)
            latest_only: Only return latest versions
        
        Returns:
            QuerySet of Document instances
        
        Example:
            # Get all documents attached to a variation order
            variation_docs = DocumentSelector.get_object_documents(
                related_object=variation_order
            )
            
            # Get only variation instruction documents
            instructions = DocumentSelector.get_object_documents(
                related_object=variation_order,
                document_type=Document.DocumentType.VARIATION_INSTRUCTION
            )
        """
        content_type = ContentType.objects.get_for_model(related_object)
        
        queryset = DocumentSelector.get_base_queryset().filter(
            content_type=content_type,
            object_id=related_object.id
        )
        
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        if latest_only:
            queryset = queryset.filter(is_latest=True)
        
        return queryset.order_by('-uploaded_at')
    
    @staticmethod
    def get_latest_versions() -> QuerySet:
        """
        Get all latest document versions.
        
        Returns:
            QuerySet of latest document versions
        """
        return DocumentSelector.get_base_queryset().filter(
            is_latest=True
        ).order_by('-uploaded_at')
    
    @staticmethod
    def get_document_with_versions(document_id: str) -> Optional[Document]:
        """
        Get a document with all its versions prefetched.
        
        Args:
            document_id: UUID of document
        
        Returns:
            Document instance with versions prefetched, or None
        """
        try:
            return DocumentSelector.get_base_queryset().prefetch_related(
                'next_versions',
                'next_versions__uploaded_by'
            ).get(id=document_id)
        except Document.DoesNotExist:
            return None
    
    @staticmethod
    def search_documents(
        query: str,
        project=None,
        organization=None,
        document_type: Optional[str] = None,
        latest_only: bool = True
    ) -> QuerySet:
        """
        Search documents by title, description, tags, or reference number.
        
        Args:
            query: Search query string
            project: Filter by project (optional)
            organization: Filter by organization (optional)
            document_type: Filter by document type (optional)
            latest_only: Only return latest versions
        
        Returns:
            QuerySet of matching documents
        
        Example:
            # Search for documents containing "cement"
            results = DocumentSelector.search_documents(
                query="cement",
                project=my_project
            )
        """
        queryset = DocumentSelector.get_base_queryset()
        
        # Search in multiple fields
        queryset = queryset.filter(
            Q(title__icontains=query) |
            Q(description__icontains=query) |
            Q(tags__icontains=query) |
            Q(reference_number__icontains=query)
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        if document_type:
            queryset = queryset.filter(document_type=document_type)
        
        if latest_only:
            queryset = queryset.filter(is_latest=True)
        
        return queryset.order_by('-uploaded_at')
    
    @staticmethod
    def get_recent_documents(
        limit: int = 10,
        project=None,
        organization=None,
        uploaded_by=None
    ) -> QuerySet:
        """
        Get most recently uploaded documents.
        
        Args:
            limit: Maximum number of documents to return
            project: Filter by project (optional)
            organization: Filter by organization (optional)
            uploaded_by: Filter by uploader (optional)
        
        Returns:
            QuerySet of recent documents
        """
        queryset = DocumentSelector.get_base_queryset().filter(
            is_latest=True
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        if uploaded_by:
            queryset = queryset.filter(uploaded_by=uploaded_by)
        
        return queryset.order_by('-uploaded_at')[:limit]
    
    @staticmethod
    def get_expiring_documents(
        days_ahead: int = 30,
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get documents expiring soon (for permits, licenses, etc.)
        
        Args:
            days_ahead: Number of days to look ahead
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of expiring documents
        """
        from django.utils import timezone
        from datetime import timedelta
        
        cutoff_date = timezone.now().date() + timedelta(days=days_ahead)
        
        queryset = DocumentSelector.get_base_queryset().filter(
            is_latest=True,
            expiry_date__isnull=False,
            expiry_date__lte=cutoff_date,
            expiry_date__gte=timezone.now().date()
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        return queryset.order_by('expiry_date')
    
    @staticmethod
    def get_confidential_documents(
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get all confidential documents.
        
        Args:
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of confidential documents
        """
        queryset = DocumentSelector.get_base_queryset().filter(
            is_latest=True,
            is_confidential=True
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        return queryset.order_by('-uploaded_at')
    
    @staticmethod
    def get_documents_by_extension(
        file_extension: str,
        project=None,
        organization=None
    ) -> QuerySet:
        """
        Get documents by file extension.
        
        Args:
            file_extension: File extension (e.g., 'pdf', 'dwg')
            project: Filter by project (optional)
            organization: Filter by organization (optional)
        
        Returns:
            QuerySet of documents with specified extension
        
        Example:
            # Get all CAD drawings
            cad_files = DocumentSelector.get_documents_by_extension(
                file_extension='dwg',
                project=my_project
            )
        """
        queryset = DocumentSelector.get_base_queryset().filter(
            is_latest=True,
            file_extension=file_extension.lower().strip('.')
        )
        
        if project:
            queryset = queryset.filter(project=project)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        return queryset.order_by('-uploaded_at')
