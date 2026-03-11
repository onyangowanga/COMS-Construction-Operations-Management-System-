"""
Consultant ViewSets
Handles Consultant, ConsultantFee, ConsultantPayment API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.consultants.models import Consultant, ConsultantFee, ConsultantPayment
from api.serializers.consultants import (
    ConsultantSerializer, ConsultantListSerializer,
    ConsultantFeeSerializer, ConsultantPaymentSerializer
)


class ConsultantViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Consultant model
    
    Provides CRUD operations for consultants
    """
    queryset = Consultant.objects.all().select_related('organization').prefetch_related('fees', 'project_assignments')
    serializer_class = ConsultantSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['consultant_type', 'is_active', 'organization']
    search_fields = ['name', 'company', 'phone', 'email']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ConsultantListSerializer
        return ConsultantSerializer
    
    @action(detail=True, methods=['get'])
    def fees(self, request, pk=None):
        """Get all fees for a consultant"""
        consultant = self.get_object()
        fees = consultant.fees.all().order_by('-created_at')
        serializer = ConsultantFeeSerializer(fees, many=True)
        return Response(serializer.data)


class ConsultantFeeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ConsultantFee model
    
    Provides CRUD operations for consultant fees
    """
    queryset = ConsultantFee.objects.all().select_related('consultant', 'project').prefetch_related('payments')
    serializer_class = ConsultantFeeSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['consultant', 'project', 'fee_type']
    search_fields = ['consultant__name', 'project__code', 'project__name']
    ordering_fields = ['created_at', 'contract_amount']
    ordering = ['-created_at']
    
    @action(detail=True, methods=['get'])
    def payments(self, request, pk=None):
        """Get all payments for a fee"""
        fee = self.get_object()
        payments = fee.payments.all().order_by('-payment_date')
        serializer = ConsultantPaymentSerializer(payments, many=True)
        return Response(serializer.data)


class ConsultantPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ConsultantPayment model
    
    Provides CRUD operations for consultant payments
    """
    queryset = ConsultantPayment.objects.all().select_related('consultant_fee')
    serializer_class = ConsultantPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['consultant_fee', 'payment_method', 'payment_date']
    search_fields = ['reference_number', 'notes', 'consultant_fee__consultant__name']
    ordering_fields = ['payment_date', 'amount']
    ordering = ['-payment_date']
