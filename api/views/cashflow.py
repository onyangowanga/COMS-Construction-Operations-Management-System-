"""
Cash Flow API Views

RESTful API endpoints for cash flow forecasting.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from drf_spectacular.utils import extend_schema, OpenApiParameter
from drf_spectacular.types import OpenApiTypes

from apps.cashflow import selectors
from apps.cashflow.services import CashFlowService
from apps.cashflow.models import CashFlowForecast, PortfolioCashFlowSummary
from api.serializers.cashflow import (
    CashFlowForecastSerializer,
    CashFlowTrendSerializer,
    CashFlowBreakdownSerializer,
    ProjectForecastSummarySerializer,
    PortfolioCashFlowSummarySerializer,
    PortfolioForecastSummarySerializer,
    PortfolioCashFlowTrendSerializer,
    CashFlowAlertSerializer,
)


class ProjectCashFlowViewSet(viewsets.GenericViewSet):
    """
    API endpoints for project-level cash flow forecasts.
    
    Endpoints:
    - GET /api/cashflow/project/{id}/forecast/
    - GET /api/cashflow/project/{id}/trend/
    - GET /api/cashflow/project/{id}/summary/
    - GET /api/cashflow/project/{id}/breakdown/
    - POST /api/cashflow/project/{id}/generate/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = CashFlowForecastSerializer
    
    @extend_schema(
        summary="Get project cash flow forecast",
        description="Retrieve cash flow forecast for a specific project",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of months to forecast (default: 6)',
                required=False
            ),
        ],
        responses={200: CashFlowForecastSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='forecast')
    def forecast(self, request, pk=None):
        """
        GET /api/cashflow/project/{id}/forecast/?months=6
        
        Returns monthly cash flow forecast for the project.
        """
        months = int(request.query_params.get('months', 6))
        
        # Validate months parameter
        if months not in [3, 6, 12]:
            return Response(
                {'error': 'months parameter must be 3, 6, or 12'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forecasts = selectors.get_project_forecast(
            project_id=pk,
            months=months
        )
        
        serializer = CashFlowForecastSerializer(forecasts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get project cash flow trend data",
        description="Get time series data suitable for charting",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of months (default: 6)',
                required=False
            ),
        ],
        responses={200: CashFlowTrendSerializer(many=True)}
    )
    @action(detail=True, methods=['get'], url_path='trend')
    def trend(self, request, pk=None):
        """
        GET /api/cashflow/project/{id}/trend/?months=6
        
        Returns cash flow trend data for charting.
        """
        months = int(request.query_params.get('months', 6))
        
        trend_data = selectors.get_cash_flow_trend_data(
            project_id=pk,
            months=months
        )
        
        serializer = CashFlowTrendSerializer(trend_data, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get project forecast summary",
        description="Get aggregated forecast metrics for project",
        responses={200: ProjectForecastSummarySerializer}
    )
    @action(detail=True, methods=['get'], url_path='summary')
    def summary(self, request, pk=None):
        """
        GET /api/cashflow/project/{id}/summary/
        
        Returns summary statistics for project forecast.
        """
        summary_data = selectors.get_project_forecast_summary(project_id=pk)
        
        serializer = ProjectForecastSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get cash flow breakdown",
        description="Get detailed inflow/outflow breakdown for a specific month",
        parameters=[
            OpenApiParameter(
                name='month',
                type=OpenApiTypes.DATE,
                location=OpenApiParameter.QUERY,
                description='Forecast month (YYYY-MM-DD, defaults to current)',
                required=False
            ),
        ],
        responses={200: CashFlowBreakdownSerializer}
    )
    @action(detail=True, methods=['get'], url_path='breakdown')
    def breakdown(self, request, pk=None):
        """
        GET /api/cashflow/project/{id}/breakdown/?month=2026-04
        
        Returns detailed breakdown of inflows and outflows.
        """
        from datetime import datetime
        
        month_param = request.query_params.get('month')
        forecast_month = None
        
        if month_param:
            try:
                forecast_month = datetime.strptime(month_param, '%Y-%m-%d').date()
            except ValueError:
                return Response(
                    {'error': 'Invalid month format. Use YYYY-MM-DD'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Get inflow and outflow breakdowns
        inflows = selectors.get_inflow_breakdown(pk, forecast_month)
        outflows = selectors.get_outflow_breakdown(pk, forecast_month)
        
        # Combine into single response
        breakdown = {**inflows, **outflows}
        
        serializer = CashFlowBreakdownSerializer(breakdown)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Generate project forecast",
        description="Generate/update cash flow forecast for project",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Forecast horizon in months (3, 6, or 12)',
                required=False
            ),
        ],
        responses={200: {'type': 'object', 'properties': {
            'message': {'type': 'string'},
            'forecasts_created': {'type': 'integer'},
        }}}
    )
    @action(detail=True, methods=['post'], url_path='generate')
    def generate(self, request, pk=None):
        """
        POST /api/cashflow/project/{id}/generate/?months=6
        
        Generate fresh forecast for the project.
        """
        months = int(request.query_params.get('months', 6))
        
        # Validate months parameter
        if months not in [3, 6, 12]:
            return Response(
                {'error': 'months parameter must be 3, 6, or 12'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate forecast
        forecasts = CashFlowService.generate_project_forecast(
            project_id=pk,
            horizon_months=months
        )
        
        return Response({
            'message': f'Forecast generated successfully',
            'forecasts_created': len(forecasts),
            'horizon_months': months
        })


class PortfolioCashFlowViewSet(viewsets.GenericViewSet):
    """
    API endpoints for portfolio-level cash flow forecasts.
    
    Endpoints:
    - GET /api/cashflow/portfolio/forecast/
    - GET /api/cashflow/portfolio/trend/
    - GET /api/cashflow/portfolio/summary/
    - GET /api/cashflow/portfolio/alerts/
    - POST /api/cashflow/portfolio/generate/
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = PortfolioCashFlowSummarySerializer
    
    @extend_schema(
        summary="Get portfolio cash flow forecast",
        description="Retrieve portfolio-wide cash flow forecast",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of months to forecast (default: 6)',
                required=False
            ),
        ],
        responses={200: PortfolioCashFlowSummarySerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='forecast')
    def forecast(self, request):
        """
        GET /api/cashflow/portfolio/forecast/?months=6
        
        Returns monthly cash flow forecast for entire portfolio.
        """
        months = int(request.query_params.get('months', 6))
        
        # Validate months parameter
        if months not in [3, 6, 12]:
            return Response(
                {'error': 'months parameter must be 3, 6, or 12'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        forecasts = selectors.get_portfolio_forecast(months=months)
        
        serializer = PortfolioCashFlowSummarySerializer(forecasts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get portfolio cash flow trend data",
        description="Get time series data suitable for charting",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Number of months (default: 6)',
                required=False
            ),
        ],
        responses={200: PortfolioCashFlowTrendSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='trend')
    def trend(self, request):
        """
        GET /api/cashflow/portfolio/trend/?months=6
        
        Returns portfolio cash flow trend data for charting.
        """
        months = int(request.query_params.get('months', 6))
        
        trend_data = selectors.get_portfolio_cash_flow_trend_data(months=months)
        
        serializer = PortfolioCashFlowTrendSerializer(trend_data, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get portfolio forecast summary",
        description="Get aggregated forecast metrics for portfolio",
        responses={200: PortfolioForecastSummarySerializer}
    )
    @action(detail=False, methods=['get'], url_path='summary')
    def summary(self, request):
        """
        GET /api/cashflow/portfolio/summary/
        
        Returns summary statistics for portfolio forecast.
        """
        summary_data = selectors.get_portfolio_forecast_summary()
        
        serializer = PortfolioForecastSummarySerializer(summary_data)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Get cash flow alerts",
        description="Get critical cash flow alerts for portfolio",
        responses={200: CashFlowAlertSerializer(many=True)}
    )
    @action(detail=False, methods=['get'], url_path='alerts')
    def alerts(self, request):
        """
        GET /api/cashflow/portfolio/alerts/
        
        Returns critical cash flow alerts (negative balances, severe deficits).
        """
        alerts = selectors.get_critical_cash_flow_alerts()
        
        serializer = CashFlowAlertSerializer(alerts, many=True)
        return Response(serializer.data)
    
    @extend_schema(
        summary="Generate portfolio forecast",
        description="Generate/update cash flow forecast for all projects",
        parameters=[
            OpenApiParameter(
                name='months',
                type=OpenApiTypes.INT,
                location=OpenApiParameter.QUERY,
                description='Forecast horizon in months (3, 6, or 12)',
                required=False
            ),
        ],
        responses={200: {'type': 'object', 'properties': {
            'message': {'type': 'string'},
            'updated_projects': {'type': 'integer'},
            'forecast_months': {'type': 'integer'},
        }}}
    )
    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """
        POST /api/cashflow/portfolio/generate/?months=6
        
        Generate fresh forecast for all active projects.
        """
        months = int(request.query_params.get('months', 6))
        
        # Validate months parameter
        if months not in [3, 6, 12]:
            return Response(
                {'error': 'months parameter must be 3, 6, or 12'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Generate portfolio forecast
        result = CashFlowService.update_all_forecasts(horizon_months=months)
        
        return Response({
            'message': 'Portfolio forecast generated successfully',
            **result
        })
