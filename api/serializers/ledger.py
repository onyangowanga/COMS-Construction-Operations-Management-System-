"""
Ledger Serializers
Handles Expense and ExpenseAllocation serialization
"""
from rest_framework import serializers
from apps.ledger.models import Expense, ExpenseAllocation


class ExpenseAllocationSerializer(serializers.ModelSerializer):
    """Serializer for ExpenseAllocation model"""
    bq_item_description = serializers.CharField(source='bq_item.description', read_only=True)
    
    class Meta:
        model = ExpenseAllocation
        fields = [
            'id', 'expense', 'bq_item', 'bq_item_description',
            'allocated_amount', 'notes', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ExpenseSerializer(serializers.ModelSerializer):
    """Serializer for Expense model"""
    expense_type_display = serializers.CharField(source='get_expense_type_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    allocations = ExpenseAllocationSerializer(many=True, read_only=True)
    allocated_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True, 
        source='allocated_amount'
    )
    unallocated_amount = serializers.DecimalField(
        max_digits=15, 
        decimal_places=2, 
        read_only=True, 
        source='unallocated_amount'
    )
    allocation_status = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = [
            'id', 'project', 'project_code', 'expense_type',
            'expense_type_display', 'date', 'amount', 'reference_number',
            'description', 'allocations', 'allocated_amount',
            'unallocated_amount', 'allocation_status',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_allocation_status(self, obj):
        """Get allocation status"""
        if obj.unallocated_amount == 0:
            return 'FULLY_ALLOCATED'
        elif obj.allocated_amount > 0:
            return 'PARTIALLY_ALLOCATED'
        return 'NOT_ALLOCATED'


class ExpenseListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for expense lists"""
    expense_type_display = serializers.CharField(source='get_expense_type_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = Expense
        fields = [
            'id', 'project', 'project_code', 'expense_type',
            'expense_type_display', 'date', 'amount', 'reference_number'
        ]
