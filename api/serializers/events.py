"""
Event Logging API Serializers

This module provides REST API serializers for system events.
"""

from rest_framework import serializers
from apps.events.models import SystemEvent


class SystemEventSerializer(serializers.ModelSerializer):
    """
    Serializer for SystemEvent model.
    
    Includes all event details with related object information.
    """
    event_type_display = serializers.CharField(
        source='get_event_type_display',
        read_only=True
    )
    category = serializers.CharField(read_only=True)
    user_display = serializers.SerializerMethodField()
    organization_display = serializers.SerializerMethodField()
    project_display = serializers.SerializerMethodField()
    entity_display = serializers.CharField(
        source='entity_display',
        read_only=True
    )
    time_since = serializers.CharField(read_only=True)
    
    class Meta:
        model = SystemEvent
        fields = [
            'id',
            'event_type',
            'event_type_display',
            'category',
            'user',
            'user_display',
            'organization',
            'organization_display',
            'project',
            'project_display',
            'entity_type',
            'entity_id',
            'entity_display',
            'timestamp',
            'time_since',
            'metadata',
            'ip_address',
            'user_agent',
            'request_path',
            'request_method',
            'response_status',
            'duration_ms',
        ]
        read_only_fields = fields  # All fields are read-only (audit log)
    
    def get_user_display(self, obj):
        """Get user display name"""
        if obj.user:
            return {
                'id': obj.user.id,
                'email': obj.user.email,
                'full_name': obj.user.get_full_name(),
            }
        return None
    
    def get_organization_display(self, obj):
        """Get organization display"""
        if obj.organization:
            return {
                'id': obj.organization.id,
                'name': obj.organization.name,
            }
        return None
    
    def get_project_display(self, obj):
        """Get project display"""
        if obj.project:
            return {
                'id': obj.project.id,
                'name': obj.project.name,
                'code': obj.project.code,
            }
        return None


class SystemEventListSerializer(serializers.ModelSerializer):
    """
    Lightweight serializer for event lists.
    
    Excludes heavy fields like user_agent and metadata for better performance.
    """
    event_type_display = serializers.CharField(
        source='get_event_type_display',
        read_only=True
    )
    category = serializers.CharField(read_only=True)
    user_email = serializers.EmailField(
        source='user.email',
        read_only=True
    )
    project_name = serializers.CharField(
        source='project.name',
        read_only=True
    )
    time_since = serializers.CharField(read_only=True)
    
    class Meta:
        model = SystemEvent
        fields = [
            'id',
            'event_type',
            'event_type_display',
            'category',
            'user_email',
            'project_name',
            'timestamp',
            'time_since',
            'response_status',
            'duration_ms',
        ]
        read_only_fields = fields


class EventCategorySerializer(serializers.Serializer):
    """Serializer for event category statistics"""
    category = serializers.CharField()
    count = serializers.IntegerField()
    percentage = serializers.FloatField()


class EventTypeSerializer(serializers.Serializer):
    """Serializer for event type statistics"""
    event_type = serializers.CharField()
    event_type_display = serializers.CharField()
    count = serializers.IntegerField()


class UserActivityStatsSerializer(serializers.Serializer):
    """Serializer for user activity statistics"""
    total_events = serializers.IntegerField()
    events_by_type = EventTypeSerializer(many=True)
    events_by_category = serializers.DictField()
    period_days = serializers.IntegerField()


class ProjectActivityStatsSerializer(serializers.Serializer):
    """Serializer for project activity statistics"""
    total_events = serializers.IntegerField()
    events_by_type = EventTypeSerializer(many=True)
    top_users = serializers.ListField()
    period_days = serializers.IntegerField()


class APIPerformanceStatsSerializer(serializers.Serializer):
    """Serializer for API performance statistics"""
    total_requests = serializers.IntegerField()
    average_duration_ms = serializers.FloatField()
    slow_requests = serializers.IntegerField()
    error_requests = serializers.IntegerField()
    error_rate_percent = serializers.FloatField()
    period_days = serializers.IntegerField()
