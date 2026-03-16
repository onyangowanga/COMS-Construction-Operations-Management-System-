"""
Supplier Serializers
Handles Supplier, LocalPurchaseOrder, LPOItem, SupplierInvoice, SupplierPayment serialization
"""
from rest_framework import serializers
from apps.suppliers.models import (
    Supplier, LocalPurchaseOrder, LPOItem, SupplierInvoice, SupplierPayment
)


class LPOItemSerializer(serializers.ModelSerializer):
    """Serializer for LPOItem model"""
    
    class Meta:
        model = LPOItem
        fields = [
            'id', 'lpo', 'item_name', 'quantity', 'unit',
            'unit_price', 'total_price', 'delivered_quantity', 'notes'
        ]
        read_only_fields = ['id']
    
    def validate(self, data):
        """Calculate total_price on save"""
        if 'quantity' in data and 'unit_price' in data:
            data['total_price'] = data['quantity'] * data['unit_price']
        return data


class SupplierPaymentSerializer(serializers.ModelSerializer):
    """Serializer for SupplierPayment model"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = SupplierPayment
        fields = [
            'id', 'supplier_invoice', 'amount', 'payment_date',
            'payment_method', 'payment_method_display',
            'reference_number', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SupplierInvoiceSerializer(serializers.ModelSerializer):
    """Serializer for SupplierInvoice model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    payments = SupplierPaymentSerializer(many=True, read_only=True)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, source='total_paid')
    outstanding_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True, source='outstanding_balance')
    
    class Meta:
        model = SupplierInvoice
        fields = [
            'id', 'supplier', 'project', 'lpo', 'invoice_number',
            'invoice_date', 'total_amount', 'status', 'status_display',
            'due_date', 'description', 'payments', 'total_paid',
            'outstanding_balance', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class LocalPurchaseOrderSerializer(serializers.ModelSerializer):
    """Serializer for LocalPurchaseOrder model"""
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    items = LPOItemSerializer(many=True, read_only=True)
    item_count = serializers.SerializerMethodField()
    
    class Meta:
        model = LocalPurchaseOrder
        fields = [
            'id', 'project', 'supplier', 'lpo_number', 'issue_date',
            'total_amount', 'status', 'status_display', 'delivery_deadline',
            'notes', 'items', 'item_count', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_item_count(self, obj):
        """Get number of items in this LPO"""
        return obj.items.count()


class SupplierSerializer(serializers.ModelSerializer):
    """Serializer for Supplier model"""
    purchase_orders = LocalPurchaseOrderSerializer(source='lpos', many=True, read_only=True)
    invoices = SupplierInvoiceSerializer(many=True, read_only=True)
    total_lpo_value = serializers.SerializerMethodField()
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'organization', 'name', 'phone', 'email',
            'address', 'tax_pin', 'is_active', 'purchase_orders',
            'invoices', 'total_lpo_value', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
        extra_kwargs = {
            # organization is injected in SupplierViewSet.perform_create()
            'organization': {'required': False},
        }

    def validate(self, attrs):
        """Block duplicate supplier names per organization (case-insensitive)."""
        request = self.context.get('request')

        name = attrs.get('name', getattr(self.instance, 'name', ''))
        if isinstance(name, str):
            name = name.strip()
            attrs['name'] = name

        organization = None
        if self.instance is not None:
            organization = self.instance.organization
        elif request is not None and getattr(request.user, 'organization_id', None):
            organization = request.user.organization
        else:
            organization = attrs.get('organization')

        if organization and name:
            qs = Supplier.objects.filter(organization=organization, name__iexact=name)
            if self.instance is not None:
                qs = qs.exclude(pk=self.instance.pk)
            if qs.exists():
                raise serializers.ValidationError({
                    'name': 'A supplier with this company name already exists in your organization.'
                })

        return attrs
    
    def get_total_lpo_value(self, obj):
        """Calculate total value of all LPOs"""
        return sum(lpo.total_amount for lpo in obj.lpos.all())


class SupplierListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for supplier lists"""
    
    class Meta:
        model = Supplier
        fields = [
            'id', 'name', 'phone', 'email', 'tax_pin', 'is_active'
        ]
