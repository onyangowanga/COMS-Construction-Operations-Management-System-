"""
Notification API Views

REST API endpoints for:
- Notification management
- User preferences
- Templates
- Batches
- Statistics
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.pagination import PageNumberPagination
from django.contrib.auth import get_user_model

from apps.notifications.models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationBatch
)
from apps.notifications.services import (
    NotificationService,
    NotificationPreferenceService,
    NotificationTemplateService,
    NotificationDeliveryService
)
from apps.notifications.selectors import (
    NotificationSelector,
    NotificationPreferenceSelector,
    NotificationTemplateSelector,
    NotificationBatchSelector,
    NotificationAnalyticsSelector
)
from apps.notifications.tasks import (
    send_batch_notifications_task,
    send_email_task,
    send_sms_task
)
from api.serializers.notifications import (
    NotificationSerializer,
    NotificationListSerializer,
    NotificationCreateSerializer,
    NotificationMarkReadSerializer,
    NotificationPreferenceSerializer,
    NotificationPreferenceUpdateSerializer,
    NotificationTemplateSerializer,
    NotificationTemplateCreateSerializer,
    NotificationBatchSerializer,
    NotificationBatchCreateSerializer,
    NotificationStatsSerializer
)

User = get_user_model()


class NotificationPagination(PageNumberPagination):
    """Pagination for notifications"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class NotificationViewSet(viewsets.ModelViewSet):
    """
    API endpoints for notifications
    
    list: Get user's notifications
    retrieve: Get specific notification
    create: Create new notification
    destroy: Delete notification
    
    Additional actions:
    - unread: Get unread notifications
    - mark_read: Mark notification(s) as read
    - mark_all_read: Mark all notifications as read
    - stats: Get notification statistics
    """
    
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = NotificationPagination
    
    def get_queryset(self):
        """Get notifications for current user"""
        user = self.request.user
        
        # Apply filters
        queryset = NotificationSelector.get_user_notifications(user)
        
        # Filter by type if specified
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Filter by priority if specified
        priority = self.request.query_params.get('priority')
        if priority:
            queryset = queryset.filter(priority=priority)
        
        # Filter by read status if specified
        is_read = self.request.query_params.get('is_read')
        if is_read is not None:
            is_read_bool = is_read.lower() in ['true', '1', 'yes']
            queryset = queryset.filter(is_read=is_read_bool)
        
        # Filter by days if specified
        days = self.request.query_params.get('days')
        if days:
            try:
                days_int = int(days)
                queryset = NotificationSelector.get_user_notifications(
                    user,
                    days=days_int
                )
            except ValueError:
                pass
        
        # Search if query provided
        query = self.request.query_params.get('search')
        if query:
            queryset = NotificationSelector.search_notifications(user, query)
        
        return queryset
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'list':
            return NotificationListSerializer
        elif self.action == 'create':
            return NotificationCreateSerializer
        return NotificationSerializer
    
    def create(self, request):
        """Create notification(s)"""
        serializer = NotificationCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Check if bulk creation
        if 'user_ids' in data:
            users = User.objects.filter(id__in=data['user_ids'])
            
            notifications = NotificationService.create_bulk_notifications(
                users=list(users),
                title=data['title'],
                message=data['message'],
                notification_type=data.get('notification_type'),
                priority=data.get('priority'),
                metadata=data.get('metadata'),
                action_url=data.get('action_url'),
                action_label=data.get('action_label'),
                expires_in_days=data.get('expires_in_days'),
                send_email=data.get('send_email', False),
                send_sms=data.get('send_sms', False)
            )
            
            return Response(
                {
                    'message': f'Created {len(notifications)} notifications',
                    'count': len(notifications)
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # Single notification
            user_id = data.get('user_id')
            user = User.objects.get(id=user_id) if user_id else request.user
            
            notification = NotificationService.create_notification(
                user=user,
                title=data['title'],
                message=data['message'],
                notification_type=data.get('notification_type'),
                priority=data.get('priority'),
                metadata=data.get('metadata'),
                action_url=data.get('action_url'),
                action_label=data.get('action_label'),
                expires_in_days=data.get('expires_in_days'),
                send_email=data.get('send_email', False),
                send_sms=data.get('send_sms', False)
            )
            
            serializer = NotificationSerializer(notification)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    def destroy(self, request, pk=None):
        """Delete notification"""
        success = NotificationService.delete_notification(pk, user=request.user)
        
        if success:
            return Response(status=status.HTTP_204_NO_CONTENT)
        
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['get'])
    def unread(self, request):
        """Get unread notifications"""
        notifications = NotificationSelector.get_unread_notifications(request.user)
        
        page = self.paginate_queryset(notifications)
        if page is not None:
            serializer = NotificationListSerializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def recent(self, request):
        """Get recent notifications"""
        limit = int(request.query_params.get('limit', 10))
        notifications = NotificationSelector.get_recent_notifications(
            request.user,
            limit=limit
        )
        
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def urgent(self, request):
        """Get urgent unread notifications"""
        notifications = NotificationSelector.get_urgent_notifications(request.user)
        
        serializer = NotificationListSerializer(notifications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def mark_read(self, request, pk=None):
        """Mark notification as read"""
        success = NotificationService.mark_as_read(pk, user=request.user)
        
        if success:
            return Response({'message': 'Notification marked as read'})
        
        return Response(
            {'error': 'Notification not found'},
            status=status.HTTP_404_NOT_FOUND
        )
    
    @action(detail=False, methods=['post'])
    def mark_all_read(self, request):
        """Mark all notifications as read"""
        count = NotificationService.mark_all_as_read(request.user)
        
        return Response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    
    @action(detail=False, methods=['post'])
    def mark_multiple_read(self, request):
        """Mark multiple notifications as read"""
        serializer = NotificationMarkReadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        notification_ids = serializer.validated_data.get('notification_ids', [])
        
        count = 0
        for notification_id in notification_ids:
            if NotificationService.mark_as_read(notification_id, user=request.user):
                count += 1
        
        return Response({
            'message': f'Marked {count} notifications as read',
            'count': count
        })
    
    @action(detail=False, methods=['get'])
    def unread_count(self, request):
        """Get unread notification count"""
        count = NotificationSelector.get_unread_count(request.user)
        count_by_type = NotificationSelector.get_unread_count_by_type(request.user)
        
        return Response({
            'total': count,
            'by_type': count_by_type
        })
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Get notification statistics"""
        days = int(request.query_params.get('days', 30))
        
        stats = NotificationAnalyticsSelector.get_user_statistics(
            request.user,
            days=days
        )
        
        serializer = NotificationStatsSerializer(stats)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def resend_email(self, request, pk=None):
        """Resend email for notification"""
        notification = NotificationSelector.get_notification_by_id(pk, user=request.user)
        
        if not notification:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Queue email task
        send_email_task.delay(str(notification.id))
        
        return Response({'message': 'Email queued for sending'})
    
    @action(detail=True, methods=['post'])
    def resend_sms(self, request, pk=None):
        """Resend SMS for notification"""
        notification = NotificationSelector.get_notification_by_id(pk, user=request.user)
        
        if not notification:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Queue SMS task
        send_sms_task.delay(str(notification.id))
        
        return Response({'message': 'SMS queued for sending'})


class NotificationPreferenceViewSet(viewsets.ViewSet):
    """
    API endpoints for notification preferences
    
    retrieve: Get user's preferences
    update: Update preferences
    """
    
    permission_classes = [IsAuthenticated]
    
    def retrieve(self, request):
        """Get user's notification preferences"""
        preferences = NotificationPreferenceSelector.get_user_preferences(request.user)
        serializer = NotificationPreferenceSerializer(preferences)
        return Response(serializer.data)
    
    def update(self, request):
        """Update user's notification preferences"""
        serializer = NotificationPreferenceUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        preferences = NotificationPreferenceService.update_preferences(
            request.user,
            **serializer.validated_data
        )
        
        response_serializer = NotificationPreferenceSerializer(preferences)
        return Response(response_serializer.data)
    
    @action(detail=False, methods=['post'])
    def enable_channel(self, request):
        """Enable a notification channel"""
        channel = request.data.get('channel')
        
        if not channel or channel not in ['email', 'in_app', 'sms']:
            return Response(
                {'error': 'Invalid channel. Must be email, in_app, or sms'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        NotificationPreferenceService.enable_channel(request.user, channel)
        
        return Response({'message': f'{channel} notifications enabled'})
    
    @action(detail=False, methods=['post'])
    def disable_channel(self, request):
        """Disable a notification channel"""
        channel = request.data.get('channel')
        
        if not channel or channel not in ['email', 'in_app', 'sms']:
            return Response(
                {'error': 'Invalid channel. Must be email, in_app, or sms'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        NotificationPreferenceService.disable_channel(request.user, channel)
        
        return Response({'message': f'{channel} notifications disabled'})


class NotificationTemplateViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for notification templates (read-only for regular users)
    
    list: Get all active templates
    retrieve: Get specific template
    """
    
    serializer_class = NotificationTemplateSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get active templates"""
        queryset = NotificationTemplateSelector.get_active_templates()
        
        # Filter by type if specified
        notification_type = self.request.query_params.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
        
        # Search if query provided
        query = self.request.query_params.get('search')
        if query:
            queryset = NotificationTemplateSelector.search_templates(query)
        
        return queryset


class NotificationBatchViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for notification batches
    
    list: Get user's batches
    retrieve: Get specific batch
    create: Create new batch
    """
    
    serializer_class = NotificationBatchSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get batches for current user"""
        return NotificationBatchSelector.get_user_batches(self.request.user)
    
    def get_serializer_class(self):
        """Use different serializers for different actions"""
        if self.action == 'create':
            return NotificationBatchCreateSerializer
        return NotificationBatchSerializer
    
    def create(self, request):
        """Create and process notification batch"""
        serializer = NotificationBatchCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        data = serializer.validated_data
        
        # Get template
        template = NotificationTemplateSelector.get_template_by_code(
            data['template_code']
        )
        
        if not template:
            return Response(
                {'error': f'Template not found: {data["template_code"]}'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create batch
        batch = NotificationBatch.objects.create(
            name=data['name'],
            template=template,
            created_by=request.user
        )
        
        # Queue batch processing task
        send_batch_notifications_task.delay(
            batch_id=str(batch.id),
            user_ids=data['user_ids'],
            context=data['context'],
            send_email=data.get('send_email', False),
            send_sms=data.get('send_sms', False)
        )
        
        response_serializer = NotificationBatchSerializer(batch)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """Get pending batches"""
        batches = NotificationBatchSelector.get_pending_batches()
        serializer = NotificationBatchSerializer(batches, many=True)
        return Response(serializer.data)
