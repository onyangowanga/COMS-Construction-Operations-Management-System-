"""
Worker ViewSets
Handles Worker and DailyLabourRecord API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.workers.models import Worker, DailyLabourRecord
from api.serializers.workers import (
    WorkerSerializer, WorkerListSerializer, DailyLabourRecordSerializer
)
from api.selectors.worker_selectors import get_workers_unpaid_wages
from api.services.worker_analytics import calculate_unpaid_wages

class WorkerViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Worker model
    
    Provides CRUD operations for workers
    """
    queryset = Worker.objects.all().select_related('organization').prefetch_related('daily_records')
    serializer_class = WorkerSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['role', 'is_active', 'organization']
    search_fields = ['name', 'phone', 'id_number']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return WorkerListSerializer
        return WorkerSerializer
    
    @action(detail=True, methods=['get'])
    def records(self, request, pk=None):
        """Get all labour records for a worker"""
        worker = self.get_object()
        records = worker.daily_records.all().order_by('-date')
        serializer = DailyLabourRecordSerializer(records, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'], url_path='worker-unpaid-wages')
    def worker_unpaid_wages(self, request, pk=None):
        """Get all unpaid wages for a specific worker"""
        worker = self.get_object()
        unpaid_records = worker.daily_records.filter(paid=False).order_by('-date')
        serializer = DailyLabourRecordSerializer(unpaid_records, many=True)
        total_unpaid = sum(record.daily_wage for record in unpaid_records)
        return Response({
            'records': serializer.data,
            'total_unpaid': total_unpaid
        })
    
    @action(detail=False, methods=['get'], url_path='unpaid-wages')
    def unpaid_wages(self, request):
        """
        Get all workers with unpaid wages
        
        Returns:
            - Worker details
            - Total days worked
            - Days unpaid
            - Total unpaid wages
        """
        workers = get_workers_unpaid_wages()
        unpaid_data = calculate_unpaid_wages(workers)
        
        total_unpaid = sum(item['total_unpaid_wages'] for item in unpaid_data)
        total_workers = len(unpaid_data)
        
        return Response({
            'summary': {
                'total_workers_with_unpaid_wages': total_workers,
                'total_unpaid_amount': total_unpaid,
            },
            'workers': unpaid_data
        })


class DailyLabourRecordViewSet(viewsets.ModelViewSet):
    """
    ViewSet for DailyLabourRecord model
    
    Provides CRUD operations for daily labour records
    """
    queryset = DailyLabourRecord.objects.all().select_related('worker', 'project')
    serializer_class = DailyLabourRecordSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['worker', 'project', 'paid', 'date']
    search_fields = ['worker__name', 'project__code', 'project__name', 'notes']
    ordering_fields = ['date', 'daily_wage']
    ordering = ['-date']
