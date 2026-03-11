"""
Project ViewSets
Handles Project and ProjectStage API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.projects.models import Project, ProjectStage
from api.serializers.projects import (
    ProjectSerializer, ProjectListSerializer, ProjectStageSerializer
)
from api.selectors.project_selectors import (
    get_project_financial_data,
    get_project_budget_variance,
    get_project_health_data,
)
from api.services.project_analytics import (
    calculate_project_financial_summary,
    calculate_budget_variance,
    calculate_project_health,
)

class ProjectViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Project model
    
    Provides CRUD operations and custom actions for projects
    """
    queryset = Project.objects.all().select_related('organization').prefetch_related('stages')
    serializer_class = ProjectSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'contract_type', 'project_type', 'organization']
    search_fields = ['code', 'name', 'client_name', 'location']
    ordering_fields = ['created_at', 'start_date', 'project_value', 'name']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ProjectListSerializer
        return ProjectSerializer
    
    @action(detail=True, methods=['get'])
    def stages(self, request, pk=None):
        """Get all stages for a project"""
        project = self.get_object()
        stages = project.stages.all().order_by('order')
        serializer = ProjectStageSerializer(stages, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def expenses(self, request, pk=None):
        """Get all expenses for a project"""
        from api.serializers.ledger import ExpenseListSerializer
        
        project = self.get_object()
        expenses = project.expenses.all().order_by('-date')
        serializer = ExpenseListSerializer(expenses, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all client payments for a project"""
        from api.serializers.clients import ClientPaymentListSerializer
        
        project = self.get_object()
        payments = project.client_payments.all().order_by('-payment_date')
        serializer = ClientPaymentListSerializer(payments, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def photos(self, request, pk=None):
        """Get all photos for a project"""
        from api.serializers.media import ProjectPhotoListSerializer
        
        project = self.get_object()
        photos = project.photos.all().order_by('-uploaded_at')
        serializer = ProjectPhotoListSerializer(photos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='financial-summary')
    def financial_summary(self, request, pk=None):
        """
        Get comprehensive financial summary for a project
        
        Returns:
            - Contract value
            - Total client payments
            - Total expenses (categorized by type)
            - Remaining budget
            - Profit and profit margin
        """
        project = get_project_financial_data(pk)
        if not project:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        summary = calculate_project_financial_summary(project)
        return Response(summary)
    
    @action(detail=True, methods=['get'], url_path='budget-variance')
    def budget_variance(self, request, pk=None):
        """
        Get budget variance analysis for all BQ items
        
        Returns:
            - Budgeted amount per BQ item
            - Actual expenses allocated
            - Variance (positive = under budget, negative = over budget)
            - Status (UNDER_BUDGET, OVER_BUDGET, etc.)
        """
        bq_items = get_project_budget_variance(pk)
        variance_analysis = calculate_budget_variance(bq_items)
        
        total_budget = sum(item['budgeted_amount'] for item in variance_analysis)
        total_actual = sum(item['actual_expenses'] for item in variance_analysis)
        total_variance = total_budget - total_actual
        
        return Response({
            'project_id': str(pk),
            'summary': {
                'total_budget': total_budget,
                'total_actual': total_actual,
                'total_variance': total_variance,
                'variance_percentage': (total_variance / total_budget * 100) if total_budget > 0 else 0,
            },
            'items': variance_analysis
        })
    
    @action(detail=True, methods=['get'], url_path='health')
    def health(self, request, pk=None):
        """
        Get project health indicator
        
        Returns:
            - Health status: GREEN, YELLOW, or RED
            - Budget utilization
            - Payment collection
            - Completion rate
            - Delayed milestones
            - Red/Yellow flags
        """
        health_data = get_project_health_data(pk)
        if not health_data:
            return Response(
                {'error': 'Project not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        health_indicator = calculate_project_health(health_data)
        return Response(health_indicator)
    
    @action(detail=True, methods=['get'], url_path='activity')
    def activity(self, request, pk=None):
        """
        Get project activity timeline
        
        Query params:
            limit: Optional limit on number of activities
        
        Returns:
            - List of project activities ordered by most recent
        """
        from api.services.activity_service import get_project_activity_timeline
        from api.serializers.workflows import ProjectActivityListSerializer
        
        limit = request.query_params.get('limit')
        limit = int(limit) if limit else None
        
        activities = get_project_activity_timeline(pk, limit=limit)
        serializer = ProjectActivityListSerializer(activities, many=True)
        
        return Response({
            'project_id': str(pk),
            'total_activities': activities.count() if not limit else None,
            'activities': serializer.data
        })
    
    @action(detail=True, methods=['get'], url_path='notifications')
    def notifications(self, request, pk=None):
        """
        Get all notifications for a project
        
        Returns:
            - Budget overruns
            - Unpaid invoices
            - Expiring approvals
        """
        from api.services.notification_service import get_all_notifications
        
        notifications = get_all_notifications(project_id=pk)
        return Response(notifications)
    
    @action(detail=True, methods=['get'], url_path='valuations')
    def valuations(self, request, pk=None):
        """
        Get all valuations for this project
        
        Returns:
            - List of valuations with financial details
        """
        from apps.valuations.selectors import get_project_valuations
        from api.serializers.valuations import ValuationListSerializer
        
        valuations = get_project_valuations(str(pk))
        serializer = ValuationListSerializer(valuations, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='valuation-summary')
    def valuation_summary(self, request, pk=None):
        """
        Get valuation summary statistics for this project
        
        Returns:
            - Total valuations count
            - Total certified amount
            - Total paid amount
            - Pending payment amount
            - Retention held
            - Latest valuation details
        """
        from apps.valuations.selectors import get_valuation_summary
        from api.serializers.valuations import ValuationSummarySerializer
        
        summary = get_valuation_summary(str(pk))
        serializer = ValuationSummarySerializer(summary)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='bq-progress')
    def bq_progress(self, request, pk=None):
        """
        Get overall BQ progress summary for this project
        
        Returns:
            - Total budget
            - Total completed value
            - Remaining value
            - Percentage complete
        """
        from apps.valuations.selectors import get_bq_progress_summary
        
        progress = get_bq_progress_summary(str(pk))
        return Response(progress)


class ProjectStageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ProjectStage model
    
    Provides CRUD operations for project stages
    """
    queryset = ProjectStage.objects.all().select_related('project')
    serializer_class = ProjectStageSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'name', 'is_completed']
    search_fields = ['name', 'description', 'project__name', 'project__code']
    ordering_fields = ['order', 'start_date', 'end_date']
    ordering = ['project', 'order']
