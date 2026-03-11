"""
Valuation Serializers
REST API serializers for valuations and BQ item progress
"""
from rest_framework import serializers
from decimal import Decimal

from apps.valuations.models import Valuation, BQItemProgress
from apps.projects.models import Project
from apps.bq.models import BQItem


class BQItemProgressSerializer(serializers.ModelSerializer):
    """Serializer for BQ item progress tracking"""
    
    bq_item_description = serializers.CharField(source='bq_item.description', read_only=True)
    bq_item_unit = serializers.CharField(source='bq_item.unit', read_only=True)
    bq_item_rate = serializers.DecimalField(
        source='bq_item.rate',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    bq_item_quantity = serializers.DecimalField(
        source='bq_item.quantity',
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    percentage_complete = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    element_name = serializers.CharField(source='bq_item.element.name', read_only=True)
    section_name = serializers.CharField(source='bq_item.element.section.name', read_only=True)
    
    class Meta:
        model = BQItemProgress
        fields = [
            'id',
            'bq_item',
            'bq_item_description',
            'bq_item_unit',
            'bq_item_rate',
            'bq_item_quantity',
            'element_name',
            'section_name',
            'previous_quantity',
            'this_quantity',
            'cumulative_quantity',
            'previous_value',
            'this_value',
            'cumulative_value',
            'percentage_complete',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'cumulative_quantity',
            'previous_value',
            'this_value',
            'cumulative_value',
            'created_at',
            'updated_at'
        ]


class BQItemProgressCreateSerializer(serializers.Serializer):
    """Serializer for creating BQ item progress (nested in valuation creation)"""
    
    bq_item_id = serializers.UUIDField()
    this_quantity = serializers.DecimalField(max_digits=12, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def validate_bq_item_id(self, value):
        """Validate BQ item exists"""
        try:
            BQItem.objects.get(id=value)
        except BQItem.DoesNotExist:
            raise serializers.ValidationError("BQ item not found")
        return value
    
    def validate_this_quantity(self, value):
        """Validate quantity is non-negative"""
        if value < 0:
            raise serializers.ValidationError("Quantity cannot be negative")
        return value


class ValuationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for valuation lists"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    gross_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    net_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Valuation
        fields = [
            'id',
            'project',
            'project_name',
            'project_code',
            'valuation_number',
            'valuation_date',
            'work_completed_value',
            'retention_percentage',
            'retention_amount',
            'previous_payments',
            'gross_amount',
            'amount_due',
            'net_amount',
            'status',
            'submitted_by_name',
            'created_at'
        ]


class ValuationSerializer(serializers.ModelSerializer):
    """Full serializer for valuation detail view"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    submitted_by_name = serializers.CharField(
        source='submitted_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    approved_by_name = serializers.CharField(
        source='approved_by.get_full_name',
        read_only=True,
        allow_null=True
    )
    item_progress = BQItemProgressSerializer(many=True, read_only=True)
    gross_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    net_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Valuation
        fields = [
            'id',
            'project',
            'project_name',
            'project_code',
            'valuation_number',
            'valuation_date',
            'work_completed_value',
            'retention_percentage',
            'retention_amount',
            'previous_payments',
            'gross_amount',
            'amount_due',
            'net_amount',
            'status',
            'notes',
            'submitted_by',
            'submitted_by_name',
            'approved_by',
            'approved_by_name',
            'approved_date',
            'payment_date',
            'item_progress',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'valuation_number',
            'work_completed_value',
            'retention_amount',
            'previous_payments',
            'amount_due',
            'created_at',
            'updated_at'
        ]


class ValuationCreateSerializer(serializers.Serializer):
    """Serializer for creating a new valuation"""
    
    project_id = serializers.UUIDField()
    valuation_date = serializers.DateField()
    retention_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        default=Decimal('10.00')
    )
    notes = serializers.CharField(required=False, allow_blank=True, default="")
    progress_items = BQItemProgressCreateSerializer(many=True)
    
    def validate_project_id(self, value):
        """Validate project exists"""
        try:
            Project.objects.get(id=value)
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
        return value
    
    def validate_retention_percentage(self, value):
        """Validate retention percentage is within acceptable range"""
        if value < 0 or value > 100:
            raise serializers.ValidationError("Retention percentage must be between 0 and 100")
        return value
    
    def validate_progress_items(self, value):
        """Validate at least one progress item is provided"""
        if not value:
            raise serializers.ValidationError("At least one progress item is required")
        return value


class ValuationUpdateSerializer(serializers.Serializer):
    """Serializer for updating an existing valuation"""
    
    retention_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    status = serializers.ChoiceField(
        choices=Valuation.Status.choices,
        required=False
    )
    progress_items = BQItemProgressCreateSerializer(many=True, required=False)
    
    def validate_retention_percentage(self, value):
        """Validate retention percentage"""
        if value is not None and (value < 0 or value > 100):
            raise serializers.ValidationError("Retention percentage must be between 0 and 100")
        return value


class ValuationApprovalSerializer(serializers.Serializer):
    """Serializer for approving a valuation"""
    
    approved_by_id = serializers.UUIDField()
    
    def validate_approved_by_id(self, value):
        """Validate user exists"""
        from apps.authentication.models import User
        try:
            User.objects.get(id=value)
        except User.DoesNotExist:
            raise serializers.ValidationError("User not found")
        return value


class ValuationRejectSerializer(serializers.Serializer):
    """Serializer for rejecting a valuation"""
    
    notes = serializers.CharField(required=True)
    
    def validate_notes(self, value):
        """Ensure rejection reason is provided"""
        if not value or not value.strip():
            raise serializers.ValidationError("Rejection reason is required")
        return value


class ValuationPaymentSerializer(serializers.Serializer):
    """Serializer for marking valuation as paid"""
    
    payment_date = serializers.DateField()


class ValuationSummarySerializer(serializers.Serializer):
    """Serializer for valuation summary statistics"""
    
    total_valuations = serializers.IntegerField()
    total_certified = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_payment = serializers.DecimalField(max_digits=15, decimal_places=2)
    retention_held = serializers.DecimalField(max_digits=15, decimal_places=2)
    latest_valuation_number = serializers.CharField(allow_null=True)
    latest_valuation_date = serializers.DateField(allow_null=True)
    latest_amount_due = serializers.DecimalField(max_digits=15, decimal_places=2)
