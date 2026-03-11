"""
Valuation ViewSets
Handles Valuation and BQItemProgress API endpoints
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.valuations.models import Valuation, BQItemProgress
from apps.valuations.services import ValuationService
from apps.valuations.selectors import (
    get_project_valuations,
    get_valuation_by_id,
    get_latest_valuation,
    get_valuation_summary,
    get_bq_progress_summary
)
from api.serializers.valuations import (
    ValuationSerializer,
    ValuationListSerializer,
    ValuationCreateSerializer,
    ValuationUpdateSerializer,
    ValuationApprovalSerializer,
    ValuationRejectSerializer,
    ValuationPaymentSerializer,
    ValuationSummarySerializer,
    BQItemProgressSerializer
)


class ValuationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Valuation model
    
    Provides CRUD operations and custom actions for valuations
    """
    queryset = Valuation.objects.all().select_related(
        'project',
        'submitted_by',
        'approved_by'
    ).prefetch_related('item_progress')
    serializer_class = ValuationSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'status', 'valuation_date']
    search_fields = ['valuation_number', 'project__name', 'project__code']
    ordering_fields = ['valuation_date', 'created_at', 'amount_due']
    ordering = ['-valuation_date', '-valuation_number']
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return ValuationListSerializer
        elif self.action == 'create':
            return ValuationCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return ValuationUpdateSerializer
        elif self.action == 'approve':
            return ValuationApprovalSerializer
        elif self.action == 'reject':
            return ValuationRejectSerializer
        elif self.action == 'mark_paid':
            return ValuationPaymentSerializer
        return ValuationSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new valuation using service layer"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            valuation = ValuationService.create_valuation(
                project_id=str(serializer.validated_data['project_id']),
                valuation_date=serializer.validated_data['valuation_date'],
                progress_items=[
                    {
                        'bq_item_id': str(item['bq_item_id']),
                        'this_quantity': item['this_quantity'],
                        'notes': item.get('notes', '')
                    }
                    for item in serializer.validated_data['progress_items']
                ],
                retention_percentage=serializer.validated_data.get('retention_percentage'),
                notes=serializer.validated_data.get('notes', ''),
                submitted_by_id=str(request.user.id) if request.user.is_authenticated else None
            )
            
            output_serializer = ValuationSerializer(valuation)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update an existing valuation using service layer"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        try:
            # Prepare progress items if provided
            progress_items = None
            if 'progress_items' in serializer.validated_data:
                progress_items = [
                    {
                        'bq_item_id': str(item['bq_item_id']),
                        'this_quantity': item['this_quantity'],
                        'notes': item.get('notes', '')
                    }
                    for item in serializer.validated_data['progress_items']
                ]
            
            valuation = ValuationService.update_valuation(
                valuation_id=str(instance.id),
                progress_items=progress_items,
                retention_percentage=serializer.validated_data.get('retention_percentage'),
                notes=serializer.validated_data.get('notes'),
                status=serializer.validated_data.get('status')
            )
            
            output_serializer = ValuationSerializer(valuation)
            return Response(output_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        request=ValuationApprovalSerializer,
        responses={200: ValuationSerializer}
    )
    @action(detail=True, methods=['post'])
    def approve(self, request, pk=None):
        """Approve a valuation"""
        valuation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            approved_valuation = ValuationService.approve_valuation(
                valuation_id=str(valuation.id),
                approved_by_id=str(serializer.validated_data['approved_by_id'])
            )
            
            output_serializer = ValuationSerializer(approved_valuation)
            return Response(output_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        request=ValuationRejectSerializer,
        responses={200: ValuationSerializer}
    )
    @action(detail=True, methods=['post'])
    def reject(self, request, pk=None):
        """Reject a valuation"""
        valuation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            rejected_valuation = ValuationService.reject_valuation(
                valuation_id=str(valuation.id),
                notes=serializer.validated_data['notes']
            )
            
            output_serializer = ValuationSerializer(rejected_valuation)
            return Response(output_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        request=ValuationPaymentSerializer,
        responses={200: ValuationSerializer}
    )
    @action(detail=True, methods=['post'])
    def mark_paid(self, request, pk=None):
        """Mark valuation as paid"""
        valuation = self.get_object()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            paid_valuation = ValuationService.mark_as_paid(
                valuation_id=str(valuation.id),
                payment_date=serializer.validated_data['payment_date']
            )
            
            output_serializer = ValuationSerializer(paid_valuation)
            return Response(output_serializer.data)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @extend_schema(
        responses={200: dict}
    )
    @action(detail=True, methods=['get'])
    def report_data(self, request, pk=None):
        """Get all data needed for generating a valuation report"""
        valuation = self.get_object()
        
        try:
            report_data = ValuationService.get_valuation_report_data(
                valuation_id=str(valuation.id)
            )
            
            # Serialize the data
            from api.serializers.projects import ProjectSerializer
            from apps.valuations.selectors import get_valuation_items_grouped
            
            output = {
                'valuation': ValuationSerializer(report_data['valuation']).data,
                'project': ProjectSerializer(report_data['project']).data,
                'summary': report_data['summary'],
                'items_grouped': get_valuation_items_grouped(str(valuation.id))
            }
            
            return Response(output)
            
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class BQItemProgressViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for BQItemProgress model
    Read-only - progress is created/updated via Valuation endpoints
    """
    queryset = BQItemProgress.objects.all().select_related(
        'valuation__project',
        'bq_item__element__section'
    )
    serializer_class = BQItemProgressSerializer
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['valuation', 'bq_item']
    ordering = ['valuation__valuation_date', 'bq_item__element__section__order']


# Custom actions for Project ViewSet (to be added to projects.py)
def project_valuations_action(self, request, pk=None):
    """
    Get all valuations for a project
    Add this to ProjectViewSet in api/views/projects.py
    """
    project = self.get_object()
    valuations = get_project_valuations(str(project.id))
    serializer = ValuationListSerializer(valuations, many=True)
    return Response(serializer.data)


def project_valuation_summary_action(self, request, pk=None):
    """
    Get valuation summary for a project
    Add this to ProjectViewSet in api/views/projects.py
    """
    project = self.get_object()
    summary = get_valuation_summary(str(project.id))
    serializer = ValuationSummarySerializer(summary)
    return Response(serializer.data)


def project_bq_progress_action(self, request, pk=None):
    """
    Get BQ progress summary for a project
    Add this to ProjectViewSet in api/views/projects.py
    """
    project = self.get_object()
    progress = get_bq_progress_summary(str(project.id))
    return Response(progress)
