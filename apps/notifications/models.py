"""
Notification Engine Models

Provides comprehensive notification system with:
- Multi-channel delivery (email, in-app, SMS)
- User preferences
- Template-based messaging
- Read/unread tracking
- Entity linking
"""

import uuid
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.core.exceptions import ValidationError

User = get_user_model()


class NotificationType(models.TextChoices):
    """Notification type categories"""
    SYSTEM = 'SYSTEM', 'System Notification'
    WORKFLOW = 'WORKFLOW', 'Workflow Event'
    FINANCIAL = 'FINANCIAL', 'Financial Alert'
    DOCUMENT = 'DOCUMENT', 'Document Activity'
    REPORT = 'REPORT', 'Report Generated'
    DEADLINE = 'DEADLINE', 'Deadline Reminder'
    APPROVAL = 'APPROVAL', 'Approval Request'
    VARIATION = 'VARIATION', 'Variation Update'
    CONTRACT = 'CONTRACT', 'Contract Event'
    PROCUREMENT = 'PROCUREMENT', 'Procurement Activity'


class NotificationPriority(models.TextChoices):
    """Notification priority levels"""
    LOW = 'LOW', 'Low Priority'
    NORMAL = 'NORMAL', 'Normal Priority'
    HIGH = 'HIGH', 'High Priority'
    URGENT = 'URGENT', 'Urgent'


class Notification(models.Model):
    """
    Core notification model
    
    Supports:
    - Multi-channel delivery
    - Entity linking via GenericForeignKey
    - Read/unread tracking
    - Priority levels
    - Metadata storage
    """
    
    # Primary fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='notifications',
        help_text='Recipient of the notification'
    )
    
    # Notification content
    title = models.CharField(
        max_length=200,
        help_text='Notification title/subject'
    )
    
    message = models.TextField(
        help_text='Notification message body'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        help_text='Type of notification'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        help_text='Notification priority level'
    )
    
    # Entity linking (polymorphic relationship)
    entity_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        help_text='Type of related entity'
    )
    
    entity_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        help_text='ID of related entity'
    )
    
    entity_object = GenericForeignKey('entity_type', 'entity_id')
    
    # Tracking fields
    is_read = models.BooleanField(
        default=False,
        help_text='Whether notification has been read'
    )
    
    read_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When notification was read'
    )
    
    # Delivery tracking
    email_sent = models.BooleanField(
        default=False,
        help_text='Whether email was sent'
    )
    
    email_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When email was sent'
    )
    
    sms_sent = models.BooleanField(
        default=False,
        help_text='Whether SMS was sent'
    )
    
    sms_sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When SMS was sent'
    )
    
    # Additional data
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text='Additional notification data (action URLs, entity details, etc.)'
    )
    
    # Action fields
    action_url = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text='URL to navigate to when notification is clicked'
    )
    
    action_label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Label for action button'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text='When notification was created'
    )
    
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text='When notification was last updated'
    )
    
    # Expiry
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text='When notification expires (for cleanup)'
    )
    
    class Meta:
        db_table = 'notifications'
        verbose_name = 'Notification'
        verbose_name_plural = 'Notifications'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', '-created_at']),
            models.Index(fields=['user', 'is_read']),
            models.Index(fields=['notification_type']),
            models.Index(fields=['entity_type', 'entity_id']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"
    
    def mark_as_read(self):
        """Mark notification as read"""
        if not self.is_read:
            self.is_read = True
            self.read_at = timezone.now()
            self.save(update_fields=['is_read', 'read_at'])
    
    def mark_as_unread(self):
        """Mark notification as unread"""
        if self.is_read:
            self.is_read = False
            self.read_at = None
            self.save(update_fields=['is_read', 'read_at'])
    
    @property
    def is_expired(self):
        """Check if notification has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def age_in_days(self):
        """Get notification age in days"""
        delta = timezone.now() - self.created_at
        return delta.days
    
    @property
    def is_urgent(self):
        """Check if notification is urgent"""
        return self.priority == NotificationPriority.URGENT


class NotificationPreference(models.Model):
    """
    User notification preferences
    
    Controls:
    - Channel preferences (email, in-app, SMS)
    - Notification type filters
    - Quiet hours
    - Frequency settings
    """
    
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='notification_preferences',
        help_text='User these preferences belong to'
    )
    
    # Channel preferences
    email_enabled = models.BooleanField(
        default=True,
        help_text='Receive email notifications'
    )
    
    in_app_enabled = models.BooleanField(
        default=True,
        help_text='Receive in-app notifications'
    )
    
    sms_enabled = models.BooleanField(
        default=False,
        help_text='Receive SMS notifications'
    )
    
    # Type-specific preferences
    system_notifications = models.BooleanField(
        default=True,
        help_text='Receive system notifications'
    )
    
    workflow_notifications = models.BooleanField(
        default=True,
        help_text='Receive workflow event notifications'
    )
    
    financial_notifications = models.BooleanField(
        default=True,
        help_text='Receive financial alert notifications'
    )
    
    document_notifications = models.BooleanField(
        default=True,
        help_text='Receive document activity notifications'
    )
    
    report_notifications = models.BooleanField(
        default=True,
        help_text='Receive report generation notifications'
    )
    
    deadline_notifications = models.BooleanField(
        default=True,
        help_text='Receive deadline reminder notifications'
    )
    
    approval_notifications = models.BooleanField(
        default=True,
        help_text='Receive approval request notifications'
    )
    
    # Frequency settings
    digest_enabled = models.BooleanField(
        default=False,
        help_text='Group notifications into daily digest'
    )
    
    digest_time = models.TimeField(
        null=True,
        blank=True,
        help_text='Time to send daily digest (e.g., 09:00)'
    )
    
    # Quiet hours
    quiet_hours_enabled = models.BooleanField(
        default=False,
        help_text='Enable quiet hours (no notifications during specified time)'
    )
    
    quiet_hours_start = models.TimeField(
        null=True,
        blank=True,
        help_text='Start of quiet hours (e.g., 22:00)'
    )
    
    quiet_hours_end = models.TimeField(
        null=True,
        blank=True,
        help_text='End of quiet hours (e.g., 08:00)'
    )
    
    # Contact information
    sms_phone_number = models.CharField(
        max_length=20,
        null=True,
        blank=True,
        help_text='Phone number for SMS notifications'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_preferences'
        verbose_name = 'Notification Preference'
        verbose_name_plural = 'Notification Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.username}"
    
    def is_type_enabled(self, notification_type):
        """Check if a specific notification type is enabled"""
        type_mapping = {
            NotificationType.SYSTEM: self.system_notifications,
            NotificationType.WORKFLOW: self.workflow_notifications,
            NotificationType.FINANCIAL: self.financial_notifications,
            NotificationType.DOCUMENT: self.document_notifications,
            NotificationType.REPORT: self.report_notifications,
            NotificationType.DEADLINE: self.deadline_notifications,
            NotificationType.APPROVAL: self.approval_notifications,
        }
        return type_mapping.get(notification_type, True)
    
    def is_in_quiet_hours(self):
        """Check if current time is within quiet hours"""
        if not self.quiet_hours_enabled or not self.quiet_hours_start or not self.quiet_hours_end:
            return False
        
        now = timezone.now().time()
        
        # Handle case where quiet hours span midnight
        if self.quiet_hours_start > self.quiet_hours_end:
            return now >= self.quiet_hours_start or now <= self.quiet_hours_end
        else:
            return self.quiet_hours_start <= now <= self.quiet_hours_end


class NotificationTemplate(models.Model):
    """
    Notification templates for common events
    
    Supports:
    - Template variables (e.g., {user_name}, {amount})
    - Multi-channel content
    - Event-based triggering
    """
    
    # Template identification
    code = models.CharField(
        max_length=100,
        unique=True,
        help_text='Unique template code (e.g., variation_approved)'
    )
    
    name = models.CharField(
        max_length=200,
        help_text='Human-readable template name'
    )
    
    description = models.TextField(
        blank=True,
        help_text='Template description and usage notes'
    )
    
    notification_type = models.CharField(
        max_length=20,
        choices=NotificationType.choices,
        default=NotificationType.SYSTEM,
        help_text='Type of notification this template generates'
    )
    
    priority = models.CharField(
        max_length=10,
        choices=NotificationPriority.choices,
        default=NotificationPriority.NORMAL,
        help_text='Default priority for notifications from this template'
    )
    
    # Content templates
    title_template = models.CharField(
        max_length=200,
        help_text='Title template (supports variables: {var_name})'
    )
    
    message_template = models.TextField(
        help_text='Message template (supports variables: {var_name})'
    )
    
    email_subject_template = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        help_text='Email subject template (if different from title)'
    )
    
    email_body_template = models.TextField(
        null=True,
        blank=True,
        help_text='Email body template (HTML supported)'
    )
    
    sms_template = models.CharField(
        max_length=160,
        null=True,
        blank=True,
        help_text='SMS template (max 160 chars)'
    )
    
    # Action configuration
    action_url_template = models.CharField(
        max_length=500,
        null=True,
        blank=True,
        help_text='Action URL template (e.g., /projects/{project_id}/)'
    )
    
    action_label = models.CharField(
        max_length=100,
        null=True,
        blank=True,
        help_text='Action button label (e.g., View Project)'
    )
    
    # Status
    is_active = models.BooleanField(
        default=True,
        help_text='Whether this template is active'
    )
    
    # Metadata
    variables = models.JSONField(
        default=list,
        blank=True,
        help_text='List of required template variables (e.g., ["user_name", "amount"])'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'notification_templates'
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"
    
    def render(self, context):
        """
        Render template with provided context
        
        Args:
            context: Dictionary of variable values
            
        Returns:
            Dictionary with rendered content
        """
        def replace_vars(template, ctx):
            """Replace {var} placeholders with context values"""
            if not template:
                return template
            
            result = template
            for key, value in ctx.items():
                placeholder = f"{{{key}}}"
                result = result.replace(placeholder, str(value))
            return result
        
        return {
            'title': replace_vars(self.title_template, context),
            'message': replace_vars(self.message_template, context),
            'email_subject': replace_vars(self.email_subject_template or self.title_template, context),
            'email_body': replace_vars(self.email_body_template or self.message_template, context),
            'sms_body': replace_vars(self.sms_template, context) if self.sms_template else None,
            'action_url': replace_vars(self.action_url_template, context) if self.action_url_template else None,
            'action_label': self.action_label,
        }
    
    def validate_context(self, context):
        """
        Validate that all required variables are present in context
        
        Args:
            context: Dictionary of variable values
            
        Raises:
            ValidationError: If required variables are missing
        """
        missing_vars = [var for var in self.variables if var not in context]
        
        if missing_vars:
            raise ValidationError(
                f"Missing required template variables: {', '.join(missing_vars)}"
            )


class NotificationBatch(models.Model):
    """
    Batch notification tracking
    
    For sending notifications to multiple users at once
    and tracking overall delivery status
    """
    
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False
    )
    
    name = models.CharField(
        max_length=200,
        help_text='Batch name/description'
    )
    
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='batches',
        help_text='Template used for batch'
    )
    
    total_recipients = models.PositiveIntegerField(
        default=0,
        help_text='Total number of recipients'
    )
    
    sent_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of notifications sent'
    )
    
    failed_count = models.PositiveIntegerField(
        default=0,
        help_text='Number of failed notifications'
    )
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('PROCESSING', 'Processing'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING',
        help_text='Batch processing status'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='notification_batches',
        help_text='User who created the batch'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        db_table = 'notification_batches'
        verbose_name = 'Notification Batch'
        verbose_name_plural = 'Notification Batches'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.name} ({self.sent_count}/{self.total_recipients})"
    
    @property
    def success_rate(self):
        """Calculate success rate percentage"""
        if self.total_recipients == 0:
            return 0
        return (self.sent_count / self.total_recipients) * 100
    
    @property
    def is_complete(self):
        """Check if batch is complete"""
        return self.status == 'COMPLETED'
