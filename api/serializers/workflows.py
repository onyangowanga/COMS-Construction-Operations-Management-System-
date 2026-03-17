"""
Workflow Serializers
Handles serialization for Approval and ProjectActivity models
"""
from rest_framework import serializers
from apps.workflows.models import Approval, ProjectActivity, WorkflowHistory, WorkflowInstance


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


class WorkflowTransitionRequestSerializer(serializers.Serializer):
    action = serializers.CharField(max_length=50)
    comment = serializers.CharField(required=False, allow_blank=True, default='')
    payload = serializers.JSONField(required=False, default=dict)


class WorkflowHistorySerializer(serializers.ModelSerializer):
    performed_by_name = serializers.CharField(source='performed_by.get_full_name', read_only=True)
    from_state = serializers.CharField(source='from_state.name', read_only=True)
    to_state = serializers.CharField(source='to_state.name', read_only=True)

    class Meta:
        model = WorkflowHistory
        fields = [
            'id',
            'from_state',
            'to_state',
            'action',
            'performed_by',
            'performed_by_name',
            'timestamp',
            'comment',
        ]


class WorkflowInstanceSerializer(serializers.ModelSerializer):
    current_state = serializers.CharField(source='current_state.name', read_only=True)
    available_actions = serializers.SerializerMethodField()
    history = serializers.SerializerMethodField()

    class Meta:
        model = WorkflowInstance
        fields = [
            'id',
            'module',
            'entity_id',
            'current_state',
            'available_actions',
            'history',
            'last_transition_by',
            'last_transition_at',
            'created_at',
            'updated_at',
        ]

    def get_available_actions(self, obj):
        transitions = obj.workflow.transitions.filter(from_state=obj.current_state).select_related('to_state')
        return [
            {
                'action': transition.action,
                'to_state': transition.to_state.name,
                'allowed_roles': transition.allowed_roles or [],
            }
            for transition in transitions
        ]

    def get_history(self, obj):
        items = obj.transition_history.select_related('from_state', 'to_state', 'performed_by').all()[:100]
        return WorkflowHistorySerializer(items, many=True).data
