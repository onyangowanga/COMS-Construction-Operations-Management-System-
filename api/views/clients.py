"""
Client ViewSets
Handles ClientPayment and ClientReceipt API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.clients.models import ClientPayment, ClientReceipt
from api.serializers.clients import (
    ClientPaymentSerializer, ClientPaymentListSerializer, ClientReceiptSerializer
)


class ClientPaymentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ClientPayment model
    
    Provides CRUD operations for client payments
    """
    queryset = ClientPayment.objects.all().select_related('project')
    serializer_class = ClientPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['project', 'payment_method', 'payment_date']
    search_fields = ['reference_number', 'description', 'project__code', 'project__name']
    ordering_fields = ['payment_date', 'amount', 'created_at']
    ordering = ['-payment_date']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return ClientPaymentListSerializer
        return ClientPaymentSerializer
    
    @action(detail=True, methods=['get'])
    def receipt(self, request, pk=None):
        """Get receipt for a payment"""
        payment = self.get_object()
        if hasattr(payment, 'receipt'):
            serializer = ClientReceiptSerializer(payment.receipt)
            return Response(serializer.data)
        return Response({'detail': 'No receipt issued for this payment'}, status=404)


class ClientReceiptViewSet(viewsets.ModelViewSet):
    """
    ViewSet for ClientReceipt model
    
    Provides CRUD operations for client receipts
    """
    queryset = ClientReceipt.objects.all().select_related('payment__project')
    serializer_class = ClientReceiptSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment', 'issued_date']
    search_fields = ['receipt_number', 'notes', 'payment__project__code']
    ordering_fields = ['issued_date', 'created_at']
    ordering = ['-issued_date']
