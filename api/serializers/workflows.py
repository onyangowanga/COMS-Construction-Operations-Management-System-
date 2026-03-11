"""
Workflow Serializers
Handles serialization for Approval and ProjectActivity models
"""
from rest_framework import serializers
from apps.workflows.models import Approval, ProjectActivity


class ApprovalSerializer(serializers.ModelSerializer):
    """
    Serializer for Approval model
    """
    requested_by_email = serializers.EmailField(source='requested_by.email', read_only=True)
    approved_by_email = serializers.EmailField(source='approved_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_type_display = serializers.CharField(source='get_approval_type_display', read_only=True)
    
    class Meta:
        model = Approval
        fields = [
            'id', 'approval_type', 'approval_type_display', 'status', 'status_display',
            'expense_id', 'supplier_payment_id', 'consultant_payment_id', 'lpo_id',
            'requested_by', 'requested_by_email', 'requested_at',
            'approved_by', 'approved_by_email', 'approved_at',
            'reason', 'notes', 'amount',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'requested_at', 'approved_at', 'created_at', 'updated_at']


class ApprovalListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for list views
    """
    requested_by_email = serializers.EmailField(source='requested_by.email', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    approval_type_display = serializers.CharField(source='get_approval_type_display', read_only=True)
    
    class Meta:
        model = Approval
        fields = [
            'id', 'approval_type', 'approval_type_display', 'status', 'status_display',
            'amount', 'requested_by_email', 'requested_at'
        ]


class ProjectActivitySerializer(serializers.ModelSerializer):
    """
    Serializer for ProjectActivity model
    """
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    performed_by_email = serializers.EmailField(source='performed_by.email', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = ProjectActivity
        fields = [
            'id', 'project_id', 'activity_type', 'activity_type_display',
            'related_object_type', 'related_object_id',
            'description', 'amount',
            'performed_by', 'performed_by_name', 'performed_by_email',
            'metadata', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class ProjectActivityListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for activity timeline
    """
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    activity_type_display = serializers.CharField(source='get_activity_type_display', read_only=True)
    
    class Meta:
        model = ProjectActivity
        fields = [
            'id', 'activity_type', 'activity_type_display',
            'description', 'amount', 'performed_by_name', 'created_at'
        ]
