"""
Consultant Serializers
Handles Consultant, ProjectConsultant, ConsultantFee, ConsultantPayment serialization
"""
from rest_framework import serializers
from apps.consultants.models import (
    Consultant, ProjectConsultant, ConsultantFee, ConsultantPayment
)


class ConsultantPaymentSerializer(serializers.ModelSerializer):
    """Serializer for ConsultantPayment model"""
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    
    class Meta:
        model = ConsultantPayment
        fields = [
            'id', 'consultant_fee', 'amount', 'payment_date',
            'payment_method', 'payment_method_display',
            'reference_number', 'notes', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class ConsultantFeeSerializer(serializers.ModelSerializer):
    """Serializer for ConsultantFee model"""
    fee_type_display = serializers.CharField(source='get_fee_type_display', read_only=True)
    payments = ConsultantPaymentSerializer(many=True, read_only=True)
    total_paid = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True, source='total_paid')
    balance_due = serializers.SerializerMethodField()
    
    class Meta:
        model = ConsultantFee
        fields = [
            'id', 'consultant', 'project', 'fee_type', 'fee_type_display',
            'contract_amount', 'payment_schedule', 'payments',
            'total_paid', 'balance_due', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_balance_due(self, obj):
        """Calculate remaining balance"""
        return obj.contract_amount - obj.total_paid


class ProjectConsultantSerializer(serializers.ModelSerializer):
    """Serializer for ProjectConsultant model"""
    consultant_name = serializers.CharField(source='consultant.name', read_only=True)
    consultant_type = serializers.CharField(source='consultant.get_consultant_type_display', read_only=True)
    
    class Meta:
        model = ProjectConsultant
        fields = [
            'id', 'project', 'consultant', 'consultant_name',
            'consultant_type', 'role', 'assigned_date', 'is_active'
        ]
        read_only_fields = ['id', 'assigned_date']


class ConsultantSerializer(serializers.ModelSerializer):
    """Serializer for Consultant model"""
    consultant_type_display = serializers.CharField(source='get_consultant_type_display', read_only=True)
    project_assignments = ProjectConsultantSerializer(many=True, read_only=True)
    fees = ConsultantFeeSerializer(many=True, read_only=True)
    total_fees = serializers.SerializerMethodField()
    
    class Meta:
        model = Consultant
        fields = [
            'id', 'organization', 'name', 'consultant_type',
            'consultant_type_display', 'company', 'phone', 'email',
            'address', 'is_active', 'project_assignments', 'fees',
            'total_fees', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_total_fees(self, obj):
        """Calculate total fees across all projects"""
        return sum(fee.contract_amount for fee in obj.fees.all())


class ConsultantListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for consultant lists"""
    consultant_type_display = serializers.CharField(source='get_consultant_type_display', read_only=True)
    
    class Meta:
        model = Consultant
        fields = [
            'id', 'name', 'consultant_type', 'consultant_type_display',
            'company', 'phone', 'email', 'is_active'
        ]
