"""
Client ViewSets
Handles ClientPayment and ClientReceipt API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db import transaction
from django.utils import timezone

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

    def _generate_receipt_number(self, payment) -> str:
        """Generate receipt number in the format RCT-{PROJECT_CODE}-{YEAR}-{SEQ}."""
        year = timezone.now().year
        project_code = (getattr(payment.project, 'code', None) or str(payment.project_id)[:6]).upper()
        prefix = f"RCT-{project_code}-{year}-"

        last_receipt = ClientReceipt.objects.select_for_update().filter(
            payment__project=payment.project,
            receipt_number__startswith=prefix,
        ).order_by('-receipt_number').first()

        sequence = 1
        if last_receipt and last_receipt.receipt_number:
            try:
                sequence = int(last_receipt.receipt_number.split('-')[-1]) + 1
            except (ValueError, IndexError):
                sequence = 1

        return f"{prefix}{sequence:03d}"

    @transaction.atomic
    def perform_create(self, serializer):
        """Auto-generate receipt number unless a superuser explicitly provides one."""
        user = self.request.user
        payment = serializer.validated_data['payment']
        provided_receipt_number = serializer.validated_data.get('receipt_number')

        can_override = bool(getattr(user, 'is_superuser', False) and provided_receipt_number)
        receipt_number = provided_receipt_number if can_override else self._generate_receipt_number(payment)

        serializer.save(receipt_number=receipt_number)
