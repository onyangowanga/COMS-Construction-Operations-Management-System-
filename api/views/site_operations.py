"""
Site Operations API ViewSets

API endpoints for:
- Daily Site Reports
- Material Deliveries
- Site Issues
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.site_operations.models import (
    DailySiteReport,
    MaterialDelivery,
    SiteIssue
)
from apps.site_operations.services import SiteOperationsService
from apps.site_operations.statOperatios_selectors import (
    get_project_site_reports,
    get_site_report_by_id,
    get_project_material_deliveries,
    get_material_delivery_by_id,
    get_project_site_issues,
    get_site_issue_by_id,
    get_site_operations_summary
)
from api.serializers.site_operations import (
    DailySiteReportListSerializer,
    DailySiteReportSerializer,
    DailySiteReportCreateSerializer,
    DailySiteReportUpdateSerializer,
    MaterialDeliveryListSerializer,
    MaterialDeliverySerializer,
    MaterialDeliveryCreateSerializer,
    MaterialDeliveryStatusUpdateSerializer,
    SiteIssueListSerializer,
    SiteIssueSerializer,
    SiteIssueCreateSerializer,
    SiteIssueUpdateSerializer,
    SiteIssueResolveSerializer,
    SiteIssueReopenSerializer,
    SiteOperationsSummarySerializer
)


class DailySiteReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing daily site reports
    
    Endpoints:
    - GET /api/site-reports/ - List all reports
    - POST /api/site-reports/ - Create new report
    - GET /api/site-reports/{id}/ - Get report details
    - PUT/PATCH /api/site-reports/{id}/ - Update report
    - DELETE /api/site-reports/{id}/ - Delete report
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'weather', 'report_date', 'prepared_by']
    search_fields = ['work_completed', 'labour_summary', 'issues']
    ordering_fields = ['report_date', 'created_at']
    ordering = ['-report_date']
    
    def get_queryset(self):
        return DailySiteReport.objects.select_related(
            'project',
            'prepared_by'
        ).all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return DailySiteReportListSerializer
        elif self.action == 'create':
            return DailySiteReportCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return DailySiteReportUpdateSerializer
        return DailySiteReportSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new site report"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            report = SiteOperationsService.create_site_report(
                project_id=str(serializer.validated_data['project_id']),
                report_date=serializer.validated_data['report_date'],
                weather=serializer.validated_data['weather'],
                labour_summary=serializer.validated_data['labour_summary'],
                work_completed=serializer.validated_data['work_completed'],
                materials_delivered=serializer.validated_data.get('materials_delivered', ''),
                issues=serializer.validated_data.get('issues', ''),
                prepared_by_id=str(request.user.id)
            )
            
            output_serializer = DailySiteReportSerializer(report)
            return Response(output_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def update(self, request, *args, **kwargs):
        """Update an existing site report"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_report = SiteOperationsService.update_site_report(
            report_id=str(instance.id),
            **serializer.validated_data
        )
        
        output_serializer = DailySiteReportSerializer(updated_report)
        return Response(output_serializer.data)


class MaterialDeliveryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing material deliveries
    
    Endpoints:
    - GET /api/material-deliveries/ - List all deliveries
    - POST /api/material-deliveries/ - Create new delivery
    - GET /api/material-deliveries/{id}/ - Get delivery details
    - PUT/PATCH /api/material-deliveries/{id}/ - Update delivery
    - DELETE /api/material-deliveries/{id}/ - Delete delivery
    - POST /api/material-deliveries/{id}/update-status/ - Update delivery status
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'supplier', 'status', 'delivery_date']
    search_fields = ['material_name', 'delivery_note_number', 'supplier_name']
    ordering_fields = ['delivery_date', 'created_at']
    ordering = ['-delivery_date']
    
    def get_queryset(self):
        return MaterialDelivery.objects.select_related(
            'project',
            'supplier',
            'received_by'
        ).all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return MaterialDeliveryListSerializer
        elif self.action == 'create':
            return MaterialDeliveryCreateSerializer
        elif self.action == 'update_status':
            return MaterialDeliveryStatusUpdateSerializer
        return MaterialDeliverySerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new material delivery record"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        delivery = SiteOperationsService.create_material_delivery(
            project_id=str(serializer.validated_data['project_id']),
            material_name=serializer.validated_data['material_name'],
            quantity=serializer.validated_data['quantity'],
            delivery_note_number=serializer.validated_data['delivery_note_number'],
            delivery_date=serializer.validated_data['delivery_date'],
            received_by_id=str(request.user.id),
            unit=serializer.validated_data.get('unit', 'units'),
            supplier_id=str(serializer.validated_data['supplier_id']) if serializer.validated_data.get('supplier_id') else None,
            supplier_name=serializer.validated_data.get('supplier_name', ''),
            status=serializer.validated_data.get('status', 'PENDING'),
            notes=serializer.validated_data.get('notes', '')
        )
        
        output_serializer = MaterialDeliverySerializer(delivery)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        request=MaterialDeliveryStatusUpdateSerializer,
        responses={200: MaterialDeliverySerializer}
    )
    @action(detail=True, methods=['post'])
    def update_status(self, request, pk=None):
        """Update delivery status (accept/reject/partial)"""
        delivery = self.get_object()
        serializer = MaterialDeliveryStatusUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        updated_delivery = SiteOperationsService.update_delivery_status(
            delivery_id=str(delivery.id),
            status=serializer.validated_data['status'],
            notes=serializer.validated_data.get('notes')
        )
        
        output_serializer = MaterialDeliverySerializer(updated_delivery)
        return Response(output_serializer.data)


class SiteIssueViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing site issues
    
    Endpoints:
    - GET /api/site-issues/ - List all issues
    - POST /api/site-issues/ - Create new issue
    - GET /api/site-issues/{id}/ - Get issue details
    - PUT/PATCH /api/site-issues/{id}/ - Update issue
    - DELETE /api/site-issues/{id}/ - Delete issue
    - POST /api/site-issues/{id}/resolve/ - Mark issue as resolved
    - POST /api/site-issues/{id}/reopen/ - Reopen a resolved issue
    """
    
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = ['project', 'severity', 'status', 'assigned_to']
    search_fields = ['title', 'description']
    ordering_fields = ['severity', 'reported_date', 'status']
    ordering = ['-severity', '-reported_date']
    
    def get_queryset(self):
        return SiteIssue.objects.select_related(
            'project',
            'reported_by',
            'assigned_to'
        ).all()
    
    def get_serializer_class(self):
        if self.action == 'list':
            return SiteIssueListSerializer
        elif self.action == 'create':
            return SiteIssueCreateSerializer
        elif self.action in ['update', 'partial_update']:
            return SiteIssueUpdateSerializer
        elif self.action == 'resolve':
            return SiteIssueResolveSerializer
        elif self.action == 'reopen':
            return SiteIssueReopenSerializer
        return SiteIssueSerializer
    
    def create(self, request, *args, **kwargs):
        """Create a new site issue"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        issue = SiteOperationsService.create_site_issue(
            project_id=str(serializer.validated_data['project_id']),
            title=serializer.validated_data['title'],
            description=serializer.validated_data['description'],
            severity=serializer.validated_data.get('severity', 'MEDIUM'),
            reported_by_id=str(request.user.id),
            assigned_to_id=str(serializer.validated_data['assigned_to_id']) if serializer.validated_data.get('assigned_to_id') else None,
            status=serializer.validated_data.get('status', 'OPEN')
        )
        
        output_serializer = SiteIssueSerializer(issue)
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    def update(self, request, *args, **kwargs):
        """Update an existing site issue"""
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        
        updated_issue = SiteOperationsService.update_site_issue(
            issue_id=str(instance.id),
            **serializer.validated_data
        )
        
        output_serializer = SiteIssueSerializer(updated_issue)
        return Response(output_serializer.data)
    
    @extend_schema(
        request=SiteIssueResolveSerializer,
        responses={200: SiteIssueSerializer}
    )
    @action(detail=True, methods=['post'])
    def resolve(self, request, pk=None):
        """Mark an issue as resolved"""
        issue = self.get_object()
        serializer = SiteIssueResolveSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        resolved_issue = SiteOperationsService.resolve_site_issue(
            issue_id=str(issue.id),
            resolution_notes=serializer.validated_data['resolution_notes']
        )
        
        output_serializer = SiteIssueSerializer(resolved_issue)
        return Response(output_serializer.data)
    
    @extend_schema(
        request=SiteIssueReopenSerializer,
        responses={200: SiteIssueSerializer}
    )
    @action(detail=True, methods=['post'])
    def reopen(self, request, pk=None):
        """Reopen a resolved issue"""
        issue = self.get_object()
        serializer = SiteIssueReopenSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reopened_issue = SiteOperationsService.reopen_site_issue(
            issue_id=str(issue.id),
            reason=serializer.validated_data['reason']
        )
        
        output_serializer = SiteIssueSerializer(reopened_issue)
        return Response(output_serializer.data)
