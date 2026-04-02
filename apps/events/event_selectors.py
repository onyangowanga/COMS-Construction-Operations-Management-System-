"""
Event Logging Selectors

This module provides optimized query methods for retrieving system events.
All queries are optimized with select_related and prefetch_related where appropriate.
"""

from django.db.models import Q, Count, Avg
from django.utils import timezone
from datetime import timedelta
from typing import Optional, List
from django.contrib.contenttypes.models import ContentType

from apps.events.models import SystemEvent


class EventSelector:
    """
    Selector for querying SystemEvent records.
    
    Provides methods for:
    - Retrieving events with various filters
    - Entity-specific event history
    - Project-level event aggregation
    - User activity tracking
    - Event analytics and statistics
    """
    
    @staticmethod
    def get_all_events(
        user=None,
        organization=None,
        project=None,
        event_type=None,
        category=None,
        start_date=None,
        end_date=None,
        limit=None
    ):
        """
        Get all events with optional filters.
        
        Args:
            user: Filter by user who triggered the event
            organization: Filter by organization
            project: Filter by project
            event_type: Filter by specific event type
            category: Filter by event category
            start_date: Filter events after this date
            end_date: Filter events before this date
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        queryset = SystemEvent.objects.select_related(
            'user',
            'organization',
            'project',
            'entity_type'
        ).all()
        
        if user:
            queryset = queryset.filter(user=user)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        if project:
            queryset = queryset.filter(project=project)
        
        if event_type:
            queryset = queryset.filter(event_type=event_type)
        
        if category:
            # Filter by category
            event_types = [
                event_type for event_type, cat in SystemEvent.EVENT_CATEGORIES.items()
                if cat == category
            ]
            queryset = queryset.filter(event_type__in=event_types)
        
        if start_date:
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if end_date:
            queryset = queryset.filter(timestamp__lte=end_date)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_entity_events(entity_type: str, entity_id: str, limit: Optional[int] = None):
        """
        Get all events related to a specific entity.
        
        Args:
            entity_type: ContentType model name (e.g., 'variation', 'document')
            entity_id: ID of the entity
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        try:
            content_type = ContentType.objects.get(model=entity_type.lower())
        except ContentType.DoesNotExist:
            return SystemEvent.objects.none()
        
        queryset = SystemEvent.objects.filter(
            entity_type=content_type,
            entity_id=str(entity_id)
        ).select_related('user', 'organization', 'project').order_by('-timestamp')
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_project_events(project, event_types: Optional[List[str]] = None, days: Optional[int] = None):
        """
        Get all events for a specific project.
        
        Args:
            project: Project instance
            event_types: Optional list of event types to filter
            days: Number of days to look back (default: all time)
            
        Returns:
            QuerySet of SystemEvent objects
        """
        queryset = SystemEvent.objects.filter(
            project=project
        ).select_related('user', 'organization').order_by('-timestamp')
        
        if event_types:
            queryset = queryset.filter(event_type__in=event_types)
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        return queryset
    
    @staticmethod
    def get_user_activity(user, days: Optional[int] = None, limit: Optional[int] = None):
        """
        Get activity log for a specific user.
        
        Args:
            user: User instance
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        queryset = SystemEvent.objects.filter(
            user=user
        ).select_related('organization', 'project', 'entity_type').order_by('-timestamp')
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        if limit:
            queryset = queryset[:limit]
        
        return queryset
    
    @staticmethod
    def get_recent_events(hours: int = 24, limit: int = 50):
        """
        Get recent events within the specified time window.
        
        Args:
            hours: Number of hours to look back
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        start_time = timezone.now() - timedelta(hours=hours)
        
        return SystemEvent.objects.filter(
            timestamp__gte=start_time
        ).select_related('user', 'organization', 'project').order_by('-timestamp')[:limit]
    
    @staticmethod
    def search_events(query: str):
        """
        Search events by various fields.
        
        Args:
            query: Search string
            
        Returns:
            QuerySet of SystemEvent objects matching the query
        """
        return SystemEvent.objects.filter(
            Q(event_type__icontains=query) |
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query) |
            Q(project__name__icontains=query) |
            Q(organization__name__icontains=query) |
            Q(request_path__icontains=query) |
            Q(metadata__icontains=query)
        ).select_related('user', 'organization', 'project').distinct()
    
    @staticmethod
    def get_login_events(days: Optional[int] = None):
        """
        Get all login events.
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet of login events
        """
        queryset = SystemEvent.objects.filter(
            event_type=SystemEvent.USER_LOGIN
        ).select_related('user', 'organization').order_by('-timestamp')
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        return queryset
    
    @staticmethod
    def get_failed_events(days: Optional[int] = None):
        """
        Get events that resulted in errors (status code >= 400).
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet of failed events
        """
        queryset = SystemEvent.objects.filter(
            response_status__gte=400
        ).select_related('user', 'organization', 'project').order_by('-timestamp')
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        return queryset


class EventAnalyticsSelector:
    """
    Selector for event analytics and statistics.
    
    Provides aggregated data and metrics about system events.
    """
    
    @staticmethod
    def get_event_counts_by_type(days: Optional[int] = None):
        """
        Get count of events grouped by type.
        
        Args:
            days: Number of days to look back
            
        Returns:
            QuerySet with event counts by type
        """
        queryset = SystemEvent.objects.all()
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        return queryset.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
    
    @staticmethod
    def get_event_counts_by_category(days: Optional[int] = None):
        """
        Get count of events grouped by category.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with category counts
        """
        queryset = SystemEvent.objects.all()
        
        if days:
            start_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(timestamp__gte=start_date)
        
        # Get all events and group by category
        events = queryset.values('event_type').annotate(count=Count('id'))
        
        category_counts = {}
        for event in events:
            category = SystemEvent.EVENT_CATEGORIES.get(event['event_type'], 'other')
            category_counts[category] = category_counts.get(category, 0) + event['count']
        
        return category_counts
    
    @staticmethod
    def get_user_activity_stats(user, days: int = 30):
        """
        Get activity statistics for a user.
        
        Args:
            user: User instance
            days: Number of days to look back
            
        Returns:
            Dict with user activity statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        events = SystemEvent.objects.filter(
            user=user,
            timestamp__gte=start_date
        )
        
        total_events = events.count()
        events_by_type = events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get category breakdown
        category_counts = {}
        for event in events_by_type:
            category = SystemEvent.EVENT_CATEGORIES.get(event['event_type'], 'other')
            category_counts[category] = category_counts.get(category, 0) + event['count']
        
        return {
            'total_events': total_events,
            'events_by_type': list(events_by_type),
            'events_by_category': category_counts,
            'period_days': days
        }
    
    @staticmethod
    def get_project_activity_stats(project, days: int = 30):
        """
        Get activity statistics for a project.
        
        Args:
            project: Project instance
            days: Number of days to look back
            
        Returns:
            Dict with project activity statistics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        events = SystemEvent.objects.filter(
            project=project,
            timestamp__gte=start_date
        )
        
        total_events = events.count()
        events_by_type = events.values('event_type').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Get top users
        top_users = events.exclude(user__isnull=True).values(
            'user__first_name',
            'user__last_name',
            'user__email'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        return {
            'total_events': total_events,
            'events_by_type': list(events_by_type),
            'top_users': list(top_users),
            'period_days': days
        }
    
    @staticmethod
    def get_api_performance_stats(days: int = 7):
        """
        Get API performance statistics.
        
        Args:
            days: Number of days to look back
            
        Returns:
            Dict with API performance metrics
        """
        start_date = timezone.now() - timedelta(days=days)
        
        api_events = SystemEvent.objects.filter(
            event_type=SystemEvent.API_REQUEST,
            timestamp__gte=start_date,
            duration_ms__isnull=False
        )
        
        stats = api_events.aggregate(
            total_requests=Count('id'),
            avg_duration=Avg('duration_ms')
        )
        
        # Get slow requests (> 1000ms)
        slow_requests = api_events.filter(duration_ms__gt=1000).count()
        
        # Get error rate
        total_requests = api_events.count()
        error_requests = api_events.filter(response_status__gte=400).count()
        error_rate = (error_requests / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'total_requests': stats['total_requests'] or 0,
            'average_duration_ms': round(stats['avg_duration'] or 0, 2),
            'slow_requests': slow_requests,
            'error_requests': error_requests,
            'error_rate_percent': round(error_rate, 2),
            'period_days': days
        }
