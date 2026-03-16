"""
Supplier ViewSets
Handles Supplier, LocalPurchaseOrder, SupplierInvoice API endpoints
"""
from rest_framework import viewsets, filters, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from django_filters.rest_framework import DjangoFilterBackend

from apps.suppliers.models import Supplier, LocalPurchaseOrder, SupplierInvoice
from api.serializers.suppliers import (
    SupplierSerializer, SupplierListSerializer,
    LocalPurchaseOrderSerializer, SupplierInvoiceSerializer
)
from api.selectors.supplier_selectors import get_suppliers_outstanding_payments
from api.services.supplier_analytics import calculate_supplier_outstanding_payments

class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Supplier model
    
    Provides CRUD operations for suppliers
    """
    queryset = Supplier.objects.all().select_related('organization').prefetch_related('lpos', 'invoices')
    serializer_class = SupplierSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['is_active', 'organization']
    search_fields = ['name', 'phone', 'email', 'tax_pin']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']
    
    def get_serializer_class(self):
        """Use lightweight serializer for list view"""
        if self.action == 'list':
            return SupplierListSerializer
        return SupplierSerializer

    def get_queryset(self):
        """Limit suppliers to the authenticated user's organization."""
        queryset = super().get_queryset()
        user = self.request.user

        if getattr(user, 'organization_id', None):
            return queryset.filter(organization=user.organization)

        # Superusers without a bound organization can still manage all suppliers.
        if getattr(user, 'is_superuser', False):
            return queryset

        return queryset.none()

    def perform_create(self, serializer):
        """Auto-assign organization from logged-in user where possible."""
        user = self.request.user

        if getattr(user, 'organization_id', None):
            requested_org = serializer.validated_data.get('organization')
            if requested_org and requested_org != user.organization and not getattr(user, 'is_superuser', False):
                raise ValidationError({'organization': 'You can only create suppliers in your own organization.'})
            serializer.save(organization=user.organization)
            return

        if getattr(user, 'is_superuser', False) and serializer.validated_data.get('organization'):
            serializer.save()
            return

        raise ValidationError({'organization': 'Your account is not linked to an organization.'})
    
    @action(detail=True, methods=['get'])
    def purchase_orders(self, request, pk=None):
        """Get all purchase orders for a supplier"""
        supplier = self.get_object()
        lpos = supplier.lpos.all().order_by('-issue_date')
        serializer = LocalPurchaseOrderSerializer(lpos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for a supplier"""
        supplier = self.get_object()
        invoices = supplier.invoices.all().order_by('-invoice_date')
        serializer = SupplierInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='outstanding-payments')
    def outstanding_payments(self, request):
        """
        Get all suppliers with outstanding payment balances
        
        Returns:
            - Supplier details
            - Total invoiced
            - Total paid
            - Outstanding balance
            - Payment completion percentage
        """
        suppliers = get_suppliers_outstanding_payments()
        outstanding_data = calculate_supplier_outstanding_payments(suppliers)
        
        total_outstanding = sum(item['outstanding_balance'] for item in outstanding_data)
        total_invoiced = sum(item['total_invoiced'] for item in outstanding_data)
        
        return Response({
            'summary': {
                'total_suppliers_with_outstanding': len(outstanding_data),
                'total_outstanding_amount': total_outstanding,
                'total_invoiced_amount': total_invoiced,
            },
            'suppliers': outstanding_data
        })


class LocalPurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LocalPurchaseOrder model
    
    Provides CRUD operations for LPOs with workflow actions
    """
    queryset = LocalPurchaseOrder.objects.all().select_related('supplier', 'project').prefetch_related('items')
    serializer_class = LocalPurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'project', 'status']
    search_fields = ['lpo_number', 'supplier__name', 'project__code', 'project__name']
    ordering_fields = ['issue_date', 'total_amount', 'created_at']
    ordering = ['-issue_date']
    
    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """
        Approve a draft LPO
        
        Transitions: DRAFT -> APPROVED
        """
        from api.services.procurement_workflow import approve_lpo, ProcurementWorkflowError
        
        lpo = self.get_object()
        
        try:
            result = approve_lpo(lpo, approved_by=request.user)
            return Response(result, status=status.HTTP_200_OK)
        except ProcurementWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='mark-delivered')
    def mark_delivered(self, request, pk=None):
        """
        Mark LPO as delivered
        
        Transitions: APPROVED/ISSUED -> DELIVERED
        """
        from api.services.procurement_workflow import mark_lpo_delivered, ProcurementWorkflowError
        
        lpo = self.get_object()
        
        try:
            result = mark_lpo_delivered(lpo, delivered_by=request.user)
            return Response(result, status=status.HTTP_200_OK)
        except ProcurementWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='mark-invoiced')
    def mark_invoiced(self, request, pk=None):
        """
        Mark LPO as invoiced
        
        Body params:
            invoice_number (optional): Invoice reference number
        
        Transitions: DELIVERED -> INVOICED
        """
        from api.services.procurement_workflow import mark_lpo_invoiced, ProcurementWorkflowError
        
        lpo = self.get_object()
        invoice_number = request.data.get('invoice_number')
        
        try:
            result = mark_lpo_invoiced(lpo, invoiced_by=request.user, invoice_number=invoice_number)
            return Response(result, status=status.HTTP_200_OK)
        except ProcurementWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'], url_path='mark-paid')
    def mark_paid(self, request, pk=None):
        """
        Mark LPO as paid
        
        Body params:
            payment_reference (optional): Payment reference number
        
        Transitions: INVOICED -> PAID
        """
        from api.services.procurement_workflow import mark_lpo_paid, ProcurementWorkflowError
        
        lpo = self.get_object()
        payment_reference = request.data.get('payment_reference')
        
        try:
            result = mark_lpo_paid(lpo, paid_by=request.user, payment_reference=payment_reference)
            return Response(result, status=status.HTTP_200_OK)
        except ProcurementWorkflowError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class SupplierInvoiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for SupplierInvoice model
    
    Provides CRUD operations for supplier invoices
    """
    queryset = SupplierInvoice.objects.all().select_related('supplier', 'project', 'lpo').prefetch_related('payments')
    serializer_class = SupplierInvoiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'project', 'status', 'lpo']
    search_fields = ['invoice_number', 'supplier__name', 'project__code']
    ordering_fields = ['invoice_date', 'due_date', 'total_amount']
    ordering = ['-invoice_date']
