"""
Ledger ViewSets
Handles Expense and ExpenseAllocation API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.ledger.models import Expense, ExpenseAllocation
from api.serializers.ledger import (
    ExpenseSerializer, ExpenseListSerializer, ExpenseAllocationSerializer
)


class ExpenseViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Expense model
    
    Provides CRUD operations for expenses
    """
    queryset = Expense.objects.all().select_related('project').prefetch_related('allocations')
    serializer_class = ExpenseSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'expense_type', 'date']
    search_fields = ['description', 'reference_number', 'project__code', 'project__name']
    ordering_fields = ['date', 'amount', 'created_at']
    ordering = ['-date']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ExpenseListSerializer
        return ExpenseSerializer
    
    @action(detail=True, methods=['get'])
    def allocations(self, request, pk=None):
        """Get all allocations for an expense"""
        expense = self.get_object()
        allocations = expense.allocations.all()
        serializer = ExpenseAllocationSerializer(allocations, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def unallocated(self, request):
        """Get all expenses that are not fully allocated"""
        expenses = self.queryset.all()
        unallocated = [exp for exp in expenses if exp.unallocated_amount > 0]
        serializer = ExpenseListSerializer(unallocated, many=True)
        return Response(serializer.data)


class ExpenseAllocationViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ExpenseAllocation model
    
    Provides CRUD operations for expense allocations
    """
    queryset = ExpenseAllocation.objects.all().select_related('expense', 'bq_item')
    serializer_class = ExpenseAllocationSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['expense', 'bq_item', 'expense__project']
    search_fields = ['notes', 'expense__description', 'bq_item__description']
    ordering_fields = ['created_at', 'allocated_amount']
    ordering = ['-created_at']
