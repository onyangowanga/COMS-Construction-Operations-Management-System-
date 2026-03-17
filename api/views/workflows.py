"""
Workflow ViewSets
Handles Approval and ProjectActivity API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend

from apps.workflows.models import Approval, ProjectActivity
from api.serializers.workflows import (
    ApprovalSerializer, ApprovalListSerializer,
    ProjectActivitySerializer, ProjectActivityListSerializer,
    WorkflowTransitionRequestSerializer,
)
from api.services.approval_workflow import (
    approve_request, reject_request, ApprovalWorkflowError
)
from apps.workflows.services import WorkflowEngineService, WorkflowEngineError


class ApprovalViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Approval model
    
    Provides CRUD operations and approval actions
    """
    queryset = Approval.objects.all().select_related('requested_by', 'approved_by')
    serializer_class = ApprovalSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['approval_type', 'status', 'requested_by', 'approved_by']
    search_fields = ['reason', 'notes']
    ordering_fields = ['requested_at', 'approved_at', 'amount']
    ordering = ['-requested_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ApprovalListSerializer
        return ApprovalSerializer
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve an approval request
        
        Body params:
            notes (optional): Approval notes
        """
        approval = self.get_object()
        notes = request.data.get('notes', '')
        
        try:
            result = approve_request(
                approval=approval,
                approved_by=request.user,
                notes=notes
            )
            return Response(result, status=status.HTTP_200_OK)
        except ApprovalWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        Reject an approval request
        
        Body params:
            reason: Reason for rejection
        """
        approval = self.get_object()
        reason = request.data.get('reason', '')
        
        try:
            result = reject_request(
                approval=approval,
                rejected_by=request.user,
                reason=reason
            )
            return Response(result, status=status.HTTP_200_OK)
        except ApprovalWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """
        Get all pending approvals
        """
        from api.services.approval_workflow import get_pending_approvals
        
        approvals = get_pending_approvals()
        serializer = self.get_serializer(approvals, many=True)
        return Response(serializer.data)


class ProjectActivityViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for ProjectActivity model
    
    Read-only endpoint for activity timeline
    """
    queryset = ProjectActivity.objects.all().select_related('performed_by')
    serializer_class = ProjectActivitySerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project_id', 'activity_type', 'performed_by']
    search_fields = ['description']
    ordering_fields = ['created_at', 'amount']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ProjectActivityListSerializer
        return ProjectActivitySerializer


class WorkflowStateAPIView(APIView):
    """Read workflow state and available transitions for a module entity."""

    permission_classes = [IsAuthenticated]

    def get(self, request, module: str, entity_id: str):
        try:
            snapshot = WorkflowEngineService.get_workflow_snapshot(
                user=request.user,
                module=module,
                entity_id=entity_id,
            )
            return Response(snapshot, status=status.HTTP_200_OK)
        except WorkflowEngineError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)


class WorkflowTransitionAPIView(APIView):
    """Apply a workflow transition to a module entity."""

    permission_classes = [IsAuthenticated]

    def post(self, request, module: str, entity_id: str):
        serializer = WorkflowTransitionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            WorkflowEngineService.perform_transition(
                user=request.user,
                module=module,
                entity_id=entity_id,
                action=serializer.validated_data['action'],
                comment=serializer.validated_data.get('comment', ''),
                payload=serializer.validated_data.get('payload', {}),
            )
            snapshot = WorkflowEngineService.get_workflow_snapshot(
                user=request.user,
                module=module,
                entity_id=entity_id,
            )
            return Response(snapshot, status=status.HTTP_200_OK)
        except WorkflowEngineError as exc:
            return Response({'detail': str(exc)}, status=status.HTTP_400_BAD_REQUEST)
