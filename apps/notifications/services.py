"""
Notification Services

Business logic layer for notification creation and delivery.
Handles multi-channel delivery, template rendering, and preference checking.
"""

import logging
from typing import List, Dict, Any, Optional
from datetime import timedelta

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.core.mail import send_mail, EmailMultiAlternatives
from django.conf import settings
from django.template import Context, Template
from django.utils import timezone
from django.db import transaction

from .models import (
    Notification,
    NotificationPreference,
    NotificationTemplate,
    NotificationBatch,
    NotificationType,
    NotificationPriority
)
from .selectors import (
    NotificationSelector,
    NotificationPreferenceSelector,
    NotificationTemplateSelector
)

User = get_user_model()
logger = logging.getLogger(__name__)


class NotificationService:
    """
    Core notification service
    
    Handles:
    - Notification creation
    - Multi-channel delivery
    - Template rendering
    - Preference checking
    """
    
    @staticmethod
    def create_notification(
        user,
        title: str,
        message: str,
        notification_type: str = NotificationType.SYSTEM,
        priority: str = NotificationPriority.NORMAL,
        entity_object=None,
        metadata: dict = None,
        action_url: str = None,
        action_label: str = None,
        expires_in_days: int = None,
        send_email: bool = False,
        send_sms: bool = False
    ) -> Notification:
        """
        Create a new notification
        
        Args:
            user: User to notify
            title: Notification title
            message: Notification message
            notification_type: Type of notification
            priority: Priority level
            entity_object: Related entity (optional)
            metadata: Additional data (optional)
            action_url: URL for action button (optional)
            action_label: Label for action button (optional)
            expires_in_days: Days until expiration (optional)
            send_email: Whether to send email notification
            send_sms: Whether to send SMS notification
            
        Returns:
            Created Notification instance
        """
        # Get entity details if provided
        entity_type = None
        entity_id = None
        
        if entity_object:
            entity_type = ContentType.objects.get_for_model(entity_object)
            entity_id = str(entity_object.pk)
        
        # Calculate expiry
        expires_at = None
        if expires_in_days:
            expires_at = timezone.now() + timedelta(days=expires_in_days)
        
        # Create notification
        notification = Notification.objects.create(
            user=user,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            entity_type=entity_type,
            entity_id=entity_id,
            metadata=metadata or {},
            action_url=action_url,
            action_label=action_label,
            expires_at=expires_at
        )
        
        logger.info(
            f"Created notification {notification.id} for user {user.username}: {title}"
        )
        
        # Send through additional channels if requested
        if send_email:
            NotificationDeliveryService.send_email_notification(notification)
        
        if send_sms:
            NotificationDeliveryService.send_sms_notification(notification)
        
        return notification
    
    @staticmethod
    def create_from_template(
        template_code: str,
        user,
        context: dict,
        entity_object=None,
        send_email: bool = False,
        send_sms: bool = False,
        **kwargs
    ) -> Optional[Notification]:
        """
        Create notification from template
        
        Args:
            template_code: Template code
            user: User to notify
            context: Template variables
            entity_object: Related entity (optional)
            send_email: Whether to send email
            send_sms: Whether to send SMS
            **kwargs: Additional notification parameters
            
        Returns:
            Created Notification instance or None if template not found
        """
        # Get template
        template = NotificationTemplateSelector.get_template_by_code(template_code)
        
        if not template:
            logger.error(f"Template not found: {template_code}")
            return None
        
        # Validate context
        try:
            template.validate_context(context)
        except Exception as e:
            logger.error(f"Template validation failed: {e}")
            return None
        
        # Render template
        rendered = template.render(context)
        
        # Create notification
        notification = NotificationService.create_notification(
            user=user,
            title=rendered['title'],
            message=rendered['message'],
            notification_type=template.notification_type,
            priority=kwargs.get('priority', template.priority),
            entity_object=entity_object,
            metadata=kwargs.get('metadata', {}),
            action_url=rendered['action_url'],
            action_label=rendered['action_label'],
            expires_in_days=kwargs.get('expires_in_days'),
            send_email=send_email,
            send_sms=send_sms
        )
        
        # Store rendered email/SMS content in metadata for later use
        notification.metadata['email_subject'] = rendered['email_subject']
        notification.metadata['email_body'] = rendered['email_body']
        notification.metadata['sms_body'] = rendered['sms_body']
        notification.save(update_fields=['metadata'])
        
        return notification
    
    @staticmethod
    def create_bulk_notifications(
        users: List[User],
        title: str,
        message: str,
        **kwargs
    ) -> List[Notification]:
        """
        Create notifications for multiple users
        
        Args:
            users: List of users to notify
            title: Notification title
            message: Notification message
            **kwargs: Additional notification parameters
            
        Returns:
            List of created Notification instances
        """
        notifications = []
        
        with transaction.atomic():
            for user in users:
                notification = NotificationService.create_notification(
                    user=user,
                    title=title,
                    message=message,
                    **kwargs
                )
                notifications.append(notification)
        
        logger.info(f"Created {len(notifications)} bulk notifications")
        
        return notifications
    
    @staticmethod
    def mark_as_read(notification_id: str, user=None) -> bool:
        """
        Mark notification as read
        
        Args:
            notification_id: Notification UUID
            user: User (for verification)
            
        Returns:
            True if successful, False otherwise
        """
        notification = NotificationSelector.get_notification_by_id(
            notification_id,
            user=user
        )
        
        if not notification:
            logger.warning(f"Notification not found: {notification_id}")
            return False
        
        notification.mark_as_read()
        logger.info(f"Marked notification {notification_id} as read")
        
        return True
    
    @staticmethod
    def mark_all_as_read(user) -> int:
        """
        Mark all notifications as read for a user
        
        Args:
            user: User instance
            
        Returns:
            Number of notifications marked as read
        """
        count = Notification.objects.filter(
            user=user,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )
        
        logger.info(f"Marked {count} notifications as read for user {user.username}")
        
        return count
    
    @staticmethod
    def delete_notification(notification_id: str, user=None) -> bool:
        """
        Delete a notification
        
        Args:
            notification_id: Notification UUID
            user: User (for verification)
            
        Returns:
            True if successful, False otherwise
        """
        notification = NotificationSelector.get_notification_by_id(
            notification_id,
            user=user
        )
        
        if not notification:
            return False
        
        notification.delete()
        logger.info(f"Deleted notification {notification_id}")
        
        return True
    
    @staticmethod
    def cleanup_old_notifications(days: int = 90) -> int:
        """
        Delete notifications older than specified days
        
        Args:
            days: Age threshold in days
            
        Returns:
            Number of notifications deleted
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        
        count, _ = Notification.objects.filter(
            created_at__lt=cutoff_date,
            is_read=True
        ).delete()
        
        logger.info(f"Cleaned up {count} old notifications")
        
        return count
    
    @staticmethod
    def cleanup_expired_notifications() -> int:
        """
        Delete expired notifications
        
        Returns:
            Number of notifications deleted
        """
        count, _ = Notification.objects.filter(
            expires_at__lt=timezone.now()
        ).delete()
        
        logger.info(f"Cleaned up {count} expired notifications")
        
        return count


class NotificationDeliveryService:
    """
    Multi-channel notification delivery service
    
    Handles:
    - Email delivery
    - SMS delivery
    - Preference checking
    - Delivery tracking
    """
    
    @staticmethod
    def send_email_notification(notification: Notification) -> bool:
        """
        Send email notification
        
        Args:
            notification: Notification instance
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check user preferences
        if not NotificationPreferenceSelector.is_user_opted_in(
            notification.user,
            notification.notification_type,
            channel='email'
        ):
            logger.info(
                f"User {notification.user.username} opted out of email for "
                f"{notification.notification_type}"
            )
            return False
        
        # Get user email
        if not notification.user.email:
            logger.warning(f"No email address for user {notification.user.username}")
            return False
        
        # Prepare email content
        subject = notification.metadata.get(
            'email_subject',
            notification.title
        )
        
        html_body = notification.metadata.get('email_body')
        text_body = notification.message
        
        try:
            if html_body:
                # Send HTML email
                email = EmailMultiAlternatives(
                    subject=subject,
                    body=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[notification.user.email]
                )
                email.attach_alternative(html_body, "text/html")
                email.send()
            else:
                # Send plain text email
                send_mail(
                    subject=subject,
                    message=text_body,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[notification.user.email],
                    fail_silently=False
                )
            
            # Update notification
            notification.email_sent = True
            notification.email_sent_at = timezone.now()
            notification.save(update_fields=['email_sent', 'email_sent_at'])
            
            logger.info(f"Sent email notification {notification.id} to {notification.user.email}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send email notification {notification.id}: {e}")
            return False
    
    @staticmethod
    def send_sms_notification(notification: Notification) -> bool:
        """
        Send SMS notification
        
        Args:
            notification: Notification instance
            
        Returns:
            True if sent successfully, False otherwise
        """
        # Check user preferences
        if not NotificationPreferenceSelector.is_user_opted_in(
            notification.user,
            notification.notification_type,
            channel='sms'
        ):
            logger.info(
                f"User {notification.user.username} opted out of SMS for "
                f"{notification.notification_type}"
            )
            return False
        
        # Get user phone number
        preferences = NotificationPreferenceSelector.get_user_preferences(
            notification.user
        )
        
        if not preferences.sms_phone_number:
            logger.warning(
                f"No phone number for user {notification.user.username}"
            )
            return False
        
        # Get SMS content
        sms_body = notification.metadata.get('sms_body', notification.message)
        
        # Truncate to 160 characters if needed
        if len(sms_body) > 160:
            sms_body = sms_body[:157] + '...'
        
        try:
            # TODO: Integrate with SMS provider (Twilio, AWS SNS, etc.)
            # For now, just log the SMS
            logger.info(
                f"SMS to {preferences.sms_phone_number}: {sms_body}"
            )
            
            # Update notification
            notification.sms_sent = True
            notification.sms_sent_at = timezone.now()
            notification.save(update_fields=['sms_sent', 'sms_sent_at'])
            
            logger.info(f"Sent SMS notification {notification.id}")
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to send SMS notification {notification.id}: {e}")
            return False
    
    @staticmethod
    def send_batch_notifications(
        batch: NotificationBatch,
        users: List[User],
        context: dict,
        send_email: bool = False,
        send_sms: bool = False
    ) -> Dict[str, int]:
        """
        Send batch notifications using a template
        
        Args:
            batch: NotificationBatch instance
            users: List of users to notify
            context: Template context
            send_email: Whether to send emails
            send_sms: Whether to send SMS
            
        Returns:
            Dictionary with counts (sent, failed)
        """
        sent_count = 0
        failed_count = 0
        
        batch.status = 'PROCESSING'
        batch.total_recipients = len(users)
        batch.save(update_fields=['status', 'total_recipients'])
        
        for user in users:
            try:
                # Create user-specific context
                user_context = {
                    **context,
                    'user_name': user.get_full_name() or user.username,
                    'user_email': user.email,
                }
                
                # Create notification from template
                notification = NotificationService.create_from_template(
                    template_code=batch.template.code,
                    user=user,
                    context=user_context,
                    send_email=send_email,
                    send_sms=send_sms
                )
                
                if notification:
                    sent_count += 1
                else:
                    failed_count += 1
                    
            except Exception as e:
                logger.error(f"Failed to send notification to {user.username}: {e}")
                failed_count += 1
        
        # Update batch
        batch.sent_count = sent_count
        batch.failed_count = failed_count
        batch.status = 'COMPLETED'
        batch.completed_at = timezone.now()
        batch.save(update_fields=[
            'sent_count',
            'failed_count',
            'status',
            'completed_at'
        ])
        
        logger.info(
            f"Batch {batch.id} completed: {sent_count} sent, {failed_count} failed"
        )
        
        return {
            'sent': sent_count,
            'failed': failed_count
        }


class NotificationPreferenceService:
    """
    Notification preference management service
    """
    
    @staticmethod
    def update_preferences(user, **preferences) -> NotificationPreference:
        """
        Update user notification preferences
        
        Args:
            user: User instance
            **preferences: Preference fields to update
            
        Returns:
            Updated NotificationPreference instance
        """
        prefs = NotificationPreferenceSelector.get_user_preferences(user)
        
        for field, value in preferences.items():
            if hasattr(prefs, field):
                setattr(prefs, field, value)
        
        prefs.save()
        
        logger.info(f"Updated notification preferences for user {user.username}")
        
        return prefs
    
    @staticmethod
    def enable_channel(user, channel: str) -> bool:
        """
        Enable a notification channel
        
        Args:
            user: User instance
            channel: 'email', 'in_app', or 'sms'
            
        Returns:
            True if successful
        """
        field_map = {
            'email': 'email_enabled',
            'in_app': 'in_app_enabled',
            'sms': 'sms_enabled'
        }
        
        if channel not in field_map:
            return False
        
        NotificationPreferenceService.update_preferences(
            user,
            **{field_map[channel]: True}
        )
        
        return True
    
    @staticmethod
    def disable_channel(user, channel: str) -> bool:
        """
        Disable a notification channel
        
        Args:
            user: User instance
            channel: 'email', 'in_app', or 'sms'
            
        Returns:
            True if successful
        """
        field_map = {
            'email': 'email_enabled',
            'in_app': 'in_app_enabled',
            'sms': 'sms_enabled'
        }
        
        if channel not in field_map:
            return False
        
        NotificationPreferenceService.update_preferences(
            user,
            **{field_map[channel]: False}
        )
        
        return True


class NotificationTemplateService:
    """
    Notification template management service
    """
    
    @staticmethod
    def create_template(
        code: str,
        name: str,
        title_template: str,
        message_template: str,
        **kwargs
    ) -> NotificationTemplate:
        """
        Create a notification template
        
        Args:
            code: Unique template code
            name: Template name
            title_template: Title template string
            message_template: Message template string
            **kwargs: Additional template fields
            
        Returns:
            Created NotificationTemplate instance
        """
        template = NotificationTemplate.objects.create(
            code=code,
            name=name,
            title_template=title_template,
            message_template=message_template,
            **kwargs
        )
        
        logger.info(f"Created notification template: {code}")
        
        return template
    
    @staticmethod
    def update_template(template_id: int, **updates) -> Optional[NotificationTemplate]:
        """
        Update a notification template
        
        Args:
            template_id: Template ID
            **updates: Fields to update
            
        Returns:
            Updated NotificationTemplate instance or None
        """
        try:
            template = NotificationTemplate.objects.get(id=template_id)
            
            for field, value in updates.items():
                if hasattr(template, field):
                    setattr(template, field, value)
            
            template.save()
            
            logger.info(f"Updated notification template: {template.code}")
            
            return template
            
        except NotificationTemplate.DoesNotExist:
            logger.error(f"Template not found: {template_id}")
            return None
