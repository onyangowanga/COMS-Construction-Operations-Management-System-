"""
Notification Selectors

Data retrieval layer for notification queries.
All selectors use query optimization (select_related, prefetch_related).
"""

from django.db.models import Q, Count, Prefetch, QuerySet
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from .models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationBatch,
    NotificationType,
    NotificationPriority
)

User = get_user_model()


class NotificationSelector:
    """
    Notification data retrieval
    
    Provides optimized queries for:
    - User notifications
    - Unread counts
    - Filtered lists
    - Priority sorting
    """
    
    @staticmethod
    def get_user_notifications(
        user,
        is_read=None,
        notification_type=None,
        priority=None,
        days=None
    ) -> QuerySet:
        """
        Get notifications for a user with optional filters
        
        Args:
            user: User instance
            is_read: Filter by read status (True/False/None for all)
            notification_type: Filter by notification type
            priority: Filter by priority level
            days: Filter by age in days (e.g., 30 for last 30 days)
            
        Returns:
            QuerySet of Notification objects
        """
        queryset = Notification.objects.select_related(
            'user',
            'entity_type'
        ).filter(
            user=user
        )
        
        # Apply filters
        if is_read is not None:
            queryset = queryset.filter(is_read=is_read)
        
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        if priority:
            queryset = queryset.filter(priority=priority)
        
        if days:
            cutoff_date = timezone.now() - timedelta(days=days)
            queryset = queryset.filter(created_at__gte=cutoff_date)
        
        # Exclude expired notifications
        queryset = queryset.exclude(
            expires_at__lt=timezone.now()
        )
        
        return queryset.order_by('-created_at')
    
    @staticmethod
    def get_unread_notifications(user) -> QuerySet:
        """
        Get unread notifications for a user
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of unread Notification objects
        """
        return NotificationSelector.get_user_notifications(
            user=user,
            is_read=False
        )
    
    @staticmethod
    def get_unread_count(user) -> int:
        """
        Get count of unread notifications for a user
        
        Args:
            user: User instance
            
        Returns:
            Integer count of unread notifications
        """
        return NotificationSelector.get_unread_notifications(user).count()
    
    @staticmethod
    def get_unread_count_by_type(user) -> dict:
        """
        Get count of unread notifications grouped by type
        
        Args:
            user: User instance
            
        Returns:
            Dictionary mapping notification types to counts
        """
        counts = Notification.objects.filter(
            user=user,
            is_read=False
        ).exclude(
            expires_at__lt=timezone.now()
        ).values('notification_type').annotate(
            count=Count('id')
        )
        
        return {
            item['notification_type']: item['count']
            for item in counts
        }
    
    @staticmethod
    def get_recent_notifications(user, limit=10) -> QuerySet:
        """
        Get most recent notifications for a user
        
        Args:
            user: User instance
            limit: Maximum number of notifications to return
            
        Returns:
            QuerySet of recent Notification objects
        """
        return NotificationSelector.get_user_notifications(
            user=user
        )[:limit]
    
    @staticmethod
    def get_urgent_notifications(user) -> QuerySet:
        """
        Get urgent notifications for a user
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of urgent Notification objects
        """
        return NotificationSelector.get_user_notifications(
            user=user,
            priority=NotificationPriority.URGENT,
            is_read=False
        )
    
    @staticmethod
    def get_notifications_for_entity(entity_type, entity_id) -> QuerySet:
        """
        Get all notifications related to a specific entity
        
        Args:
            entity_type: ContentType instance
            entity_id: ID of the entity
            
        Returns:
            QuerySet of Notification objects
        """
        return Notification.objects.select_related(
            'user'
        ).filter(
            entity_type=entity_type,
            entity_id=str(entity_id)
        ).order_by('-created_at')
    
    @staticmethod
    def get_notification_by_id(notification_id, user=None):
        """
        Get a specific notification by ID
        
        Args:
            notification_id: UUID of notification
            user: Optional user to verify ownership
            
        Returns:
            Notification instance or None
        """
        try:
            queryset = Notification.objects.select_related(
                'user',
                'entity_type'
            )
            
            if user:
                queryset = queryset.filter(user=user)
            
            return queryset.get(id=notification_id)
        except Notification.DoesNotExist:
            return None
    
    @staticmethod
    def search_notifications(user, query) -> QuerySet:
        """
        Search notifications by title or message content
        
        Args:
            user: User instance
            query: Search query string
            
        Returns:
            QuerySet of matching Notification objects
        """
        return Notification.objects.select_related(
            'user',
            'entity_type'
        ).filter(
            user=user
        ).filter(
            Q(title__icontains=query) |
            Q(message__icontains=query)
        ).exclude(
            expires_at__lt=timezone.now()
        ).order_by('-created_at')


class NotificationPreferenceSelector:
    """
    Notification preference data retrieval
    
    Handles user preference queries and creation
    """
    
    @staticmethod
    def get_user_preferences(user):
        """
        Get notification preferences for a user
        (creates default preferences if none exist)
        
        Args:
            user: User instance
            
        Returns:
            NotificationPreference instance
        """
        preferences, created = NotificationPreference.objects.get_or_create(
            user=user
        )
        return preferences
    
    @staticmethod
    def is_user_opted_in(user, notification_type, channel='in_app'):
        """
        Check if user has opted in to receive a specific type of notification
        
        Args:
            user: User instance
            notification_type: NotificationType value
            channel: 'email', 'in_app', or 'sms'
            
        Returns:
            Boolean indicating if user wants this notification
        """
        preferences = NotificationPreferenceSelector.get_user_preferences(user)
        
        # Check channel is enabled
        channel_enabled = {
            'email': preferences.email_enabled,
            'in_app': preferences.in_app_enabled,
            'sms': preferences.sms_enabled,
        }.get(channel, True)
        
        if not channel_enabled:
            return False
        
        # Check if in quiet hours (only for email/SMS)
        if channel in ['email', 'sms'] and preferences.is_in_quiet_hours():
            return False
        
        # Check type-specific preference
        return preferences.is_type_enabled(notification_type)
    
    @staticmethod
    def get_users_with_preferences(**filters):
        """
        Get users with specific preference settings
        
        Args:
            **filters: Preference field filters (e.g., email_enabled=True)
            
        Returns:
            QuerySet of User objects
        """
        return User.objects.select_related(
            'notification_preferences'
        ).filter(
            notification_preferences__isnull=False,
            **{f'notification_preferences__{k}': v for k, v in filters.items()}
        )


class NotificationTemplateSelector:
    """
    Notification template data retrieval
    
    Handles template queries and lookups
    """
    
    @staticmethod
    def get_template_by_code(code):
        """
        Get template by code
        
        Args:
            code: Template code (e.g., 'variation_approved')
            
        Returns:
            NotificationTemplate instance or None
        """
        try:
            return NotificationTemplate.objects.get(
                code=code,
                is_active=True
            )
        except NotificationTemplate.DoesNotExist:
            return None
    
    @staticmethod
    def get_active_templates() -> QuerySet:
        """
        Get all active templates
        
        Returns:
            QuerySet of active NotificationTemplate objects
        """
        return NotificationTemplate.objects.filter(
            is_active=True
        ).order_by('name')
    
    @staticmethod
    def get_templates_by_type(notification_type) -> QuerySet:
        """
        Get templates for a specific notification type
        
        Args:
            notification_type: NotificationType value
            
        Returns:
            QuerySet of NotificationTemplate objects
        """
        return NotificationTemplate.objects.filter(
            notification_type=notification_type,
            is_active=True
        ).order_by('name')
    
    @staticmethod
    def search_templates(query) -> QuerySet:
        """
        Search templates by name, code, or description
        
        Args:
            query: Search query string
            
        Returns:
            QuerySet of matching NotificationTemplate objects
        """
        return NotificationTemplate.objects.filter(
            Q(name__icontains=query) |
            Q(code__icontains=query) |
            Q(description__icontains=query),
            is_active=True
        ).order_by('name')


class NotificationBatchSelector:
    """
    Notification batch data retrieval
    
    Handles batch tracking queries
    """
    
    @staticmethod
    def get_batch_by_id(batch_id):
        """
        Get batch by ID
        
        Args:
            batch_id: UUID of batch
            
        Returns:
            NotificationBatch instance or None
        """
        try:
            return NotificationBatch.objects.select_related(
                'template',
                'created_by'
            ).get(id=batch_id)
        except NotificationBatch.DoesNotExist:
            return None
    
    @staticmethod
    def get_user_batches(user) -> QuerySet:
        """
        Get batches created by a user
        
        Args:
            user: User instance
            
        Returns:
            QuerySet of NotificationBatch objects
        """
        return NotificationBatch.objects.select_related(
            'template',
            'created_by'
        ).filter(
            created_by=user
        ).order_by('-created_at')
    
    @staticmethod
    def get_pending_batches() -> QuerySet:
        """
        Get batches pending processing
        
        Returns:
            QuerySet of pending NotificationBatch objects
        """
        return NotificationBatch.objects.select_related(
            'template',
            'created_by'
        ).filter(
            status='PENDING'
        ).order_by('created_at')
    
    @staticmethod
    def get_batch_statistics(days=30) -> dict:
        """
        Get batch statistics for a time period
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with batch statistics
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        batches = NotificationBatch.objects.filter(
            created_at__gte=cutoff_date
        ).aggregate(
            total_batches=Count('id'),
            total_recipients=Count('total_recipients'),
            total_sent=Count('sent_count'),
            total_failed=Count('failed_count')
        )
        
        return batches


class NotificationAnalyticsSelector:
    """
    Notification analytics and statistics
    
    Provides aggregated data for reporting
    """
    
    @staticmethod
    def get_user_statistics(user, days=30) -> dict:
        """
        Get notification statistics for a user
        
        Args:
            user: User instance
            days: Number of days to analyze
            
        Returns:
            Dictionary with notification statistics
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        notifications = Notification.objects.filter(
            user=user,
            created_at__gte=cutoff_date
        )
        
        stats = notifications.aggregate(
            total=Count('id'),
            unread=Count('id', filter=Q(is_read=False)),
            urgent=Count('id', filter=Q(priority=NotificationPriority.URGENT)),
        )
        
        # Add type breakdown
        type_counts = notifications.values('notification_type').annotate(
            count=Count('id')
        )
        
        stats['by_type'] = {
            item['notification_type']: item['count']
            for item in type_counts
        }
        
        # Add read rate
        if stats['total'] > 0:
            stats['read_rate'] = ((stats['total'] - stats['unread']) / stats['total']) * 100
        else:
            stats['read_rate'] = 0
        
        return stats
    
    @staticmethod
    def get_system_statistics(days=30) -> dict:
        """
        Get system-wide notification statistics
        
        Args:
            days: Number of days to analyze
            
        Returns:
            Dictionary with system statistics
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        notifications = Notification.objects.filter(
            created_at__gte=cutoff_date
        )
        
        stats = notifications.aggregate(
            total=Count('id'),
            unread=Count('id', filter=Q(is_read=False)),
            email_sent=Count('id', filter=Q(email_sent=True)),
            sms_sent=Count('id', filter=Q(sms_sent=True)),
        )
        
        # Add type breakdown
        type_counts = notifications.values('notification_type').annotate(
            count=Count('id')
        )
        
        stats['by_type'] = {
            item['notification_type']: item['count']
            for item in type_counts
        }
        
        # Add priority breakdown
        priority_counts = notifications.values('priority').annotate(
            count=Count('id')
        )
        
        stats['by_priority'] = {
            item['priority']: item['count']
            for item in priority_counts
        }
        
        # Add delivery rates
        if stats['total'] > 0:
            stats['email_delivery_rate'] = (stats['email_sent'] / stats['total']) * 100
            stats['sms_delivery_rate'] = (stats['sms_sent'] / stats['total']) * 100
        else:
            stats['email_delivery_rate'] = 0
            stats['sms_delivery_rate'] = 0
        
        return stats
