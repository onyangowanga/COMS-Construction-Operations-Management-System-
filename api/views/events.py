"""
Event Logging API Views

This module provides REST API endpoints for system events.
"""

from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404
from django.contrib.contenttypes.models import ContentType

from apps.events.models import SystemEvent
from apps.events.selectors import EventSelector, EventAnalyticsSelector
from apps.projects.models import Project
from api.serializers.events import (
    SystemEventSerializer,
    SystemEventListSerializer,
    UserActivityStatsSerializer,
    ProjectActivityStatsSerializer,
    APIPerformanceStatsSerializer,
)


class EventPagination(PageNumberPagination):
    """Pagination for event lists"""
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200


class SystemEventViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing system events.
    
    This is a read-only viewset as events are created automatically
    or through services, not directly via API.
    
    Endpoints:
    - GET /api/events/ - List all events (with filters)
    - GET /api/events/{id}/ - Get event detail
    - GET /api/events/recent/ - Get recent events
    - GET /api/events/project/{project_id}/ - Get project events
    - GET /api/events/entity/{type}/{id}/ - Get entity events
    - GET /api/events/user_activity/ - Get current user's activity
    - GET /api/events/statistics/ - Get event statistics
    """
    
    permission_classes = [permissions.IsAuthenticated]
    pagination_class = EventPagination
    
    def get_queryset(self):
        """
        Get queryset with filters.
        
        Query parameters:
        - event_type: Filter by event type
        - category: Filter by category
        - user: Filter by user ID
        - project: Filter by project ID
        - start_date: Filter from date (YYYY-MM-DD)
        - end_date: Filter to date (YYYY-MM-DD)
        - days: Filter last N days
        """
        queryset = SystemEvent.objects.select_related(
            'user',
            'organization',
            'project',
            'entity_type'
        ).all()
        
        # Apply filters from query params
        event_type = self.request.query_params.get('event_type')
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        category = self.request.query_params.get('category')
        if category:
            event_types = [
                et for et, cat in SystemEvent.EVENT_CATEGORIES.items()
                if cat == category
            ]
            queryset = queryset.filter(event_type__in=event_types)
        
        user_id = self.request.query_params.get('user')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        project_id = self.request.query_params.get('project')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Date filters
        start_date = self.request.query_params.get('start_date')
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        end_date = self.request.query_params.get('end_date')
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        days = self.request.query_params.get('days')
        if days:
            start = timezone.now() - timedelta(days=int(days))
            queryset = queryset.filter(timestamp__gte=start)
        
        # Filter by user's organization (security)
        if not self.request.user.is_superuser:
            queryset = queryset.filter(
                organization=self.request.user.organization
            )
        
        return queryset.order_by('-timestamp')
    
    def get_serializer_class(self):
        """Use lightweight serializer for lists"""
        if self.action == 'list':
            return SystemEventListSerializer
        return SystemEventSerializer
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """
        Get recent events.
        
        Query params:
        - hours: Number of hours to look back (default: 24)
        - limit: Number of results (default: 50)
        """
        hours = int(request.query_params.get('hours', 24))
        limit = int(request.query_params.get('limit', 50))
        
        events = EventSelector.get_recent_events(hours=hours, limit=limit)
        
        # Apply organization filter
        if not request.user.is_superuser:
            events = events.filter(organization=request.user.organization)
        
        serializer = SystemEventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='project/(?P<project_id>[^/.]+)')
    def project_events(self, request, project_id=None):
        """
        Get all events for a specific project.
        
        Query params:
        - event_types: Comma-separated list of event types
        - days: Number of days to look back
        """
        project = get_object_or_404(Project, pk=project_id)
        
        # Check permission
        if not request.user.is_superuser:
            if project.organization != request.user.organization:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        # Get event types filter
        event_types_param = request.query_params.get('event_types')
        event_types = event_types_param.split(',') if event_types_param else None
        
        days = request.query_params.get('days')
        days = int(days) if days else None
        
        events = EventSelector.get_project_events(
            project=project,
            event_types=event_types,
            days=days
        )
        
        # Paginate
        page = self.paginate_queryset(events)
        if page is not None:
            serializer = SystemEventListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = SystemEventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='entity/(?P<entity_type>[^/.]+)/(?P<entity_id>[^/.]+)')
    def entity_events(self, request, entity_type=None, entity_id=None):
        """
        Get all events for a specific entity.
        
        Args:
            entity_type: Model name (e.g., 'variation', 'document')
            entity_id: Entity ID
            
        Query params:
            - limit: Maximum number of results
        """
        limit = request.query_params.get('limit')
        limit = int(limit) if limit else None
        
        events = EventSelector.get_entity_events(
            entity_type=entity_type,
            entity_id=entity_id,
            limit=limit
        )
        
        # Apply organization filter
        if not request.user.is_superuser:
            events = events.filter(organization=request.user.organization)
        
        serializer = SystemEventSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_activity(self, request):
        """
        Get activity log for current user.
        
        Query params:
        - days: Number of days to look back
        - limit: Maximum number of results
        """
        days = request.query_params.get('days')
        days = int(days) if days else None
        
        limit = request.query_params.get('limit')
        limit = int(limit) if limit else 100
        
        events = EventSelector.get_user_activity(
            user=request.user,
            days=days,
            limit=limit
        )
        
        serializer = SystemEventListSerializer(events, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def user_stats(self, request):
        """
        Get activity statistics for current user.
        
        Query params:
        - days: Number of days to look back (default: 30)
        """
        days = int(request.query_params.get('days', 30))
        
        stats = EventAnalyticsSelector.get_user_activity_stats(
            user=request.user,
            days=days
        )
        
        serializer = UserActivityStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'], url_path='project/(?P<project_id>[^/.]+)/stats')
    def project_stats(self, request, project_id=None):
        """
        Get activity statistics for a project.
        
        Query params:
        - days: Number of days to look back (default: 30)
        """
        project = get_object_or_404(Project, pk=project_id)
        
        # Check permission
        if not request.user.is_superuser:
            if project.organization != request.user.organization:
                return Response(
                    {'error': 'Permission denied'},
                    status=status.HTTP_403_FORBIDDEN
                )
        
        days = int(request.query_params.get('days', 30))
        
        stats = EventAnalyticsSelector.get_project_activity_stats(
            project=project,
            days=days
        )
        
        serializer = ProjectActivityStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def statistics(self, request):
        """
        Get system-wide event statistics.
        
        Query params:
        - days: Number of days to look back (default: 30)
        """
        days = int(request.query_params.get('days', 30))
        
        event_counts = EventAnalyticsSelector.get_event_counts_by_type(days=days)
        category_counts = EventAnalyticsSelector.get_event_counts_by_category(days=days)
        
        return Response({
            'events_by_type': list(event_counts),
            'events_by_category': category_counts,
            'period_days': days
        })
    
    @action(detail=False, methods=['get'])
    def api_performance(self, request):
        """
        Get API performance statistics.
        
        Query params:
        - days: Number of days to look back (default: 7)
        """
        days = int(request.query_params.get('days', 7))
        
        stats = EventAnalyticsSelector.get_api_performance_stats(days=days)
        
        serializer = APIPerformanceStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def event_types(self, request):
        """
        Get list of all available event types and categories.
        """
        event_types = [
            {
                'value': value,
                'label': label,
                'category': SystemEvent.EVENT_CATEGORIES.get(value, 'other')
            }
            for value, label in SystemEvent.EVENT_TYPE_CHOICES
        ]
        
        categories = list(set(SystemEvent.EVENT_CATEGORIES.values()))
        
        return Response({
            'event_types': event_types,
            'categories': sorted(categories)
        })
