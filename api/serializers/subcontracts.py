"""
Subcontractor Management - API Serializers

Comprehensive serializers for subcontract operations including:
- Subcontractor CRUD
- Subcontract agreement management
- Payment claim workflow
- Financial summaries
"""

from decimal import Decimal
from rest_framework import serializers
from django.utils import timezone
from django.db import IntegrityError
from django.core.exceptions import ValidationError as DjangoValidationError

from apps.subcontracts.models import (
    Subcontractor,
    SubcontractAgreement,
    SubcontractClaim
)
from apps.subcontracts.services import SubcontractService
from apps.subcontracts.selectors import ClaimSelector


class UserBasicSerializer(serializers.Serializer):
    """Basic user info for nested serialization"""
    id = serializers.UUIDField()
    username = serializers.CharField()
    full_name = serializers.CharField(source='get_full_name')
    email = serializers.EmailField()


class ProjectBasicSerializer(serializers.Serializer):
    """Basic project info for nested serialization"""
    id = serializers.UUIDField()
    code = serializers.CharField()
    name = serializers.CharField()


class SubcontractorBasicSerializer(serializers.ModelSerializer):
    """Basic subcontractor info for nested use"""
    active_contracts_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = Subcontractor
        fields = [
            'id',
            'name',
            'specialization',
            'contact_person',
            'phone',
            'email',
            'is_active',
            'active_contracts_count',
        ]


class SubcontractorSerializer(serializers.ModelSerializer):
    """
    Full subcontractor serializer with statistics.
    
    Used for detail views and complete subcontractor information.
    """
    created_by_data = UserBasicSerializer(source='created_by', read_only=True)
    active_contracts_count = serializers.IntegerField(read_only=True)
    total_contract_value = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Subcontractor
        fields = [
            'id',
            'organization',
            'name',
            'company_registration',
            'tax_number',
            'contact_person',
            'phone',
            'email',
            'address',
            'specialization',
            'is_active',
            'notes',
            'created_by',
            'created_by_data',
            'created_at',
            'updated_at',
            'active_contracts_count',
            'total_contract_value',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class SubcontractorCreateSerializer(serializers.Serializer):
    """Serializer for creating new subcontractors"""
    name = serializers.CharField(max_length=255)
    contact_person = serializers.CharField(max_length=255)
    phone = serializers.CharField(max_length=20)
    email = serializers.EmailField()
    address = serializers.CharField()
    company_registration = serializers.CharField(max_length=100, required=False, allow_blank=True)
    tax_number = serializers.CharField(max_length=100, required=False, allow_blank=True)
    specialization = serializers.CharField(max_length=255, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate(self, attrs):
        """Validate organization context and avoid DB-level unique crashes."""
        request = self.context.get('request')
        user = getattr(request, 'user', None)

        if not user or not getattr(user, 'organization', None):
            raise serializers.ValidationError({
                'organization': 'Your account is not linked to an organization. Please contact an administrator.'
            })

        name = attrs.get('name', '').strip()
        if Subcontractor.objects.filter(organization=user.organization, name__iexact=name).exists():
            raise serializers.ValidationError({
                'name': 'A subcontractor with this name already exists in your organization.'
            })

        attrs['name'] = name
        return attrs
    
    def create(self, validated_data):
        """Create subcontractor using service layer"""
        user = self.context['request'].user

        try:
            subcontractor = SubcontractService.create_subcontractor(
                organization=user.organization,
                name=validated_data['name'],
                contact_person=validated_data['contact_person'],
                phone=validated_data['phone'],
                email=validated_data['email'],
                address=validated_data['address'],
                created_by=user,
                company_registration=validated_data.get('company_registration', ''),
                tax_number=validated_data.get('tax_number', ''),
                specialization=validated_data.get('specialization', ''),
                notes=validated_data.get('notes', '')
            )
            return subcontractor
        except DjangoValidationError as exc:
            raise serializers.ValidationError({'non_field_errors': exc.messages})
        except IntegrityError:
            raise serializers.ValidationError({
                'name': 'A subcontractor with this name already exists in your organization.'
            })


class SubcontractAgreementBasicSerializer(serializers.ModelSerializer):
    """Basic subcontract info for nested use"""
    subcontractor_name = serializers.CharField(source='subcontractor.name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    completion_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = SubcontractAgreement
        fields = [
            'id',
            'contract_reference',
            'subcontractor',
            'subcontractor_name',
            'contract_value',
            'status',
            'status_display',
            'start_date',
            'end_date',
            'completion_percentage',
        ]


class SubcontractAgreementSerializer(serializers.ModelSerializer):
    """
    Full subcontract agreement serializer.
    
    Used for detail views with complete contract information.
    """
    project_data = ProjectBasicSerializer(source='project', read_only=True)
    subcontractor_data = SubcontractorBasicSerializer(source='subcontractor', read_only=True)
    created_by_data = UserBasicSerializer(source='created_by', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed properties
    duration_days = serializers.IntegerField(read_only=True)
    is_active = serializers.BooleanField(read_only=True)
    retention_amount = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_claimed = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_certified = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    completion_percentage = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)
    outstanding_balance = serializers.DecimalField(max_digits=15, decimal_places=2, read_only=True)
    
    class Meta:
        model = SubcontractAgreement
        fields = [
            'id',
            'project',
            'project_data',
            'subcontractor',
            'subcontractor_data',
            'contract_reference',
            'scope_of_work',
            'contract_value',
            'retention_percentage',
            'start_date',
            'end_date',
            'status',
            'status_display',
            'payment_terms',
            'vat_applicable',
            'performance_bond_required',
            'performance_bond_percentage',
            'notes',
            'created_by',
            'created_by_data',
            'created_at',
            'updated_at',
            'activated_at',
            'completed_at',
            # Computed
            'duration_days',
            'is_active',
            'retention_amount',
            'total_claimed',
            'total_certified',
            'total_paid',
            'completion_percentage',
            'outstanding_balance',
        ]
        read_only_fields = [
            'id',
            'created_at',
            'updated_at',
            'activated_at',
            'completed_at'
        ]


class SubcontractCreateSerializer(serializers.Serializer):
    """Serializer for creating new subcontracts"""
    project = serializers.UUIDField()
    subcontractor = serializers.UUIDField()
    contract_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    scope_of_work = serializers.CharField()
    contract_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    retention_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('10.00')
    )
    start_date = serializers.DateField()
    end_date = serializers.DateField()
    payment_terms = serializers.CharField(max_length=255, required=False, allow_blank=True)
    vat_applicable = serializers.BooleanField(default=True)
    performance_bond_required = serializers.BooleanField(default=False)
    performance_bond_percentage = serializers.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=False,
        allow_null=True
    )
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Create subcontract using service layer"""
        from apps.projects.models import Project
        
        user = self.context['request'].user
        
        # Get project
        try:
            project = Project.objects.get(id=validated_data['project'])
        except Project.DoesNotExist:
            raise serializers.ValidationError("Project not found")
        
        # Get subcontractor
        try:
            subcontractor = Subcontractor.objects.get(
                id=validated_data['subcontractor']
            )
        except Subcontractor.DoesNotExist:
            raise serializers.ValidationError("Subcontractor not found")
        
        # Create subcontract
        subcontract = SubcontractService.create_subcontract(
            project=project,
            subcontractor=subcontractor,
            contract_reference=validated_data.get('contract_reference'),
            scope_of_work=validated_data['scope_of_work'],
            contract_value=validated_data['contract_value'],
            start_date=validated_data['start_date'],
            end_date=validated_data['end_date'],
            created_by=user,
            retention_percentage=validated_data.get('retention_percentage', Decimal('10.00')),
            payment_terms=validated_data.get('payment_terms', ''),
            vat_applicable=validated_data.get('vat_applicable', True),
            performance_bond_required=validated_data.get('performance_bond_required', False),
            performance_bond_percentage=validated_data.get('performance_bond_percentage'),
            notes=validated_data.get('notes', '')
        )
        
        return subcontract


class SubcontractClaimSerializer(serializers.ModelSerializer):
    """
    Full subcontract claim serializer.
    
    Used for detail views with complete claim information.
    """
    subcontract_data = SubcontractAgreementBasicSerializer(source='subcontract', read_only=True)
    submitted_by_data = UserBasicSerializer(source='submitted_by', read_only=True)
    certified_by_data = UserBasicSerializer(source='certified_by', read_only=True)
    
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    # Computed properties
    cumulative_certified_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    net_payment_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    is_pending_certification = serializers.BooleanField(read_only=True)
    is_pending_payment = serializers.BooleanField(read_only=True)
    period_days = serializers.IntegerField(read_only=True)
    variance_amount = serializers.DecimalField(
        max_digits=15,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = SubcontractClaim
        fields = [
            'id',
            'subcontract',
            'subcontract_data',
            'claim_number',
            'period_start',
            'period_end',
            'claimed_amount',
            'certified_amount',
            'retention_amount',
            'previous_cumulative_amount',
            'status',
            'status_display',
            'submitted_date',
            'certified_date',
            'paid_date',
            'description',
            'rejection_reason',
            'notes',
            'submitted_by',
            'submitted_by_data',
            'certified_by',
            'certified_by_data',
            'created_by',
            'created_at',
            'updated_at',
            # Computed
            'cumulative_certified_amount',
            'net_payment_amount',
            'is_pending_certification',
            'is_pending_payment',
            'period_days',
            'variance_amount',
        ]
        read_only_fields = [
            'id',
            'certified_amount',
            'retention_amount',
            'previous_cumulative_amount',
            'submitted_date',
            'certified_date',
            'paid_date',
            'created_at',
            'updated_at',
        ]


class ClaimSubmitSerializer(serializers.Serializer):
    """Serializer for submitting new payment claims"""
    subcontract = serializers.UUIDField()
    claim_number = serializers.CharField(max_length=50, required=False, allow_blank=True)
    period_start = serializers.DateField()
    period_end = serializers.DateField()
    claimed_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def create(self, validated_data):
        """Submit claim using service layer"""
        user = self.context['request'].user
        
        # Get subcontract
        try:
            subcontract = SubcontractAgreement.objects.get(
                id=validated_data['subcontract']
            )
        except SubcontractAgreement.DoesNotExist:
            raise serializers.ValidationError("Subcontract not found")
        
        # Submit claim
        claim = SubcontractService.submit_claim(
            subcontract=subcontract,
            claim_number=validated_data.get('claim_number'),
            period_start=validated_data['period_start'],
            period_end=validated_data['period_end'],
            claimed_amount=validated_data['claimed_amount'],
            submitted_by=user,
            description=validated_data.get('description', ''),
            notes=validated_data.get('notes', '')
        )
        
        return claim


class ClaimCertifySerializer(serializers.Serializer):
    """Serializer for certifying payment claims"""
    certified_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    notes = serializers.CharField(required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        """Certify claim using service layer"""
        user = self.context['request'].user
        
        certified_claim = SubcontractService.certify_claim(
            claim=instance,
            certified_amount=validated_data['certified_amount'],
            certified_by=user,
            notes=validated_data.get('notes', '')
        )
        
        return certified_claim


class ClaimRejectSerializer(serializers.Serializer):
    """Serializer for rejecting payment claims"""
    rejection_reason = serializers.CharField()
    
    def update(self, instance, validated_data):
        """Reject claim using service layer"""
        user = self.context['request'].user
        
        rejected_claim = SubcontractService.reject_claim(
            claim=instance,
            rejection_reason=validated_data['rejection_reason'],
            rejected_by=user
        )
        
        return rejected_claim


class ClaimMarkPaidSerializer(serializers.Serializer):
    """Serializer for marking claims as paid"""
    payment_reference = serializers.CharField(max_length=100, required=False, allow_blank=True)
    
    def update(self, instance, validated_data):
        """Mark claim as paid using service layer"""
        user = self.context['request'].user
        
        paid_claim = SubcontractService.mark_claim_paid(
            claim=instance,
            paid_by=user,
            payment_reference=validated_data.get('payment_reference', '')
        )
        
        return paid_claim


class SubcontractSummarySerializer(serializers.Serializer):
    """Serializer for project subcontract summary statistics"""
    total_contracts = serializers.IntegerField()
    active_contracts = serializers.IntegerField()
    total_contract_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_certified = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    avg_completion = serializers.DecimalField(max_digits=5, decimal_places=2)


class PaymentSummarySerializer(serializers.Serializer):
    """Serializer for subcontract payment summary"""
    contract_value = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_claims = serializers.IntegerField()
    total_claimed = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_certified = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_retention = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_paid = serializers.DecimalField(max_digits=15, decimal_places=2)
    outstanding_certified = serializers.DecimalField(max_digits=15, decimal_places=2)
    completion_percentage = serializers.DecimalField(max_digits=5, decimal_places=2)
    variance = serializers.DecimalField(max_digits=15, decimal_places=2)
    pending_certification_count = serializers.IntegerField()
    pending_payment_count = serializers.IntegerField()
