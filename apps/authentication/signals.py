"""
Django signals for authentication module
Handles automatic audit logging for security events
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out, user_login_failed
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import User, ProjectAccess, AuditLog


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log successful user login"""
    AuditLog.objects.create(
        user=user,
        action=AuditLog.Action.USER_LOGIN,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        details={'timestamp': timezone.now().isoformat()}
    )
    
    # Update last login IP
    user.last_login_ip = get_client_ip(request)
    user.save(update_fields=['last_login_ip'])


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout"""
    if user:
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.USER_LOGOUT,
            ip_address=get_client_ip(request),
            user_agent=request.META.get('HTTP_USER_AGENT', '')[:500]
        )


@receiver(user_login_failed)
def log_failed_login(sender, credentials, request, **kwargs):
    """Log failed login attempts"""
    AuditLog.objects.create(
        user=None,
        action=AuditLog.Action.LOGIN_FAILED,
        ip_address=get_client_ip(request),
        user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
        details={
            'username': credentials.get('username', 'unknown'),
            'timestamp': timezone.now().isoformat()
        }
    )


@receiver(post_save, sender=User)
def log_user_changes(sender, instance, created, **kwargs):
    """Log user account creation and changes"""
    if created:
        AuditLog.objects.create(
            user=instance,
            action=AuditLog.Action.USER_CREATED,
            details={
                'system_role': instance.system_role,
                'email': instance.email
            }
        )


@receiver(post_save, sender=ProjectAccess)
def log_access_changes(sender, instance, created, **kwargs):
    """Log project access grants and revocations"""
    if created:
        AuditLog.objects.create(
            user=instance.user,
            action=AuditLog.Action.ACCESS_GRANTED,
            details={
                'project': str(instance.project),
                'project_role': instance.project_role,
                'assigned_by': instance.assigned_by.username if instance.assigned_by else None
            }
        )
    elif not instance.is_active and instance.removed_at:
        AuditLog.objects.create(
            user=instance.user,
            action=AuditLog.Action.ACCESS_REVOKED,
            details={
                'project': str(instance.project),
                'project_role': instance.project_role
            }
        )


def get_client_ip(request):
    """Extract client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip
