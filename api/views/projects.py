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
    
    @action(detail=True, methods=['get'])
    def financial_summary(self, request, pk=None):
        """Get financial summary for a project"""
        project = self.get_object()
        
        # Calculate totals
        total_expenses = sum(
            expense.amount for expense in project.expenses.all()
        )
        total_payments = sum(
            payment.amount for payment in project.client_payments.all()
        )
        outstanding_balance = project.project_value - total_payments if project.project_value else 0
        
        return Response({
            'project_value': project.project_value,
            'total_expenses': total_expenses,
            'total_payments': total_payments,
            'outstanding_balance': outstanding_balance,
            'profit_loss': total_payments - total_expenses if total_payments else -total_expenses
        })


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
