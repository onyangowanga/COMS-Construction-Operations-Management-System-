"""
Document ViewSets
Handles Document and DocumentVersion API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.documents.models import Document, DocumentVersion
from api.serializers.documents import (
    DocumentSerializer, DocumentListSerializer, DocumentVersionSerializer
)


class DocumentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Document model
    
    Provides CRUD operations for documents
    """
    queryset = Document.objects.all().select_related('project', 'uploaded_by').prefetch_related('versions')
    serializer_class = DocumentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'document_type', 'uploaded_by']
    search_fields = ['name', 'description', 'project__code', 'project__name']
    ordering_fields = ['created_at', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return DocumentListSerializer
        return DocumentSerializer
    
    @action(detail=True, methods=['get'])
    def versions(self, request, pk=None):
        """Get all versions for a document"""
        document = self.get_object()
        versions = document.versions.all().order_by('-created_at')
        serializer = DocumentVersionSerializer(versions, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def latest_version(self, request, pk=None):
        """Get the latest version of a document"""
        document = self.get_object()
        latest = document.latest_version
        if latest:
            serializer = DocumentVersionSerializer(latest)
            return Response(serializer.data)
        return Response({'detail': 'No versions available for this document'}, status=404)


class DocumentVersionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DocumentVersion model
    
    Provides CRUD operations for document versions
    """
    queryset = DocumentVersion.objects.all().select_related('document', 'uploaded_by')
    serializer_class = DocumentVersionSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['document', 'is_latest', 'uploaded_by']
    search_fields = ['version_number', 'notes', 'document__name']
    ordering_fields = ['created_at', 'version_number']
    ordering = ['-created_at']
