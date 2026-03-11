"""
Approval ViewSets
Handles ProjectApproval API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from datetime import date

from apps.approvals.models import ProjectApproval
from api.serializers.approvals import (
    ProjectApprovalSerializer, ProjectApprovalListSerializer
)


class ProjectApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProjectApproval model
    
    Provides CRUD operations for project approvals
    """
    queryset = ProjectApproval.objects.all().select_related('project')
    serializer_class = ProjectApprovalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'approval_type', 'status']
    search_fields = ['reference_number', 'notes', 'project__code', 'project__name']
    ordering_fields = ['issue_date', 'expiry_date', 'created_at']
    ordering = ['-issue_date']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ProjectApprovalListSerializer
        return ProjectApprovalSerializer
    
    @action(detail=False, methods=['get'])
    def expired(self, request):
        """Get all expired approvals"""
        today = date.today()
        expired = self.queryset.filter(expiry_date__lt=today, status='APPROVED')
        serializer = self.get_serializer(expired, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def expiring_soon(self, request):
        """Get approvals expiring within 30 days"""
        from datetime import timedelta
        today = date.today()
        threshold = today + timedelta(days=30)
        expiring = self.queryset.filter(
            expiry_date__gte=today,
            expiry_date__lte=threshold,
            status='APPROVED'
        )
        serializer = self.get_serializer(expiring, many=True)
        return Response(serializer.data)
