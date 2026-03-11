"""
Approval Serializers
Handles ProjectApproval serialization
"""
from rest_framework import serializers
from apps.approvals.models import ProjectApproval
from datetime import date


class ProjectApprovalSerializer(serializers.ModelSerializer):
    """Serializer for ProjectApproval model"""
    approval_type_display = serializers.CharField(source='get_approval_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    days_to_expiry = serializers.SerializerMethodField()
    is_expired = serializers.SerializerMethodField()
    is_expiring_soon = serializers.SerializerMethodField()
    
    class Meta:
        model = ProjectApproval
        fields = [
            'id', 'project', 'project_code', 'approval_type',
            'approval_type_display', 'reference_number', 'issue_date',
            'expiry_date', 'status', 'status_display', 'notes',
            'days_to_expiry', 'is_expired', 'is_expiring_soon',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_days_to_expiry(self, obj):
        """Calculate days until expiry"""
        if not obj.expiry_date:
            return None
        today = date.today()
        delta = obj.expiry_date - today
        return delta.days
    
    def get_is_expired(self, obj):
        """Check if approval is expired"""
        if not obj.expiry_date:
            return False
        return obj.expiry_date < date.today()
    
    def get_is_expiring_soon(self, obj):
        """Check if approval is expiring within 30 days"""
        if not obj.expiry_date:
            return False
        today = date.today()
        days_left = (obj.expiry_date - today).days
        return 0 < days_left <= 30


class ProjectApprovalListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for approval lists"""
    approval_type_display = serializers.CharField(source='get_approval_type_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    project_code = serializers.CharField(source='project.code', read_only=True)
    
    class Meta:
        model = ProjectApproval
        fields = [
            'id', 'project', 'project_code', 'approval_type',
            'approval_type_display', 'reference_number', 'status',
            'status_display', 'expiry_date'
        ]
