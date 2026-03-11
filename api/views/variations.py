"""
Variation Order API Views
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.variations.models import VariationOrder
from apps.variations import selectors
from apps.variations.services import VariationService
from api.serializers.variations import (
    VariationOrderSerializer,
    VariationOrderListSerializer,
    VariationOrderCreateSerializer,
    VariationSubmitSerializer,
    VariationApproveSerializer,
    VariationRejectSerializer,
    VariationCertifySerializer,
    ProjectVariationSummarySerializer,
    VariationTrendDataSerializer,
    PortfolioVariationSummarySerializer,
)


class VariationOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Variation Orders.
    
    Provides CRUD operations and workflow actions for variation orders.
    
    Endpoints:
    - GET /api/variations/ - List all variations
    - POST /api/variations/ - Create new variation
    - GET /api/variations/{id}/ - Get variation details
    - PUT /api/variations/{id}/ - Update variation
    - DELETE /api/variations/{id}/ - Delete variation
    - POST /api/variations/{id}/submit/ - Submit for approval
    - POST /api/variations/{id}/approve/ - Approve variation
    - POST /api/variations/{id}/reject/ - Reject variation
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    
    filterset_fields = ['status', 'priority', 'change_type', 'project']
    search_fields = ['reference_number', 'title', 'description', 'client_reference']
    ordering_fields = ['instruction_date', 'created_at', 'estimated_value', 'approved_value']
    ordering = ['-instruction_date']
    
    def get_queryset(self):
        """Get optimized queryset"""
        return VariationOrder.objects.select_related(
            'project',
            'project__organization',
            'created_by',
            'submitted_by',
            'approved_by'
        ).all()
    
    def get_serializer_class(self):
        """Return appropriate serializer based on action"""
        if self.action == 'list':
            return VariationOrderListSerializer
        elif self.action == 'create':
            return VariationOrderCreateSerializer
        return VariationOrderSerializer
    
    @extend_schema(
        summary="Submit variation for approval",
        description="Submit a draft variation for approval",
        request=VariationSubmitSerializer,
        responses={200: VariationOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='submit')
    def submit(self, request, pk=None):
        """
        POST /api/variations/{id}/submit/
        
        Submit variation for approval.
        """
        variation = self.get_object()
        
        serializer = VariationSubmitSerializer(
            data={'variation_id': pk},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_variation = serializer.save()
        
        return Response(
            VariationOrderSerializer(updated_variation).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Approve variation",
        description="Approve a submitted variation (updates project contract value)",
        request=VariationApproveSerializer,
        responses={200: VariationOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        POST /api/variations/{id}/approve/
        
        Approve variation and trigger financial impact.
        
        Body:
        {
            "approved_value": 1500000.00,  // Optional, defaults to estimated_value
            "notes": "Approval notes"       // Optional
        }
        """
        variation = self.get_object()
        
        serializer = VariationApproveSerializer(
            data={
                'variation_id': pk,
                **request.data
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_variation = serializer.save()
        
        return Response(
            VariationOrderSerializer(updated_variation).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Reject variation",
        description="Reject a submitted variation",
        request=VariationRejectSerializer,
        responses={200: VariationOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='reject')
    def reject(self, request, pk=None):
        """
        POST /api/variations/{id}/reject/
        
        Reject variation.
        
        Body:
        {
            "rejection_reason": "Exceeds budget constraints"
        }
        """
        variation = self.get_object()
        
        serializer = VariationRejectSerializer(
            data={
                'variation_id': pk,
                **request.data
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_variation = serializer.save()
        
        return Response(
            VariationOrderSerializer(updated_variation).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Certify variation",
        description="Certify variation by consultant (QS, Architect, Engineer)",
        request=VariationCertifySerializer,
        responses={200: VariationOrderSerializer}
    )
    @action(detail=True, methods=['post'], url_path='certify')
    def certify(self, request, pk=None):
        """
        POST /api/variations/{id}/certify/
        
        Certify variation by consultant.
        Certified amount may differ from approved value.
        
        Body:
        {
            "certified_amount": 1450000.00,  // Amount certified by consultant
            "notes": "Certification notes"    // Optional
        }
        """
        variation = self.get_object()
        
        serializer = VariationCertifySerializer(
            data={
                'variation_id': pk,
                **request.data
            },
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        updated_variation = serializer.save()
        
        return Response(
            VariationOrderSerializer(updated_variation).data,
            status=status.HTTP_200_OK
        )
    
    @extend_schema(
        summary="Get pending variations",
        description="Get all variations pending approval",
        responses={200: VariationOrderListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='pending')
    def pending(self, request):
        """
        GET /api/variations/pending/
        
        Get all pending variations across portfolio.
        """
        pending_variations = selectors.get_pending_variations()
        
        serializer = VariationOrderListSerializer(
            pending_variations,
            many=True
        )
        
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get portfolio variation summary",
        description="Get portfolio-wide variation statistics",
        responses={200: PortfolioVariationSummarySerializer}
    )
    @action(detail=False, methods=['get'], url_path='portfolio-summary')
    def portfolio_summary(self, request):
        """
        GET /api/variations/portfolio-summary/
        
        Get portfolio-wide variation summary.
        """
        summary = selectors.get_portfolio_variation_summary()
        
        serializer = PortfolioVariationSummarySerializer(summary)
        
        return Response(serializer.data)


class ProjectVariationViewSet(viewsets.GenericViewSet):
    """
    ViewSet for project-specific variation operations.
    
    Endpoints:
    - GET /api/projects/{id}/variations/ - Get project variations
    - GET /api/projects/{id}/variations/summary/ - Get project variation summary
    - GET /api/projects/{id}/variations/trend/ - Get variation trend data
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get project variations",
        description="Get all variation orders for a project",
        parameters=[
            OpenApiParameter(
                name='status',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by status'
            ),
            OpenApiParameter(
                name='priority',
                type=OpenApiTypes.STR,
                location=OpenApiParameter.QUERY,
                description='Filter by priority'
            ),
        ],
        responses={200: VariationOrderListSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='variations')
    def variations(self, request, pk=None):
        """
        GET /api/projects/{id}/variations/?status=SUBMITTED&priority=HIGH
        
        Get variations for a specific project with optional filters.
        """
        status_filter = request.query_params.get('status')
        priority_filter = request.query_params.get('priority')
        
        variations = selectors.get_project_variations(
            project_id=pk,
            status=status_filter,
            priority=priority_filter
        )
        
        serializer = VariationOrderListSerializer(variations, many=True)
        
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get project variation summary",
        description="Get comprehensive variation summary for a project",
        responses={200: ProjectVariationSummarySerializer}
    )
    @action(detail=True, methods=['get'], url_path='variations/summary')
    def variation_summary(self, request, pk=None):
        """
        GET /api/projects/{id}/variations/summary/
        
        Get variation summary metrics for a project.
        """
        summary = selectors.get_project_variation_summary(project_id=pk)
        
        # Remove project object from summary for serialization
        summary_data = {k: v for k, v in summary.items() if k != 'project'}
        
        serializer = ProjectVariationSummarySerializer(summary_data)
        
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get variation trend data",
        description="Get monthly variation trend data for charting",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of months (default: 6)'
            ),
        ],
        responses={200: VariationTrendDataSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='variations/trend')
    def variation_trend(self, request, pk=None):
        """
        GET /api/projects/{id}/variations/trend/?months=12
        
        Get monthly variation trend data.
        """
        months = int(request.query_params.get('months', 6))
        
        trend_data = selectors.get_variation_trend_data(
            project_id=pk,
            months=months
        )
        
        serializer = VariationTrendDataSerializer(trend_data, many=True)
        
        return Response(serializer.data)
