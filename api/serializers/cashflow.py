"""
Cash Flow API Serializers

Serializers for cash flow forecast data API endpoints.
"""

from rest_framework import serializers
from apps.cashflow.models import CashFlowForecast, PortfolioCashFlowSummary
from apps.projects.models import Project


class ProjectBasicSerializer(serializers.ModelSerializer):
    """Basic project info for nested serialization"""
    
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )
    
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'project_code',
            'status',
            'organization_name',
        ]
        read_only_fields = fields


class CashFlowForecastSerializer(serializers.ModelSerializer):
    """Serializer for cash flow forecast records"""
    
    project = ProjectBasicSerializer(read_only=True)
    month = serializers.SerializerMethodField()
    month_label = serializers.SerializerMethodField()
    
    class Meta:
        model = CashFlowForecast
        fields = [
            'id',
            'project',
            'forecast_month',
            'month',
            'month_label',
            # Inflows
            'expected_valuations',
            'expected_client_payments',
            'expected_retention_releases',
            'expected_variation_order_payments',
            'total_inflow',
            # Outflows
            'expected_supplier_payments',
            'expected_labour_costs',
            'expected_consultant_fees',
            'expected_procurement_payments',
            'expected_site_expenses',
            'expected_other_expenses',
            'total_outflow',
            # Metrics
            'net_cash_flow',
            'cumulative_cash_balance',
            'confidence_level',
            'is_actual',
            'forecast_generated_at',
        ]
        read_only_fields = fields
    
    def get_month(self, obj):
        """Get month in YYYY-MM format"""
        return obj.forecast_month.strftime('%Y-%m')
    
    def get_month_label(self, obj):
        """Get month in human-readable format"""
        return obj.forecast_month.strftime('%b %Y')


class CashFlowTrendSerializer(serializers.Serializer):
    """Serializer for cash flow trend data (charting)"""
    
    month = serializers.CharField()
    month_label = serializers.CharField()
    inflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    outflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    cumulative_balance = serializers.DecimalField(max_digits=15, decimal_places=2)


class CashFlowBreakdownSerializer(serializers.Serializer):
    """Serializer for detailed inflow/outflow breakdown"""
    
    # Inflows
    valuations = serializers.DecimalField(max_digits=15, decimal_places=2)
    client_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    retention_releases = serializers.DecimalField(max_digits=15, decimal_places=2)
    variation_orders = serializers.DecimalField(max_digits=15, decimal_places=2)
    
    # Outflows
    supplier_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    labour_costs = serializers.DecimalField(max_digits=15, decimal_places=2)
    consultant_fees = serializers.DecimalField(max_digits=15, decimal_places=2)
    procurement_payments = serializers.DecimalField(max_digits=15, decimal_places=2)
    site_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    other_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)


class ProjectForecastSummarySerializer(serializers.Serializer):
    """Serializer for project forecast summary"""
    
    total_expected_inflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expected_outflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_cash_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    final_cash_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    months_with_negative_flow = serializers.IntegerField()


class PortfolioCashFlowSummarySerializer(serializers.ModelSerializer):
    """Serializer for portfolio cash flow summary"""
    
    month = serializers.SerializerMethodField()
    month_label = serializers.SerializerMethodField()
    
    class Meta:
        model = PortfolioCashFlowSummary
        fields = [
            'id',
            'forecast_month',
            'month',
            'month_label',
            'total_portfolio_inflow',
            'total_portfolio_outflow',
            'net_portfolio_cash_flow',
            'cumulative_portfolio_balance',
            'active_projects_count',
            'projects_with_negative_flow',
            'average_cash_burn_rate',
            'cash_runway_months',
            'forecast_generated_at',
        ]
        read_only_fields = fields
    
    def get_month(self, obj):
        """Get month in YYYY-MM format"""
        return obj.forecast_month.strftime('%Y-%m')
    
    def get_month_label(self, obj):
        """Get month in human-readable format"""
        return obj.forecast_month.strftime('%b %Y')


class PortfolioForecastSummarySerializer(serializers.Serializer):
    """Serializer for portfolio forecast summary"""
    
    total_expected_inflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expected_outflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_portfolio_cash_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    final_portfolio_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    months_with_negative_flow = serializers.IntegerField()
    total_forecast_months = serializers.IntegerField()
    average_burn_rate = serializers.DecimalField(max_digits=15, decimal_places=2)
    cash_runway_months = serializers.DecimalField(max_digits=5, decimal_places=1)


class PortfolioCashFlowTrendSerializer(serializers.Serializer):
    """Serializer for portfolio cash flow trend data (charting)"""
    
    month = serializers.CharField()
    month_label = serializers.CharField()
    inflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    outflow = serializers.DecimalField(max_digits=15, decimal_places=2)
    net_flow = serializers.DecimalField(max_digits=15, decimal_places=2)
    cumulative_balance = serializers.DecimalField(max_digits=15, decimal_places=2)
    active_projects = serializers.IntegerField()
    negative_projects = serializers.IntegerField()


class CashFlowAlertSerializer(serializers.Serializer):
    """Serializer for cash flow alerts"""
    
    project_id = serializers.UUIDField()
    project_name = serializers.CharField()
    alert_type = serializers.CharField()
    severity = serializers.CharField()
    message = serializers.CharField()
    forecast_month = serializers.DateField()
