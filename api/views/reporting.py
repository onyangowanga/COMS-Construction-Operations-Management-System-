"""
Reporting Engine - API Views

RESTful API endpoints for report management and execution.
"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from drf_spectacular.utils import extend_schema, OpenApiParameter

from apps.reporting.models import Report, ReportSchedule, ReportExecution, ReportWidget
from apps.reporting.selectors import ReportSelector, ReportExecutionSelector, DashboardWidgetDataSelector
from api.serializers.reporting import (
    ReportSerializer,
    ReportCreateSerializer,
    ReportExecutionSerializer,
    ReportExecuteSerializer,
    ReportScheduleSerializer,
    ReportScheduleCreateSerializer,
    ReportWidgetSerializer,
    ReportWidgetDataSerializer
)


class ReportViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report management.
    
    Endpoints:
        GET    /api/reports/              List all reports
        POST   /api/reports/              Create new report
        GET    /api/reports/{id}/         Get report details
        PUT    /api/reports/{id}/         Update report
        DELETE /api/reports/{id}/         Delete report
        POST   /api/reports/{id}/execute/ Execute report
        GET    /api/reports/{id}/executions/ Get execution history
    """
    
    queryset = ReportSelector.get_base_queryset()
    serializer_class = ReportSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['report_type', 'is_active', 'is_public']
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'create':
            return ReportCreateSerializer
        elif self.action == 'execute':
            return ReportExecuteSerializer
        return ReportSerializer
    
    def get_queryset(self):
        """Filter by organization"""
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(organization=user.organization)
    
    @extend_schema(
        summary="Create new report",
        request=ReportCreateSerializer,
        responses={201: ReportSerializer}
    )
    def create(self, request, *args, **kwargs):
        """Create new report configuration"""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        report = serializer.save()
        
        output_serializer = ReportSerializer(report, context={'request': request})
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)
    
    @extend_schema(
        summary="Execute report",
        request=ReportExecuteSerializer,
        responses={200: ReportExecutionSerializer}
    )
    @action(detail=True, methods=['post'], url_path='execute')
    def execute(self, request, pk=None):
        """
        POST /api/reports/{id}/execute/
        
        Execute a report with given parameters.
        
        Body:
        {
            "parameters": {
                "project_id": "uuid",
                "start_date": "2026-01-01",
                "end_date": "2026-03-31"
            },
            "export_format": "PDF",
            "use_cache": true
        }
        """
        report = self.get_object()
        
        serializer = ReportExecuteSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        execution = serializer.execute(
            report=report,
            executed_by=request.user
        )
        
        output_serializer = ReportExecutionSerializer(
            execution,
            context={'request': request}
        )
        return Response(output_serializer.data)
    
    @extend_schema(
        summary="Get execution history",
        responses={200: ReportExecutionSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='executions')
    def executions(self, request, pk=None):
        """
        GET /api/reports/{id}/executions/
        
        Get execution history for this report.
        """
        report = self.get_object()
        
        executions = ReportExecutionSelector.get_recent_executions(
            report=report,
            limit=20
        )
        
        serializer = ReportExecutionSerializer(
            executions,
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class ReportExecutionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing report execution history.
    
    Endpoints:
        GET /api/report-executions/     List all executions
        GET /api/report-executions/{id}/ Get execution details
    """
    
    queryset = ReportExecutionSelector.get_base_queryset()
    serializer_class = ReportExecutionSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'status', 'export_format']
    ordering_fields = ['created_at', 'execution_time']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """Filter by organization"""
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(report__organization=user.organization)


class ReportScheduleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Report Schedule management.
    
    Endpoints:
        GET    /api/report-schedules/        List all schedules
        POST   /api/report-schedules/        Create new schedule
        GET    /api/report-schedules/{id}/   Get schedule details
        PUT    /api/report-schedules/{id}/   Update schedule
        DELETE /api/report-schedules/{id}/   Delete schedule
    """
    
    queryset = ReportSchedule.objects.select_related(
        'report',
        'created_by'
    ).prefetch_related('executions')
    serializer_class = ReportScheduleSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['report', 'frequency', 'is_active']
    ordering_fields = ['next_run', 'created_at']
    ordering = ['next_run']
    
    def get_serializer_class(self):
        """Use appropriate serializer based on action"""
        if self.action == 'create':
            return ReportScheduleCreateSerializer
        return ReportScheduleSerializer
    
    def get_queryset(self):
        """Filter by organization"""
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(report__organization=user.organization)
    
    def create(self, request, *args, **kwargs):
        """Create new schedule"""
        report_id = request.data.get('report_id')
        if not report_id:
            return Response(
                {'error': 'report_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(
            data=request.data,
            context={'request': request, 'report_id': report_id}
        )
        serializer.is_valid(raise_exception=True)
        schedule = serializer.save()
        
        output_serializer = ReportScheduleSerializer(
            schedule,
            context={'request': request}
        )
        return Response(output_serializer.data, status=status.HTTP_201_CREATED)


class ReportWidgetViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Dashboard Widget management.
    
    Endpoints:
        GET    /api/widgets/           List all widgets
        POST   /api/widgets/           Create new widget
        GET    /api/widgets/{id}/      Get widget details
        PUT    /api/widgets/{id}/      Update widget
        DELETE /api/widgets/{id}/      Delete widget
        GET    /api/widgets/{id}/data/ Get widget data
    """
    
    queryset = ReportWidget.objects.select_related(
        'organization',
        'report',
        'created_by'
    )
    serializer_class = ReportWidgetSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['widget_type', 'is_active']
    ordering_fields = ['display_order', 'name']
    ordering = ['display_order']
    
    def get_queryset(self):
        """Filter by organization"""
        queryset = super().get_queryset()
        user = self.request.user
        return queryset.filter(organization=user.organization, is_active=True)
    
    def perform_create(self, serializer):
        """Set organization and created_by on creation"""
        serializer.save(
            organization=self.request.user.organization,
            created_by=self.request.user
        )
    
    @extend_schema(
        summary="Get widget data",
        responses={200: ReportWidgetDataSerializer}
    )
    @action(detail=True, methods=['get'], url_path='data')
    def data(self, request, pk=None):
        """
        GET /api/widgets/{id}/data/
        
        Get current data for this widget.
        """
        widget = self.get_object()
        
        widget_data = DashboardWidgetDataSelector.get_widget_data(widget)
        
        serializer = ReportWidgetDataSerializer(widget_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get dashboard widgets",
        responses={200: ReportWidgetSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='dashboard')
    def dashboard(self, request):
        """
        GET /api/widgets/dashboard/
        
        Get all active dashboard widgets with their data.
        """
        widgets = self.get_queryset().order_by('display_order')
        
        result = []
        for widget in widgets:
            widget_data = DashboardWidgetDataSelector.get_widget_data(widget)
            result.append({
                'widget': ReportWidgetSerializer(widget).data,
                'data': widget_data
            })
        
        return Response(result)
