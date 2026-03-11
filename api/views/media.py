"""
Media ViewSets
Handles ProjectPhoto API endpoints
"""
from rest_framework import viewsets, filters
from django_filters.rest_framework import DjangoFilterBackend

from apps.media.models import ProjectPhoto
from api.serializers.media import ProjectPhotoSerializer, ProjectPhotoListSerializer


class ProjectPhotoViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProjectPhoto model
    
    Provides CRUD operations for project photos
    """
    queryset = ProjectPhoto.objects.all().select_related('project', 'stage', 'uploaded_by')
    serializer_class = ProjectPhotoSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'stage', 'uploaded_by', 'uploaded_at']
    search_fields = ['caption', 'project__code', 'project__name']
    ordering_fields = ['uploaded_at', 'created_at']
    ordering = ['-uploaded_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ProjectPhotoListSerializer
        return ProjectPhotoSerializer
