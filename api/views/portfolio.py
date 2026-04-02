"""
Portfolio API Views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.portfolio.models import ProjectMetrics
from apps.portfolio import portfolio_selectors as selectors
from apps.portfolio.services import PortfolioAnalyticsService
from api.serializers.portfolio import (
    ProjectMetricsSerializer,
    ProjectMetricsListSerializer,
    PortfolioSummarySerializer,
    EVMSummarySerializer,
    RiskDistributionSerializer,
    HealthDistributionSerializer,
)


class PortfolioViewSet(viewsets.GenericViewSet):
    """
    Portfolio analytics and metrics endpoints
    
    Provides portfolio-wide analytics, risk assessment, and EVM metrics
    """
    
    permission_classes = [IsAuthenticated]
    
    @extend_schema(
        summary="Get portfolio summary",
        description="Returns comprehensive portfolio-wide metrics including financials, risk indicators, and project counts",
        responses={200: PortfolioSummarySerializer}
    )
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        GET /api/portfolio/summary/
        
        Returns:
            active_projects: Count of active projects
            total_contract_value: Sum of all project values
            total_expenses: Sum of all approved expenses
            total_revenue: Sum of all client payments
            total_profit: Revenue - Expenses
            projects_over_budget: Count of projects exceeding budget
            projects_behind_schedule: Count of delayed projects
            high_risk_projects: Count of high/critical risk projects
            avg_budget_utilization: Average budget utilization %
            avg_profit_margin: Average profit margin %
        """
        summary_data = selectors.get_portfolio_summary()
        serializer = PortfolioSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get risk distribution",
        description="Returns count of projects by risk level",
        responses={200: RiskDistributionSerializer}
    )
    @action(detail=False, methods=['get'], url_path='risk-distribution')
    def risk_distribution(self, request):
        """
        GET /api/portfolio/risk-distribution/
        
        Returns counts by risk level: low, medium, high, critical
        """
        distribution = selectors.get_portfolio_risk_distribution()
        serializer = RiskDistributionSerializer(distribution)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get health distribution",
        description="Returns count of projects by health status",
        responses={200: HealthDistributionSerializer}
    )
    @action(detail=False, methods=['get'], url_path='health-distribution')
    def health_distribution(self, request):
        """
        GET /api/portfolio/health-distribution/
        
        Returns counts by health: excellent, good, warning, critical
        """
        distribution = selectors.get_portfolio_health_distribution()
        serializer = HealthDistributionSerializer(distribution)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update all project metrics",
        description="Triggers recalculation of metrics for all active projects",
        responses={200: {'type': 'object', 'properties': {
            'message': {'type': 'string'},
            'updated_count': {'type': 'integer'}
        }}}
    )
    @action(detail=False, methods=['post'], url_path='update-metrics')
    def update_metrics(self, request):
        """
        POST /api/portfolio/update-metrics/
        
        Recalculates metrics for all active projects
        """
        updated_count = PortfolioAnalyticsService.update_all_project_metrics()
        return Response({
            'message': f'Successfully updated metrics for {updated_count} projects',
            'updated_count': updated_count
        })


class ProjectMetricsViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Project metrics CRUD endpoints
    
    Provides detailed metrics for individual projects including EVM analysis
    """
    
    permission_classes = [IsAuthenticated]
    queryset = ProjectMetrics.objects.select_related('project').all()
    
    def get_serializer_class(self):
        """Use different serializers for list vs detail"""
        if self.action == 'list':
            return ProjectMetricsListSerializer
        return ProjectMetricsSerializer
    
    @extend_schema(
        summary="List all project metrics",
        description="Returns metrics for all projects with optional filtering",
        parameters=[
            OpenApiParameter(
                name='risk_level',
                type=OpenApiTypes.STR,
                description='Filter by risk level: LOW, MEDIUM, HIGH, CRITICAL'
            ),
            OpenApiParameter(
                name='health',
                type=OpenApiTypes.STR,
                description='Filter by health: EXCELLENT, GOOD, WARNING, CRITICAL'
            ),
            OpenApiParameter(
                name='over_budget',
                type=OpenApiTypes.BOOL,
                description='Filter projects over budget'
            ),
            OpenApiParameter(
                name='behind_schedule',
                type=OpenApiTypes.BOOL,
                description='Filter projects behind schedule'
            ),
        ]
    )
    def list(self, request, *args, **kwargs):
        """
        GET /api/project-metrics/
        
        Query Parameters:
            - risk_level: Filter by risk level
            - health: Filter by health status
            - over_budget: true/false
            - behind_schedule: true/false
        """
        queryset = self.get_queryset()
        
        # Apply filters
        risk_level = request.query_params.get('risk_level')
        if risk_level:
            queryset = queryset.filter(risk_level=risk_level.upper())
        
        health = request.query_params.get('health')
        if health:
            queryset = queryset.filter(project_health=health.upper())
        
        over_budget = request.query_params.get('over_budget')
        if over_budget is not None:
            queryset = queryset.filter(is_over_budget=(over_budget.lower() == 'true'))
        
        behind_schedule = request.query_params.get('behind_schedule')
        if behind_schedule is not None:
            queryset = queryset.filter(is_behind_schedule=(behind_schedule.lower() == 'true'))
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get project metrics details",
        description="Returns detailed metrics for a specific project",
        responses={200: ProjectMetricsSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        """
        GET /api/project-metrics/{id}/
        
        Returns full project metrics including EVM data
        """
        return super().retrieve(request, *args, **kwargs)
    
    @extend_schema(
        summary="Get EVM summary for project",
        description="Returns detailed Earned Value Management metrics for a project",
        responses={200: EVMSummarySerializer}
    )
    @action(detail=True, methods=['get'], url_path='evm-summary')
    def evm_summary(self, request, pk=None):
        """
        GET /api/project-metrics/{id}/evm-summary/
        
        Returns:
            - Planned Value (PV)
            - Earned Value (EV)
            - Actual Cost (AC)
            - Cost Variance (CV)
            - Schedule Variance (SV)
            - Cost Performance Index (CPI)
            - Schedule Performance Index (SPI)
            - Estimate at Completion (EAC)
            - Variance at Completion (VAC)
        """
        metrics = self.get_object()
        evm_data = selectors.get_evm_summary_for_project(str(metrics.project.id))
        serializer = EVMSummarySerializer(evm_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Update project metrics",
        description="Triggers recalculation of metrics for this specific project",
        responses={200: ProjectMetricsSerializer}
    )
    @action(detail=True, methods=['post'], url_path='update')
    def update_metrics(self, request, pk=None):
        """
        POST /api/project-metrics/{id}/update/
        
        Recalculates all metrics for this project
        """
        metrics = self.get_object()
        updated_metrics = PortfolioAnalyticsService.compute_project_risk_indicators(
            str(metrics.project.id)
        )
        serializer = ProjectMetricsSerializer(updated_metrics)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get high risk projects",
        description="Returns projects with HIGH or CRITICAL risk level",
        responses={200: ProjectMetricsListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='high-risk')
    def high_risk(self, request):
        """
        GET /api/project-metrics/high-risk/
        
        Returns all HIGH and CRITICAL risk projects
        """
        projects = selectors.get_high_risk_projects()
        serializer = ProjectMetricsListSerializer(projects, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get projects requiring attention",
        description="Returns projects with issues: high risk, over budget, or behind schedule",
        responses={200: ProjectMetricsListSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='attention-required')
    def attention_required(self, request):
        """
        GET /api/project-metrics/attention-required/
        
        Returns projects needing immediate attention
        """
        projects = selectors.get_projects_requiring_attention()
        serializer = ProjectMetricsListSerializer(projects, many=True)
        return Response(serializer.data)
