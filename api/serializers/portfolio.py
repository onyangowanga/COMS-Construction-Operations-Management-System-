"""
Portfolio API Serializers
"""
from rest_framework import serializers
from apps.portfolio.models import ProjectMetrics
from apps.projects.models import Project


class ProjectBriefSerializer(serializers.ModelSerializer):
    """Brief project information for portfolio views"""
    
    class Meta:
        model = Project
        fields = [
            'id',
            'code',
            'name',
            'client_name',
            'project_type',
            'contract_type',
            'status',
            'project_value',
            'start_date',
            'end_date',
        ]


class ProjectMetricsSerializer(serializers.ModelSerializer):
    """Full project metrics serializer"""
    
    project = ProjectBriefSerializer(read_only=True)
    risk_level_display = serializers.CharField(
        source='get_risk_level_display',
        read_only=True
    )
    project_health_display = serializers.CharField(
        source='get_project_health_display',
        read_only=True
    )
    
    class Meta:
        model = ProjectMetrics
        fields = [
            'id',
            'project',
            'total_contract_value',
            'total_expenses',
            'total_revenue',
            'total_profit',
            'budget_utilization',
            'profit_margin',
            'project_health',
            'project_health_display',
            'risk_level',
            'risk_level_display',
            'planned_value',
            'earned_value',
            'actual_cost',
            'cost_performance_index',
            'schedule_performance_index',
            'days_elapsed',
            'days_remaining',
            'schedule_variance_days',
            'is_over_budget',
            'is_behind_schedule',
            'last_updated',
        ]


class ProjectMetricsListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    
    project_code = serializers.CharField(source='project.code', read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_status = serializers.CharField(source='project.status', read_only=True)
    
    class Meta:
        model = ProjectMetrics
        fields = [
            'id',
            'project_code',
            'project_name',
            'project_status',
            'risk_level',
            'project_health',
            'budget_utilization',
            'profit_margin',
            'cost_performance_index',
            'schedule_performance_index',
            'is_over_budget',
            'is_behind_schedule',
            'last_updated',
        ]


class PortfolioSummarySerializer(serializers.Serializer):
    """Serializer for portfolio-wide summary"""
    
    active_projects = serializers.IntegerField()
    total_contract_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_expenses = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_profit = serializers.DecimalField(max_digits=15, decimal_places=2)
    projects_over_budget = serializers.IntegerField()
    projects_behind_schedule = serializers.IntegerField()
    high_risk_projects = serializers.IntegerField()
    avg_budget_utilization = serializers.DecimalField(max_digits=5, decimal_places=2)
    avg_profit_margin = serializers.DecimalField(max_digits=5, decimal_places=2)


class EVMSummarySerializer(serializers.Serializer):
    """Serializer for Earned Value Management summary"""
    
    planned_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    earned_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    actual_cost = serializers.DecimalField(max_digits=15, decimal_places=2)
    cost_variance = serializers.DecimalField(max_digits=15, decimal_places=2)
    schedule_variance = serializers.DecimalField(max_digits=15, decimal_places=2)
    cost_performance_index = serializers.DecimalField(max_digits=5, decimal_places=2)
    schedule_performance_index = serializers.DecimalField(max_digits=5, decimal_places=2)
    estimate_at_completion = serializers.DecimalField(max_digits=15, decimal_places=2)
    variance_at_completion = serializers.DecimalField(max_digits=15, decimal_places=2)
    budget_at_completion = serializers.DecimalField(max_digits=15, decimal_places=2)


class RiskDistributionSerializer(serializers.Serializer):
    """Serializer for risk distribution"""
    
    low = serializers.IntegerField()
    medium = serializers.IntegerField()
    high = serializers.IntegerField()
    critical = serializers.IntegerField()


class HealthDistributionSerializer(serializers.Serializer):
    """Serializer for health distribution"""
    
    excellent = serializers.IntegerField()
    good = serializers.IntegerField()
    warning = serializers.IntegerField()
    critical = serializers.IntegerField()
