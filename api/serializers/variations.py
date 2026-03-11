"""
Variation Order API Serializers
"""

from rest_framework import serializers
from apps.variations.models import VariationOrder
from apps.projects.models import Project
from apps.authentication.models import User


class UserBasicSerializer(serializers.ModelSerializer):
    """Basic user info for nested serialization"""
    
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'full_name']
        read_only_fields = fields
    
    def get_full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}".strip() or obj.username


class ProjectBasicSerializer(serializers.ModelSerializer):
    """Basic project info for nested serialization"""
    
    organization_name = serializers.CharField(
        source='organization.name',
        read_only=True
    )
    
    class Meta:
        model = Project
        fields = [
            'id',
            'name',
            'project_code',
            'status',
            'organization_name',
            'contract_sum',
        ]
        read_only_fields = fields


class VariationOrderSerializer(serializers.ModelSerializer):
    """Full variation order serializer"""
    
    project = ProjectBasicSerializer(read_only=True)
    project_id = serializers.UUIDField(write_only=True)
    
    created_by = UserBasicSerializer(read_only=True)
    submitted_by = UserBasicSerializer(read_only=True)
    approved_by = UserBasicSerializer(read_only=True)
    
    status_display = serializers.CharField(
        source='get_status_display',
        read_only=True
    )
    priority_display = serializers.CharField(
        source='get_priority_display',
        read_only=True
    )
    change_type_display = serializers.CharField(
        source='get_change_type_display',
        read_only=True
    )
    
    # Computed properties
    value_variance = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    outstanding_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    # Permission checks
    can_submit = serializers.BooleanField(read_only=True)
    can_approve = serializers.BooleanField(read_only=True)
    can_reject = serializers.BooleanField(read_only=True)
    can_invoice = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = VariationOrder
        fields = [
            'id',
            'project',
            'project_id',
            'reference_number',
            'title',
            'description',
            'change_type',
            'change_type_display',
            'priority',
            'priority_display',
            'instruction_date',
            'required_by_date',
            'estimated_value',
            'approved_value',
            'invoiced_value',
            'paid_value',
            'value_variance',
            'outstanding_amount',
            'status',
            'status_display',
            'justification',
            'client_reference',
            'impact_on_schedule',
            'technical_notes',
            'rejection_reason',
            'created_by',
            'submitted_by',
            'approved_by',
            'submitted_date',
            'approved_date',
            'created_at',
            'updated_at',
            'can_submit',
            'can_approve',
            'can_reject',
            'can_invoice',
        ]
        read_only_fields = [
            'id',
            'reference_number',
            'submitted_date',
            'approved_date',
            'created_at',
            'updated_at',
        ]


class VariationOrderCreateSerializer(serializers.ModelSerializer):
    """Serializer for creating variation orders"""
    
    project_id = serializers.UUIDField()
    
    class Meta:
        model = VariationOrder
        fields = [
            'project_id',
            'title',
            'description',
            'change_type',
            'priority',
            'instruction_date',
            'required_by_date',
            'estimated_value',
            'justification',
            'client_reference',
            'impact_on_schedule',
            'technical_notes',
        ]
    
    def create(self, validated_data):
        """Create variation order via service layer"""
        from apps.variations.services import VariationService
        
        project_id = validated_data.pop('project_id')
        user = self.context['request'].user
        
        return VariationService.create_variation(
            project_id=str(project_id),
            created_by=user,
            **validated_data
        )


class VariationOrderListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for list views"""
    
    project_name = serializers.CharField(source='project.name', read_only=True)
    project_code = serializers.CharField(source='project.project_code', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    outstanding_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = VariationOrder
        fields = [
            'id',
            'reference_number',
            'project_name',
            'project_code',
            'title',
            'status',
            'status_display',
            'priority',
            'priority_display',
            'estimated_value',
            'approved_value',
            'outstanding_amount',
            'instruction_date',
            'created_at',
        ]


class VariationSubmitSerializer(serializers.Serializer):
    """Serializer for submitting variation for approval"""
    
    variation_id = serializers.UUIDField()
    
    def create(self, validated_data):
        """Submit variation via service layer"""
        from apps.variations.services import VariationService
        
        user = self.context['request'].user
        
        return VariationService.submit_for_approval(
            variation_id=str(validated_data['variation_id']),
            submitted_by=user
        )


class VariationApproveSerializer(serializers.Serializer):
    """Serializer for approving variations"""
    
    variation_id = serializers.UUIDField()
    approved_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        required=False
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Approve variation via service layer"""
        from apps.variations.services import VariationService
        
        user = self.context['request'].user
        
        return VariationService.approve_variation(
            variation_id=str(validated_data['variation_id']),
            approved_by=user,
            approved_value=validated_data.get('approved_value'),
            notes=validated_data.get('notes', '')
        )


class VariationRejectSerializer(serializers.Serializer):
    """Serializer for rejecting variations"""
    
    variation_id = serializers.UUIDField()
    rejection_reason = serializers.CharField()
    
    def create(self, validated_data):
        """Reject variation via service layer"""
        from apps.variations.services import VariationService
        
        user = self.context['request'].user
        
        return VariationService.reject_variation(
            variation_id=str(validated_data['variation_id']),
            rejected_by=user,
            rejection_reason=validated_data['rejection_reason']
        )


class ProjectVariationSummarySerializer(serializers.Serializer):
    """Serializer for project variation summary"""
    
    total_variations = serializers.IntegerField()
    status_breakdown = serializers.DictField()
    total_estimated_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_approved_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_invoiced_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    outstanding_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_variation_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    largest_variation_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    contract_impact_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    original_contract_sum = serializers.DecimalField(max_digits=15, decimal_places=2)
    revised_contract_sum = serializers.DecimalField(max_digits=15, decimal_places=2)


class VariationTrendDataSerializer(serializers.Serializer):
    """Serializer for variation trend data"""
    
    month = serializers.CharField()
    month_label = serializers.CharField()
    variation_count = serializers.IntegerField()
    total_estimated = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_approved = serializers.DecimalField(max_digits=15, decimal_places=2)
    approved_count = serializers.IntegerField()


class PortfolioVariationSummarySerializer(serializers.Serializer):
    """Serializer for portfolio-wide variation summary"""
    
    total_variations = serializers.IntegerField()
    pending_approval = serializers.IntegerField()
    approved = serializers.IntegerField()
    rejected = serializers.IntegerField()
    urgent = serializers.IntegerField()
    total_estimated_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_approved_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_outstanding_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    projects_affected = serializers.IntegerField()
