"""
Celery Tasks for Notification Engine

Asynchronous tasks for:
- Email delivery
- SMS delivery
- Batch notifications
- Cleanup operations
- Scheduled digests
"""

import logging
from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

from .models import Notification, NotificationBatch
from .services import (
    NotificationService,
    NotificationDeliveryService,
    NotificationPreferenceService
)
from .selectors import (
    NotificationSelector,
    NotificationBatchSelector
)

User = get_user_model()
logger = logging.getLogger(__name__)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_email_task(self, notification_id: str):
    """
    Send email notification asynchronously
    
    Args:
        notification_id: UUID of notification to send
        
    Returns:
        True if sent successfully
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        success = NotificationDeliveryService.send_email_notification(notification)
        
        if not success:
            logger.warning(f"Email notification {notification_id} not sent (user preferences or missing email)")
        
        return success
        
    except Notification.DoesNotExist:
        logger.error(f"Notification not found: {notification_id}")
        return False
        
    except Exception as exc:
        logger.error(f"Error sending email notification {notification_id}: {exc}")
        
        # Retry on failure
        raise self.retry(exc=exc)


@shared_task(
    bind=True,
    max_retries=3,
    default_retry_delay=60
)
def send_sms_task(self, notification_id: str):
    """
    Send SMS notification asynchronously
    
    Args:
        notification_id: UUID of notification to send
        
    Returns:
        True if sent successfully
    """
    try:
        notification = Notification.objects.get(id=notification_id)
        
        success = NotificationDeliveryService.send_sms_notification(notification)
        
        if not success:
            logger.warning(f"SMS notification {notification_id} not sent (user preferences or missing phone)")
        
        return success
        
    except Notification.DoesNotExist:
        logger.error(f"Notification not found: {notification_id}")
        return False
        
    except Exception as exc:
        logger.error(f"Error sending SMS notification {notification_id}: {exc}")
        
        # Retry on failure
        raise self.retry(exc=exc)


@shared_task
def send_batch_notifications_task(batch_id: str, user_ids: list, context: dict, send_email: bool = False, send_sms: bool = False):
    """
    Send batch notifications asynchronously
    
    Args:
        batch_id: UUID of notification batch
        user_ids: List of user IDs to notify
        context: Template context dictionary
        send_email: Whether to send emails
        send_sms: Whether to send SMS
        
    Returns:
        Dictionary with results
    """
    try:
        batch = NotificationBatch.objects.get(id=batch_id)
        users = User.objects.filter(id__in=user_ids)
        
        results = NotificationDeliveryService.send_batch_notifications(
            batch=batch,
            users=list(users),
            context=context,
            send_email=send_email,
            send_sms=send_sms
        )
        
        logger.info(f"Batch {batch_id} completed: {results}")
        
        return results
        
    except NotificationBatch.DoesNotExist:
        logger.error(f"Notification batch not found: {batch_id}")
        return {'sent': 0, 'failed': 0}
        
    except Exception as exc:
        logger.error(f"Error processing batch {batch_id}: {exc}")
        
        # Update batch status to failed
        try:
            batch = NotificationBatch.objects.get(id=batch_id)
            batch.status = 'FAILED'
            batch.completed_at = timezone.now()
            batch.save(update_fields=['status', 'completed_at'])
        except:
            pass
        
        return {'sent': 0, 'failed': len(user_ids)}


@shared_task
def cleanup_old_notifications_task(days: int = 90):
    """
    Clean up old read notifications
    
    Args:
        days: Delete notifications older than this many days
        
    Returns:
        Number of notifications deleted
    """
    try:
        count = NotificationService.cleanup_old_notifications(days=days)
        logger.info(f"Cleaned up {count} old notifications")
        return count
        
    except Exception as exc:
        logger.error(f"Error cleaning up old notifications: {exc}")
        return 0


@shared_task
def cleanup_expired_notifications_task():
    """
    Clean up expired notifications
    
    Returns:
        Number of notifications deleted
    """
    try:
        count = NotificationService.cleanup_expired_notifications()
        logger.info(f"Cleaned up {count} expired notifications")
        return count
        
    except Exception as exc:
        logger.error(f"Error cleaning up expired notifications: {exc}")
        return 0


@shared_task
def send_daily_digest_task():
    """
    Send daily notification digest to users who have it enabled
    
    Returns:
        Number of digests sent
    """
    try:
        from django.core.mail import send_mail
        from django.conf import settings
        
        sent_count = 0
        
        # Get users with digest enabled
        users = User.objects.select_related(
            'notification_preferences'
        ).filter(
            notification_preferences__digest_enabled=True,
            notification_preferences__isnull=False
        )
        
        for user in users:
            preferences = user.notification_preferences
            
            # Check if it's the right time for this user's digest
            # (in production, would check against digest_time)
            
            # Get unread notifications from last 24 hours
            notifications = NotificationSelector.get_user_notifications(
                user=user,
                is_read=False,
                days=1
            )
            
            if not notifications.exists():
                continue
            
            # Build digest email
            notification_list = "\n".join([
                f"- {n.title}" for n in notifications[:10]
            ])
            
            message = f"""
Hello {user.get_full_name() or user.username},

You have {notifications.count()} unread notifications:

{notification_list}

Log in to view all notifications.

Best regards,
COMS System
            """
            
            try:
                send_mail(
                    subject=f"Daily Notification Digest - {notifications.count()} unread",
                    message=message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[user.email],
                    fail_silently=False
                )
                
                sent_count += 1
                logger.info(f"Sent daily digest to {user.username}")
                
            except Exception as e:
                logger.error(f"Failed to send digest to {user.username}: {e}")
        
        logger.info(f"Sent {sent_count} daily digests")
        return sent_count
        
    except Exception as exc:
        logger.error(f"Error sending daily digests: {exc}")
        return 0


@shared_task
def process_pending_batches_task():
    """
    Process any pending notification batches
    
    Returns:
        Number of batches processed
    """
    try:
        pending_batches = NotificationBatchSelector.get_pending_batches()
        
        processed_count = 0
        
        for batch in pending_batches:
            # Get batch metadata (should include user_ids and context)
            # This is a placeholder - actual implementation would depend on
            # how batches are structured
            logger.info(f"Processing batch {batch.id}: {batch.name}")
            processed_count += 1
        
        logger.info(f"Processed {processed_count} pending batches")
        return processed_count
        
    except Exception as exc:
        logger.error(f"Error processing pending batches: {exc}")
        return 0


@shared_task
def send_deadline_reminders_task():
    """
    Send deadline reminder notifications
    
    This is a placeholder task that would integrate with other modules
    to send reminders for upcoming deadlines (contracts, claims, etc.)
    
    Returns:
        Number of reminders sent
    """
    try:
        # TODO: Integrate with Projects, Contracts, Claims modules
        # to find upcoming deadlines and send notifications
        
        logger.info("Deadline reminders task executed")
        return 0
        
    except Exception as exc:
        logger.error(f"Error sending deadline reminders: {exc}")
        return 0


@shared_task
def notify_users_bulk(user_ids: list, title: str, message: str, **kwargs):
    """
    Send notification to multiple users
    
    Args:
        user_ids: List of user IDs
        title: Notification title
        message: Notification message
        **kwargs: Additional notification parameters
        
    Returns:
        Number of notifications created
    """
    try:
        users = User.objects.filter(id__in=user_ids)
        
        notifications = NotificationService.create_bulk_notifications(
            users=list(users),
            title=title,
            message=message,
            **kwargs
        )
        
        logger.info(f"Created {len(notifications)} bulk notifications")
        
        # Send emails if requested
        if kwargs.get('send_email'):
            for notification in notifications:
                send_email_task.delay(str(notification.id))
        
        # Send SMS if requested
        if kwargs.get('send_sms'):
            for notification in notifications:
                send_sms_task.delay(str(notification.id))
        
        return len(notifications)
        
    except Exception as exc:
        logger.error(f"Error sending bulk notifications: {exc}")
        return 0


# Celery Beat Schedule (add to celerybeat-schedule.py or settings.py)
"""
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications_task',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2:00 AM
        'args': (90,)  # Delete notifications older than 90 days
    },
    'cleanup-expired-notifications': {
        'task': 'apps.notifications.tasks.cleanup_expired_notifications_task',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3:00 AM
    },
    'send-daily-digest': {
        'task': 'apps.notifications.tasks.send_daily_digest_task',
        'schedule': crontab(hour=9, minute=0),  # Daily at 9:00 AM
    },
    'send-deadline-reminders': {
        'task': 'apps.notifications.tasks.send_deadline_reminders_task',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8:00 AM
    },
    'process-pending-batches': {
        'task': 'apps.notifications.tasks.process_pending_batches_task',
        'schedule': crontab(minute='*/30'),  # Every 30 minutes
    },
}
"""
