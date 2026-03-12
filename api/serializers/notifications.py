"""
Notification API Serializers

Serializers for:
- Notifications
- Notification preferences
- Notification templates
- Notification batches
"""

from rest_framework import serializers
from django.contrib.auth import get_user_model

from apps.notifications.models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationBatch,
    NotificationType,
    NotificationPriority
)

User = get_user_model()


class NotificationSerializer(serializers.ModelSerializer):
    """Serializer for Notification model"""
    
    user_display = serializers.SerializerMethodField()
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    age_in_days = serializers.IntegerField(read_only=True)
    is_urgent = serializers.BooleanField(read_only=True)
    is_expired = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'user',
            'user_display',
            'title',
            'message',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'entity_type',
            'entity_id',
            'is_read',
            'read_at',
            'email_sent',
            'email_sent_at',
            'sms_sent',
            'sms_sent_at',
            'metadata',
            'action_url',
            'action_label',
            'created_at',
            'updated_at',
            'expires_at',
            'age_in_days',
            'is_urgent',
            'is_expired'
        ]
        read_only_fields = [
            'id',
            'is_read',
            'read_at',
            'email_sent',
            'email_sent_at',
            'sms_sent',
            'sms_sent_at',
            'created_at',
            'updated_at'
        ]
    
    def get_user_display(self, obj):
        """Get user display name"""
        return obj.user.get_full_name() or obj.user.username


class NotificationListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for notification lists"""
    
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = Notification
        fields = [
            'id',
            'title',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'is_read',
            'created_at',
            'action_url',
            'action_label'
        ]


class NotificationCreateSerializer(serializers.Serializer):
    """Serializer for creating notifications"""
    
    user_id = serializers.IntegerField(required=False, help_text='User ID (defaults to current user)')
    user_ids = serializers.ListField(
        child=serializers.IntegerField(),
        required=False,
        help_text='List of user IDs for bulk creation'
    )
    
    title = serializers.CharField(max_length=200)
    message = serializers.CharField()
    notification_type = serializers.ChoiceField(
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    priority = serializers.ChoiceField(
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    
    metadata = serializers.JSONField(required=False, default=dict)
    action_url = serializers.CharField(max_length=500, required=False, allow_null=True)
    action_label = serializers.CharField(max_length=100, required=False, allow_null=True)
    expires_in_days = serializers.IntegerField(required=False, allow_null=True)
    
    send_email = serializers.BooleanField(default=False)
    send_sms = serializers.BooleanField(default=False)


class NotificationMarkReadSerializer(serializers.Serializer):
    """Serializer for marking notifications as read"""
    
    notification_ids = serializers.ListField(
        child=serializers.UUIDField(),
        required=False,
        help_text='List of notification IDs to mark as read'
    )


class NotificationPreferenceSerializer(serializers.ModelSerializer):
    """Serializer for NotificationPreference model"""
    
    user_display = serializers.SerializerMethodField()
    
    class Meta:
        model = NotificationPreference
        fields = [
            'id',
            'user',
            'user_display',
            'email_enabled',
            'in_app_enabled',
            'sms_enabled',
            'system_notifications',
            'workflow_notifications',
            'financial_notifications',
            'document_notifications',
            'report_notifications',
            'deadline_notifications',
            'approval_notifications',
            'digest_enabled',
            'digest_time',
            'quiet_hours_enabled',
            'quiet_hours_start',
            'quiet_hours_end',
            'sms_phone_number',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
    
    def get_user_display(self, obj):
        """Get user display name"""
        return obj.user.get_full_name() or obj.user.username


class NotificationPreferenceUpdateSerializer(serializers.Serializer):
    """Serializer for updating notification preferences"""
    
    email_enabled = serializers.BooleanField(required=False)
    in_app_enabled = serializers.BooleanField(required=False)
    sms_enabled = serializers.BooleanField(required=False)
    
    system_notifications = serializers.BooleanField(required=False)
    workflow_notifications = serializers.BooleanField(required=False)
    financial_notifications = serializers.BooleanField(required=False)
    document_notifications = serializers.BooleanField(required=False)
    report_notifications = serializers.BooleanField(required=False)
    deadline_notifications = serializers.BooleanField(required=False)
    approval_notifications = serializers.BooleanField(required=False)
    
    digest_enabled = serializers.BooleanField(required=False)
    digest_time = serializers.TimeField(required=False, allow_null=True)
    
    quiet_hours_enabled = serializers.BooleanField(required=False)
    quiet_hours_start = serializers.TimeField(required=False, allow_null=True)
    quiet_hours_end = serializers.TimeField(required=False, allow_null=True)
    
    sms_phone_number = serializers.CharField(max_length=20, required=False, allow_null=True, allow_blank=True)


class NotificationTemplateSerializer(serializers.ModelSerializer):
    """Serializer for NotificationTemplate model"""
    
    type_display = serializers.CharField(source='get_notification_type_display', read_only=True)
    priority_display = serializers.CharField(source='get_priority_display', read_only=True)
    
    class Meta:
        model = NotificationTemplate
        fields = [
            'id',
            'code',
            'name',
            'description',
            'notification_type',
            'type_display',
            'priority',
            'priority_display',
            'title_template',
            'message_template',
            'email_subject_template',
            'email_body_template',
            'sms_template',
            'action_url_template',
            'action_label',
            'is_active',
            'variables',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class NotificationTemplateCreateSerializer(serializers.Serializer):
    """Serializer for creating notification templates"""
    
    code = serializers.CharField(max_length=100)
    name = serializers.CharField(max_length=200)
    description = serializers.CharField(required=False, allow_blank=True)
    
    notification_type = serializers.ChoiceField(
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM
    )
    priority = serializers.ChoiceField(
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL
    )
    
    title_template = serializers.CharField(max_length=200)
    message_template = serializers.CharField()
    
    email_subject_template = serializers.CharField(max_length=200, required=False, allow_null=True, allow_blank=True)
    email_body_template = serializers.CharField(required=False, allow_null=True, allow_blank=True)
    sms_template = serializers.CharField(max_length=160, required=False, allow_null=True, allow_blank=True)
    
    action_url_template = serializers.CharField(max_length=500, required=False, allow_null=True, allow_blank=True)
    action_label = serializers.CharField(max_length=100, required=False, allow_null=True, allow_blank=True)
    
    is_active = serializers.BooleanField(default=True)
    variables = serializers.ListField(child=serializers.CharField(), required=False, default=list)


class NotificationBatchSerializer(serializers.ModelSerializer):
    """Serializer for NotificationBatch model"""
    
    template_name = serializers.SerializerMethodField()
    created_by_display = serializers.SerializerMethodField()
    success_rate = serializers.FloatField(read_only=True)
    is_complete = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = NotificationBatch
        fields = [
            'id',
            'name',
            'template',
            'template_name',
            'total_recipients',
            'sent_count',
            'failed_count',
            'status',
            'success_rate',
            'is_complete',
            'created_by',
            'created_by_display',
            'created_at',
            'completed_at'
        ]
        read_only_fields = [
            'id',
            'total_recipients',
            'sent_count',
            'failed_count',
            'status',
            'created_at',
            'completed_at'
        ]
    
    def get_template_name(self, obj):
        """Get template name"""
        return obj.template.name if obj.template else None
    
    def get_created_by_display(self, obj):
        """Get creator display name"""
        if obj.created_by:
            return obj.created_by.get_full_name() or obj.created_by.username
        return None


class NotificationBatchCreateSerializer(serializers.Serializer):
    """Serializer for creating notification batches"""
    
    name = serializers.CharField(max_length=200)
    template_code = serializers.CharField(max_length=100)
    user_ids = serializers.ListField(child=serializers.IntegerField())
    context = serializers.JSONField()
    
    send_email = serializers.BooleanField(default=False)
    send_sms = serializers.BooleanField(default=False)


class NotificationStatsSerializer(serializers.Serializer):
    """Serializer for notification statistics"""
    
    total = serializers.IntegerField()
    unread = serializers.IntegerField()
    urgent = serializers.IntegerField()
    read_rate = serializers.FloatField()
    by_type = serializers.DictField()
