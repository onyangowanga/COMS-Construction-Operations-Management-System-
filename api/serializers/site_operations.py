"""
Site Operations API Serializers

Serializers for:
- Daily Site Reports
- Material Deliveries
- Site Issues
"""

from rest_framework import serializers
from decimal import Decimal
from datetime import date

from apps.site_operations.models import (
    DailySiteReport,
    MaterialDelivery,
    SiteIssue
)
from apps.authentication.models import User
from apps.projects.models import Project


# ===== User Serializers =====

class SiteOperationsUserSerializer(serializers.ModelSerializer):
    """Lightweight user serializer for site operations"""
    
    class Meta:
        model = User
        fields = ['id', 'email', 'first_name', 'last_name', 'full_name']
        read_only_fields = fields


# ===== Daily Site Report Serializers =====

class DailySiteReportListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing site reports"""
    
    prepared_by = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    has_issues = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = DailySiteReport
        fields = [
            'id',
            'project',
            'project_name',
            'report_date',
            'weather',
            'prepared_by',
            'has_issues',
            'created_at'
        ]
        read_only_fields = fields


class DailySiteReportSerializer(serializers.ModelSerializer):
    """Full serializer for site report details"""
    
    prepared_by = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    has_issues = serializers.BooleanField(read_only=True)
    weather_display = serializers.CharField(source='get_weather_display', read_only=True)
    
    class Meta:
        model = DailySiteReport
        fields = [
            'id',
            'project',
            'project_name',
            'report_date',
            'weather',
            'weather_display',
            'labour_summary',
            'work_completed',
            'materials_delivered',
            'issues',
            'prepared_by',
            'has_issues',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'prepared_by',
            'has_issues',
            'created_at',
            'updated_at'
        ]


class DailySiteReportCreateSerializer(serializers.Serializer):
    """Serializer for creating site reports"""
    
    project_id = serializers.UUIDField()
    report_date = serializers.DateField()
    weather = serializers.ChoiceField(choices=DailySiteReport.WEATHER_CHOICES)
    labour_summary = serializers.CharField()
    work_completed = serializers.CharField()
    materials_delivered = serializers.CharField(required=False, allow_blank=True, default='')
    issues = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_project_id(self, value):
        """Validate project exists"""
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project not found")
        return value
    
    def validate_report_date(self, value):
        """Validate report date is not in the future"""
        if value > date.today():
            raise serializers.ValidationError("Report date cannot be in the future")
        return value


class DailySiteReportUpdateSerializer(serializers.Serializer):
    """Serializer for updating site reports"""
    
    weather = serializers.ChoiceField(choices=DailySiteReport.WEATHER_CHOICES, required=False)
    labour_summary = serializers.CharField(required=False)
    work_completed = serializers.CharField(required=False)
    materials_delivered = serializers.CharField(required=False, allow_blank=True)
    issues = serializers.CharField(required=False, allow_blank=True)


# ===== Material Delivery Serializers =====

class MaterialDeliveryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing deliveries"""
    
    received_by = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    supplier_display = serializers.CharField(read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MaterialDelivery
        fields = [
            'id',
            'project',
            'project_name',
            'material_name',
            'quantity',
            'unit',
            'supplier_display',
            'delivery_note_number',
            'delivery_date',
            'status',
            'status_display',
            'received_by',
            'created_at'
        ]
        read_only_fields = fields


class MaterialDeliverySerializer(serializers.ModelSerializer):
    """Full serializer for delivery details"""
    
    received_by = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    supplier_display = serializers.CharField(read_only=True)
    supplier_name_display = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = MaterialDelivery
        fields = [
            'id',
            'project',
            'project_name',
            'supplier',
            'supplier_name',
            'supplier_display',
            'supplier_name_display',
            'material_name',
            'quantity',
            'unit',
            'delivery_note_number',
            'delivery_date',
            'received_by',
            'status',
            'status_display',
            'notes',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'received_by',
            'supplier_display',
            'created_at',
            'updated_at'
        ]
    
    def get_supplier_name_display(self, obj):
        """Get supplier name for display"""
        if obj.supplier:
            return obj.supplier.name
        return obj.supplier_name or 'Unknown'


class MaterialDeliveryCreateSerializer(serializers.Serializer):
    """Serializer for creating material deliveries"""
    
    project_id = serializers.UUIDField()
    material_name = serializers.CharField(max_length=255)
    quantity = serializers.DecimalField(max_digits=12, decimal_places=2, min_value=Decimal('0.01'))
    unit = serializers.CharField(max_length=50, default='units')
    delivery_note_number = serializers.CharField(max_length=100)
    delivery_date = serializers.DateField()
    supplier_id = serializers.UUIDField(required=False, allow_null=True)
    supplier_name = serializers.CharField(max_length=255, required=False, allow_blank=True)
    status = serializers.ChoiceField(choices=MaterialDelivery.STATUS_CHOICES, default='PENDING')
    notes = serializers.CharField(required=False, allow_blank=True, default='')
    
    def validate_project_id(self, value):
        """Validate project exists"""
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project not found")
        return value
    
    def validate(self, data):
        """Validate supplier information"""
        if not data.get('supplier_id') and not data.get('supplier_name'):
            raise serializers.ValidationError({
                'supplier': 'Either supplier_id or supplier_name must be provided'
            })
        return data


class MaterialDeliveryStatusUpdateSerializer(serializers.Serializer):
    """Serializer for updating delivery status"""
    
    status = serializers.ChoiceField(choices=MaterialDelivery.STATUS_CHOICES)
    notes = serializers.CharField(required=False, allow_blank=True)


# ===== Site Issue Serializers =====

class SiteIssueListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing issues"""
    
    reported_by = SiteOperationsUserSerializer(read_only=True)
    assigned_to = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    is_high_priority = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SiteIssue
        fields = [
            'id',
            'project',
            'project_name',
            'title',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'reported_by',
            'assigned_to',
            'reported_date',
            'is_open',
            'is_high_priority',
            'created_at'
        ]
        read_only_fields = fields


class SiteIssueSerializer(serializers.ModelSerializer):
    """Full serializer for issue details"""
    
    reported_by = SiteOperationsUserSerializer(read_only=True)
    assigned_to = SiteOperationsUserSerializer(read_only=True)
    project_name = serializers.CharField(source='project.name', read_only=True)
    severity_display = serializers.CharField(source='get_severity_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_open = serializers.BooleanField(read_only=True)
    is_high_priority = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = SiteIssue
        fields = [
            'id',
            'project',
            'project_name',
            'title',
            'description',
            'severity',
            'severity_display',
            'status',
            'status_display',
            'reported_by',
            'assigned_to',
            'reported_date',
            'resolved_date',
            'resolution_notes',
            'is_open',
            'is_high_priority',
            'created_at',
            'updated_at'
        ]
        read_only_fields = [
            'id',
            'reported_by',
            'reported_date',
            'is_open',
            'is_high_priority',
            'created_at',
            'updated_at'
        ]


class SiteIssueCreateSerializer(serializers.Serializer):
    """Serializer for creating site issues"""
    
    project_id = serializers.UUIDField()
    title = serializers.CharField(max_length=255)
    description = serializers.CharField()
    severity = serializers.ChoiceField(choices=SiteIssue.SEVERITY_CHOICES, default='MEDIUM')
    assigned_to_id = serializers.UUIDField(required=False, allow_null=True)
    status = serializers.ChoiceField(choices=SiteIssue.STATUS_CHOICES, default='OPEN')
    
    def validate_project_id(self, value):
        """Validate project exists"""
        if not Project.objects.filter(id=value).exists():
            raise serializers.ValidationError("Project not found")
        return value
    
    def validate_assigned_to_id(self, value):
        """Validate assigned user exists"""
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found")
        return value


class SiteIssueUpdateSerializer(serializers.Serializer):
    """Serializer for updating site issues"""
    
    title = serializers.CharField(max_length=255, required=False)
    description = serializers.CharField(required=False)
    severity = serializers.ChoiceField(choices=SiteIssue.SEVERITY_CHOICES, required=False)
    status = serializers.ChoiceField(choices=SiteIssue.STATUS_CHOICES, required=False)
    assigned_to_id = serializers.UUIDField(required=False, allow_null=True)
    
    def validate_assigned_to_id(self, value):
        """Validate assigned user exists"""
        if value and not User.objects.filter(id=value).exists():
            raise serializers.ValidationError("User not found")
        return value


class SiteIssueResolveSerializer(serializers.Serializer):
    """Serializer for resolving issues"""
    
    resolution_notes = serializers.CharField()


class SiteIssueReopenSerializer(serializers.Serializer):
    """Serializer for reopening issues"""
    
    reason = serializers.CharField()


# ===== Summary Serializers =====

class SiteOperationsSummarySerializer(serializers.Serializer):
    """Serializer for site operations summary data"""
    
    total_reports = serializers.IntegerField()
    recent_reports_count = serializers.IntegerField()
    total_deliveries = serializers.IntegerField()
    pending_deliveries = serializers.IntegerField()
    total_issues = serializers.IntegerField()
    open_issues_count = serializers.IntegerField()
    high_priority_issues = serializers.IntegerField()
    issues_by_severity = serializers.DictField()
    latest_report = DailySiteReportListSerializer(allow_null=True)
    latest_delivery = MaterialDeliveryListSerializer(allow_null=True)
    latest_issue = SiteIssueListSerializer(allow_null=True)
