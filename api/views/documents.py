"""
Document Management System - API Views

RESTful API endpoints for document operations including:
- Document CRUD
- Version management
- Search and filtering
- Project-specific endpoints
- Object-specific endpoints
- Statistics
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter, OpenApiResponse

from apps.documents.models import Document
from apps.documents.selectors import DocumentSelector
from apps.documents.services import DocumentService
from api.serializers.documents import (
    DocumentSerializer,
    DocumentListSerializer,
    DocumentUploadSerializer,
    DocumentVersionSerializer,
    DocumentUpdateSerializer,
    DocumentStatsSerializer,
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document operations.
    
    Provides complete CRUD and supports:
    - File uploads
    - Version management
    - Search across multiple fields
    - Filtering by type, project, confidentiality
    - Generic object linking
    
    Endpoints:
        GET    /api/documents/              List documents
        POST   /api/documents/              Upload new document
        GET    /api/documents/{id}/         Get document details
        PUT    /api/documents/{id}/         Update document metadata
        PATCH  /api/documents/{id}/         Partial update
        DELETE /api/documents/{id}/         Delete document
        POST   /api/documents/{id}/version/ Create new version
        GET    /api/documents/{id}/history/ Get version history
        GET    /api/documents/stats/        Get statistics
        GET    /api/documents/recent/       Get recent documents
        GET    /api/documents/expiring/     Get expiring documents
    """
    
    queryset = DocumentSelector.get_base_queryset()
    serializer_class = DocumentSerializer
    parser_classes = (MultiPartParser, FormParser)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = [
        'project',
        'document_type',
        'uploaded_by',
        'is_latest',
        'is_confidential',
        'file_extension',
    ]
    search_fields = ['title', 'description', 'tags', 'reference_number']
    ordering_fields = ['uploaded_at', 'title', 'file_size', 'version']
    ordering = ['-uploaded_at']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'list':
            return DocumentListSerializer
        elif self.action == 'create':
            return DocumentUploadSerializer
        elif self.action in ['update', 'partial_update']:
            return DocumentUpdateSerializer
        elif self.action == 'create_version':
            return DocumentVersionSerializer
        return DocumentSerializer
    
    def get_queryset(self):
        """Filter queryset based on user permissions"""
        queryset = super().get_queryset()
        
        # Filter by project if provided
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter confidential documents based on permissions
        # (Add your permission logic here)
        
        return queryset
    
    @extend_schema(
        summary="Upload new document",
        description="Upload a new document with metadata",
        request=DocumentUploadSerializer,
        responses={201: DocumentSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Upload new document"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        
        # Return full document data
        output_serializer = DocumentSerializer(
            document,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Update document metadata",
        description="Update document metadata without changing the file",
        request=DocumentUpdateSerializer,
        responses={200: DocumentSerializer}
    )
    def update(self, request, *args, **kwargs):
        """Update document metadata"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        document = serializer.save()
        
        # Return full document data
        output_serializer = DocumentSerializer(
            document,
            context={'request': request}
        )
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Create new document version",
        description="Upload a new version of an existing document",
        request=DocumentVersionSerializer,
        responses={201: DocumentSerializer}
    )
    @action(detail=True, methods=['post'], url_path='version')
    def create_version(self, request, pk=None):
        """
        POST /api/documents/{id}/version/
        
        Create new version of document.
        
        Body:
        {
            "file": <file>,
            "notes": "Updated pricing to reflect market changes"
        }
        """
        document = self.get_object()
        
        serializer = DocumentVersionSerializer(
            data=request.data,
            context={'request': request, 'document_id': pk}
        )
        serializer.is_valid(raise_exception=True)
        new_version = serializer.save()
        
        # Return full document data
        output_serializer = DocumentSerializer(
            new_version,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Get version history",
        description="Get all versions of this document in chronological order",
        responses={200: DocumentSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='history')
    def version_history(self, request, pk=None):
        """
        GET /api/documents/{id}/history/
        
        Get complete version history.
        
        Response:
        [
            {
                "id": "...",
                "title": "Contract Document",
                "version": 1,
                "uploaded_at": "2026-01-01T10:00:00Z",
                "version_notes": ""
            },
            {
                "id": "...",
                "title": "Contract Document",
                "version": 2,
                "uploaded_at": "2026-02-15T14:30:00Z",
                "version_notes": "Updated pricing"
            }
        ]
        """
        document = self.get_object()
        versions = document.get_version_history()
        
        serializer = DocumentSerializer(
            versions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get document statistics",
        description="Get document statistics for the current user's organization",
        responses={200: DocumentStatsSerializer}
    )
    @action(detail=False, methods=['get'], url_path='stats')
    def statistics(self, request):
        """
        GET /api/documents/stats/
        
        Get document statistics.
        
        Query params:
        - project: Filter by project ID
        
        Response:
        {
            "total_documents": 1450,
            "total_size_bytes": 5894563200,
            "total_size_mb": 5621.25,
            "counts_by_type": {
                "CONTRACT": 12,
                "DRAWING": 245,
                "LPO_ATTACHMENT": 567,
                ...
            },
            "confidential_count": 28
        }
        """
        project_id = request.query_params.get('project')
        project = None
        
        if project_id:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        stats = DocumentService.get_document_stats(
            project=project,
            organization=request.user.organization
        )
        
        serializer = DocumentStatsSerializer(stats)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get recent documents",
        description="Get most recently uploaded documents",
        parameters=[
            OpenApiParameter(
                name='limit',
                type=int,
                default=10,
                description='Number of documents to return'
            ),
            OpenApiParameter(
                name='project',
                type=str,
                description='Filter by project ID'
            ),
        ],
        responses={200: DocumentListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='recent')
    def recent(self, request):
        """
        GET /api/documents/recent/
        
        Get recently uploaded documents.
        
        Query params:
        - limit: Number of documents (default: 10)
        - project: Filter by project ID
        """
        limit = int(request.query_params.get('limit', 10))
        project_id = request.query_params.get('project')
        project = None
        
        if project_id:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        documents = DocumentSelector.get_recent_documents(
            limit=limit,
            project=project,
            organization=request.user.organization
        )
        
        serializer = DocumentListSerializer(
            documents,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get expiring documents",
        description="Get documents expiring soon (permits, licenses, etc.)",
        parameters=[
            OpenApiParameter(
                name='days_ahead',
                type=int,
                default=30,
                description='Number of days to look ahead'
            ),
            OpenApiParameter(
                name='project',
                type=str,
                description='Filter by project ID'
            ),
        ],
        responses={200: DocumentListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='expiring')
    def expiring(self, request):
        """
        GET /api/documents/expiring/
        
        Get documents expiring soon.
        
        Query params:
        - days_ahead: Days to look ahead (default: 30)
        - project: Filter by project ID
        """
        days_ahead = int(request.query_params.get('days_ahead', 30))
        project_id = request.query_params.get('project')
        project = None
        
        if project_id:
            from apps.projects.models import Project
            try:
                project = Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        documents = DocumentSelector.get_expiring_documents(
            days_ahead=days_ahead,
            project=project,
            organization=request.user.organization
        )
        
        serializer = DocumentListSerializer(
            documents,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ProjectDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for project-specific document access.
    
    Nested under projects endpoint:
        GET /api/projects/{project_id}/documents/
    """
    serializer_class = DocumentListSerializer
    
    def get_queryset(self):
        """Get documents for specific project"""
        project_id = self.kwargs.get('project_pk')
        return DocumentSelector.get_project_documents(
            project_id=project_id,
            latest_only=True
        )


class ObjectDocumentViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Read-only viewset for object-specific document access.
    
    Access documents linked to any object via generic foreign key:
        GET /api/documents/object/{content_type}/{object_id}/
    
    Example:
        GET /api/documents/object/lpo/abc-123-uuid/
        GET /api/documents/object/variation/xyz-456-uuid/
    """
    serializer_class = DocumentListSerializer
    
    def get_queryset(self):
        """Get documents for specific object"""
        from django.contrib.contenttypes.models import ContentType
        
        content_type_name = self.kwargs.get('content_type')
        object_id = self.kwargs.get('object_id')
        
        try:
            content_type = ContentType.objects.get(model=content_type_name.lower())
            model_class = content_type.model_class()
            related_object = model_class.objects.get(id=object_id)
            
            return DocumentSelector.get_object_documents(
                related_object=related_object,
                latest_only=True
            )
        except (ContentType.DoesNotExist, model_class.DoesNotExist):
            return Document.objects.none()

