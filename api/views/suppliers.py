"""
Supplier ViewSets
Handles Supplier, LocalPurchaseOrder, SupplierInvoice API endpoints
"""
from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend

from apps.suppliers.models import Supplier, LocalPurchaseOrder, SupplierInvoice
from api.serializers.suppliers import (
    SupplierSerializer, SupplierListSerializer,
    LocalPurchaseOrderSerializer, SupplierInvoiceSerializer
)


class SupplierViewSet(viewsets.ModelViewSet):
    """
    ViewSet for Supplier model
    
    Provides CRUD operations for suppliers
    """
    queryset = Supplier.objects.all().select_related('organization').prefetch_related('purchase_orders', 'invoices')
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
    
    @action(detail=True, methods=['get'])
    def purchase_orders(self, request, pk=None):
        """Get all purchase orders for a supplier"""
        supplier = self.get_object()
        lpos = supplier.purchase_orders.all().order_by('-issue_date')
        serializer = LocalPurchaseOrderSerializer(lpos, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['get'])
    def invoices(self, request, pk=None):
        """Get all invoices for a supplier"""
        supplier = self.get_object()
        invoices = supplier.invoices.all().order_by('-invoice_date')
        serializer = SupplierInvoiceSerializer(invoices, many=True)
        return Response(serializer.data)


class LocalPurchaseOrderViewSet(viewsets.ModelViewSet):
    """
    ViewSet for LocalPurchaseOrder model
    
    Provides CRUD operations for LPOs
    """
    queryset = LocalPurchaseOrder.objects.all().select_related('supplier', 'project').prefetch_related('items')
    serializer_class = LocalPurchaseOrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['supplier', 'project', 'status']
    search_fields = ['lpo_number', 'supplier__name', 'project__code', 'project__name']
    ordering_fields = ['issue_date', 'total_amount', 'created_at']
    ordering = ['-issue_date']


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
