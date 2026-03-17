"""
Client Serializers
Handles ClientPayment and ClientReceipt serialization
"""
from rest_framework import serializers
from apps.clients.models import ClientPayment, ClientReceipt


class ClientReceiptSerializer(serializers.ModelSerializer):
    """Serializer for ClientReceipt model"""
    payment_amount = serializers.DecimalField(
        source='payment.amount',
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = ClientReceipt
        fields = [
            'id', 'payment', 'payment_amount', 'receipt_number',
            'document_path', 'issued_date', 'notes',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'issued_date', 'created_at', 'updated_at']
        extra_kwargs = {
            'receipt_number': {'required': False},
        }


class ClientPaymentSerializer(serializers.ModelSerializer):
    """Serializer for ClientPayment model"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    receipt = ClientReceiptSerializer(read_only=True)
    has_receipt = serializers.SerializerMethodField()
    
    class Meta:
        model = ClientPayment
        fields = [
            'id', 'project', 'project_code', 'amount', 'payment_date',
            'payment_method', 'payment_method_display', 'reference_number',
            'description', 'receipt', 'has_receipt',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_has_receipt(self, obj):
        """Check if receipt was issued"""
        return hasattr(obj, 'receipt')


class ClientPaymentListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for payment lists"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = ClientPayment
        fields = [
            'id', 'project', 'project_code', 'amount', 'payment_date',
            'payment_method', 'payment_method_display', 'reference_number'
        ]
