"""
Event Logging Models

This module defines the SystemEvent model for tracking all platform activities.
"""

from django.db import models
from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
import uuid


class SystemEvent(models.Model):
    """
    Tracks all significant events across the COMS platform.
    
    This model provides a centralized audit log for:
    - User actions (login, logout, CRUD operations)
    - Document activities (upload, sign, share, delete)
    - Workflow events (variation creation, approval, rejection)
    - Financial transactions (claim submission, certification, payment)
    - System events (report generation, data exports, backups)
    
    The model uses GenericForeignKey to link events to any entity type,
    providing flexible entity tracking across all modules.
    """
    
    # Event Types - Categorized by module/domain
    # Authentication Events
    USER_LOGIN = 'user_login'
    USER_LOGOUT = 'user_logout'
    USER_CREATED = 'user_created'
    USER_UPDATED = 'user_updated'
    USER_DELETED = 'user_deleted'
    PASSWORD_CHANGED = 'password_changed'
    PASSWORD_RESET = 'password_reset'
    
    # Organization Events
    ORGANIZATION_CREATED = 'organization_created'
    ORGANIZATION_UPDATED = 'organization_updated'
    ORGANIZATION_DELETED = 'organization_deleted'
    
    # Project Events
    PROJECT_CREATED = 'project_created'
    PROJECT_UPDATED = 'project_updated'
    PROJECT_DELETED = 'project_deleted'
    PROJECT_STATUS_CHANGED = 'project_status_changed'
    
    # Contract Events
    CONTRACT_CREATED = 'contract_created'
    CONTRACT_UPDATED = 'contract_updated'
    CONTRACT_SIGNED = 'contract_signed'
    CONTRACT_TERMINATED = 'contract_terminated'
    CONTRACT_VARIATION_ADDED = 'contract_variation_added'
    
    # Subcontract Events
    SUBCONTRACT_CREATED = 'subcontract_created'
    SUBCONTRACT_UPDATED = 'subcontract_updated'
    SUBCONTRACT_APPROVED = 'subcontract_approved'
    SUBCONTRACT_REJECTED = 'subcontract_rejected'
    
    # Document Events
    DOCUMENT_UPLOADED = 'document_uploaded'
    DOCUMENT_DOWNLOADED = 'document_downloaded'
    DOCUMENT_VIEWED = 'document_viewed'
    DOCUMENT_SHARED = 'document_shared'
    DOCUMENT_SIGNED = 'document_signed'
    DOCUMENT_DELETED = 'document_deleted'
    DOCUMENT_UPDATED = 'document_updated'
    
    # Variation Events
    VARIATION_CREATED = 'variation_created'
    VARIATION_SUBMITTED = 'variation_submitted'
    VARIATION_APPROVED = 'variation_approved'
    VARIATION_REJECTED = 'variation_rejected'
    VARIATION_WITHDRAWN = 'variation_withdrawn'
    VARIATION_REVISED = 'variation_revised'
    
    # Claim (Valuation) Events
    CLAIM_CREATED = 'claim_created'
    CLAIM_SUBMITTED = 'claim_submitted'
    CLAIM_CERTIFIED = 'claim_certified'
    CLAIM_REJECTED = 'claim_rejected'
    CLAIM_REVISED = 'claim_revised'
    CLAIM_PAID = 'claim_paid'
    
    # Payment Events
    PAYMENT_CREATED = 'payment_created'
    PAYMENT_RECORDED = 'payment_recorded'
    PAYMENT_APPROVED = 'payment_approved'
    PAYMENT_PROCESSED = 'payment_processed'
    PAYMENT_REVERSED = 'payment_reversed'
    
    # Approval Workflow Events
    APPROVAL_REQUESTED = 'approval_requested'
    APPROVAL_GRANTED = 'approval_granted'
    APPROVAL_DENIED = 'approval_denied'
    APPROVAL_DELEGATED = 'approval_delegated'
    
    # Report Events
    REPORT_GENERATED = 'report_generated'
    REPORT_EXPORTED = 'report_exported'
    REPORT_SCHEDULED = 'report_scheduled'
    
    # Procurement Events
    LPO_CREATED = 'lpo_created'
    LPO_APPROVED = 'lpo_approved'
    LPO_ISSUED = 'lpo_issued'
    LPO_RECEIVED = 'lpo_received'
    
    # Notification Events
    NOTIFICATION_SENT = 'notification_sent'
    NOTIFICATION_READ = 'notification_read'
    
    # System Events
    DATA_EXPORTED = 'data_exported'
    DATA_IMPORTED = 'data_imported'
    BACKUP_CREATED = 'backup_created'
    SETTINGS_CHANGED = 'settings_changed'
    
    # API Events
    API_REQUEST = 'api_request'
    API_ERROR = 'api_error'
    
    EVENT_TYPE_CHOICES = [
        # Authentication
        (USER_LOGIN, 'User Login'),
        (USER_LOGOUT, 'User Logout'),
        (USER_CREATED, 'User Created'),
        (USER_UPDATED, 'User Updated'),
        (USER_DELETED, 'User Deleted'),
        (PASSWORD_CHANGED, 'Password Changed'),
        (PASSWORD_RESET, 'Password Reset'),
        
        # Organization
        (ORGANIZATION_CREATED, 'Organization Created'),
        (ORGANIZATION_UPDATED, 'Organization Updated'),
        (ORGANIZATION_DELETED, 'Organization Deleted'),
        
        # Project
        (PROJECT_CREATED, 'Project Created'),
        (PROJECT_UPDATED, 'Project Updated'),
        (PROJECT_DELETED, 'Project Deleted'),
        (PROJECT_STATUS_CHANGED, 'Project Status Changed'),
        
        # Contract
        (CONTRACT_CREATED, 'Contract Created'),
        (CONTRACT_UPDATED, 'Contract Updated'),
        (CONTRACT_SIGNED, 'Contract Signed'),
        (CONTRACT_TERMINATED, 'Contract Terminated'),
        (CONTRACT_VARIATION_ADDED, 'Contract Variation Added'),
        
        # Subcontract
        (SUBCONTRACT_CREATED, 'Subcontract Created'),
        (SUBCONTRACT_UPDATED, 'Subcontract Updated'),
        (SUBCONTRACT_APPROVED, 'Subcontract Approved'),
        (SUBCONTRACT_REJECTED, 'Subcontract Rejected'),
        
        # Document
        (DOCUMENT_UPLOADED, 'Document Uploaded'),
        (DOCUMENT_DOWNLOADED, 'Document Downloaded'),
        (DOCUMENT_VIEWED, 'Document Viewed'),
        (DOCUMENT_SHARED, 'Document Shared'),
        (DOCUMENT_SIGNED, 'Document Signed'),
        (DOCUMENT_DELETED, 'Document Deleted'),
        (DOCUMENT_UPDATED, 'Document Updated'),
        
        # Variation
        (VARIATION_CREATED, 'Variation Created'),
        (VARIATION_SUBMITTED, 'Variation Submitted'),
        (VARIATION_APPROVED, 'Variation Approved'),
        (VARIATION_REJECTED, 'Variation Rejected'),
        (VARIATION_WITHDRAWN, 'Variation Withdrawn'),
        (VARIATION_REVISED, 'Variation Revised'),
        
        # Claim
        (CLAIM_CREATED, 'Claim Created'),
        (CLAIM_SUBMITTED, 'Claim Submitted'),
        (CLAIM_CERTIFIED, 'Claim Certified'),
        (CLAIM_REJECTED, 'Claim Rejected'),
        (CLAIM_REVISED, 'Claim Revised'),
        (CLAIM_PAID, 'Claim Paid'),
        
        # Payment
        (PAYMENT_CREATED, 'Payment Created'),
        (PAYMENT_RECORDED, 'Payment Recorded'),
        (PAYMENT_APPROVED, 'Payment Approved'),
        (PAYMENT_PROCESSED, 'Payment Processed'),
        (PAYMENT_REVERSED, 'Payment Reversed'),
        
        # Approval
        (APPROVAL_REQUESTED, 'Approval Requested'),
        (APPROVAL_GRANTED, 'Approval Granted'),
        (APPROVAL_DENIED, 'Approval Denied'),
        (APPROVAL_DELEGATED, 'Approval Delegated'),
        
        # Report
        (REPORT_GENERATED, 'Report Generated'),
        (REPORT_EXPORTED, 'Report Exported'),
        (REPORT_SCHEDULED, 'Report Scheduled'),
        
        # Procurement
        (LPO_CREATED, 'LPO Created'),
        (LPO_APPROVED, 'LPO Approved'),
        (LPO_ISSUED, 'LPO Issued'),
        (LPO_RECEIVED, 'LPO Received'),
        
        # Notification
        (NOTIFICATION_SENT, 'Notification Sent'),
        (NOTIFICATION_READ, 'Notification Read'),
        
        # System
        (DATA_EXPORTED, 'Data Exported'),
        (DATA_IMPORTED, 'Data Imported'),
        (BACKUP_CREATED, 'Backup Created'),
        (SETTINGS_CHANGED, 'Settings Changed'),
        
        # API
        (API_REQUEST, 'API Request'),
        (API_ERROR, 'API Error'),
    ]
    
    # Event Categories for grouping
    CATEGORY_AUTHENTICATION = 'authentication'
    CATEGORY_ORGANIZATION = 'organization'
    CATEGORY_PROJECT = 'project'
    CATEGORY_CONTRACT = 'contract'
    CATEGORY_SUBCONTRACT = 'subcontract'
    CATEGORY_DOCUMENT = 'document'
    CATEGORY_VARIATION = 'variation'
    CATEGORY_CLAIM = 'claim'
    CATEGORY_PAYMENT = 'payment'
    CATEGORY_APPROVAL = 'approval'
    CATEGORY_REPORT = 'report'
    CATEGORY_PROCUREMENT = 'procurement'
    CATEGORY_NOTIFICATION = 'notification'
    CATEGORY_SYSTEM = 'system'
    CATEGORY_API = 'api'
    
    # Mapping event types to categories
    EVENT_CATEGORIES = {
        USER_LOGIN: CATEGORY_AUTHENTICATION,
        USER_LOGOUT: CATEGORY_AUTHENTICATION,
        USER_CREATED: CATEGORY_AUTHENTICATION,
        USER_UPDATED: CATEGORY_AUTHENTICATION,
        USER_DELETED: CATEGORY_AUTHENTICATION,
        PASSWORD_CHANGED: CATEGORY_AUTHENTICATION,
        PASSWORD_RESET: CATEGORY_AUTHENTICATION,
        
        ORGANIZATION_CREATED: CATEGORY_ORGANIZATION,
        ORGANIZATION_UPDATED: CATEGORY_ORGANIZATION,
        ORGANIZATION_DELETED: CATEGORY_ORGANIZATION,
        
        PROJECT_CREATED: CATEGORY_PROJECT,
        PROJECT_UPDATED: CATEGORY_PROJECT,
        PROJECT_DELETED: CATEGORY_PROJECT,
        PROJECT_STATUS_CHANGED: CATEGORY_PROJECT,
        
        CONTRACT_CREATED: CATEGORY_CONTRACT,
        CONTRACT_UPDATED: CATEGORY_CONTRACT,
        CONTRACT_SIGNED: CATEGORY_CONTRACT,
        CONTRACT_TERMINATED: CATEGORY_CONTRACT,
        CONTRACT_VARIATION_ADDED: CATEGORY_CONTRACT,
        
        SUBCONTRACT_CREATED: CATEGORY_SUBCONTRACT,
        SUBCONTRACT_UPDATED: CATEGORY_SUBCONTRACT,
        SUBCONTRACT_APPROVED: CATEGORY_SUBCONTRACT,
        SUBCONTRACT_REJECTED: CATEGORY_SUBCONTRACT,
        
        DOCUMENT_UPLOADED: CATEGORY_DOCUMENT,
        DOCUMENT_DOWNLOADED: CATEGORY_DOCUMENT,
        DOCUMENT_VIEWED: CATEGORY_DOCUMENT,
        DOCUMENT_SHARED: CATEGORY_DOCUMENT,
        DOCUMENT_SIGNED: CATEGORY_DOCUMENT,
        DOCUMENT_DELETED: CATEGORY_DOCUMENT,
        DOCUMENT_UPDATED: CATEGORY_DOCUMENT,
        
        VARIATION_CREATED: CATEGORY_VARIATION,
        VARIATION_SUBMITTED: CATEGORY_VARIATION,
        VARIATION_APPROVED: CATEGORY_VARIATION,
        VARIATION_REJECTED: CATEGORY_VARIATION,
        VARIATION_WITHDRAWN: CATEGORY_VARIATION,
        VARIATION_REVISED: CATEGORY_VARIATION,
        
        CLAIM_CREATED: CATEGORY_CLAIM,
        CLAIM_SUBMITTED: CATEGORY_CLAIM,
        CLAIM_CERTIFIED: CATEGORY_CLAIM,
        CLAIM_REJECTED: CATEGORY_CLAIM,
        CLAIM_REVISED: CATEGORY_CLAIM,
        CLAIM_PAID: CATEGORY_CLAIM,
        
        PAYMENT_CREATED: CATEGORY_PAYMENT,
        PAYMENT_RECORDED: CATEGORY_PAYMENT,
        PAYMENT_APPROVED: CATEGORY_PAYMENT,
        PAYMENT_PROCESSED: CATEGORY_PAYMENT,
        PAYMENT_REVERSED: CATEGORY_PAYMENT,
        
        APPROVAL_REQUESTED: CATEGORY_APPROVAL,
        APPROVAL_GRANTED: CATEGORY_APPROVAL,
        APPROVAL_DENIED: CATEGORY_APPROVAL,
        APPROVAL_DELEGATED: CATEGORY_APPROVAL,
        
        REPORT_GENERATED: CATEGORY_REPORT,
        REPORT_EXPORTED: CATEGORY_REPORT,
        REPORT_SCHEDULED: CATEGORY_REPORT,
        
        LPO_CREATED: CATEGORY_PROCUREMENT,
        LPO_APPROVED: CATEGORY_PROCUREMENT,
        LPO_ISSUED: CATEGORY_PROCUREMENT,
        LPO_RECEIVED: CATEGORY_PROCUREMENT,
        
        NOTIFICATION_SENT: CATEGORY_NOTIFICATION,
        NOTIFICATION_READ: CATEGORY_NOTIFICATION,
        
        DATA_EXPORTED: CATEGORY_SYSTEM,
        DATA_IMPORTED: CATEGORY_SYSTEM,
        BACKUP_CREATED: CATEGORY_SYSTEM,
        SETTINGS_CHANGED: CATEGORY_SYSTEM,
        
        API_REQUEST: CATEGORY_API,
        API_ERROR: CATEGORY_API,
    }
    
    # Primary Fields
    id = models.UUIDField(
        primary_key=True,
        default=uuid.uuid4,
        editable=False,
        help_text="Unique identifier for the event"
    )
    
    event_type = models.CharField(
        max_length=50,
        choices=EVENT_TYPE_CHOICES,
        db_index=True,
        help_text="Type of event that occurred"
    )
    
    # Entity Tracking (Generic Foreign Key)
    entity_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        help_text="Type of entity this event relates to"
    )
    
    entity_id = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        db_index=True,
        help_text="ID of the entity this event relates to"
    )
    
    entity = GenericForeignKey('entity_type', 'entity_id')
    
    # User and Organization Context
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        db_index=True,
        help_text="User who triggered this event (if applicable)"
    )
    
    organization = models.ForeignKey(
        'authentication.Organization',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        db_index=True,
        help_text="Organization context for this event"
    )
    
    project = models.ForeignKey(
        'projects.Project',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='events',
        db_index=True,
        help_text="Project context for this event (if applicable)"
    )
    
    # Timestamp and Metadata
    timestamp = models.DateTimeField(
        default=timezone.now,
        db_index=True,
        help_text="When the event occurred"
    )
    
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Additional event data (context, changes, etc.)"
    )
    
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address from which the event originated"
    )
    
    # Additional Context
    user_agent = models.TextField(
        blank=True,
        default='',
        help_text="User agent string (for web requests)"
    )
    
    request_path = models.CharField(
        max_length=500,
        blank=True,
        default='',
        help_text="Request path (for API events)"
    )
    
    request_method = models.CharField(
        max_length=10,
        blank=True,
        default='',
        help_text="HTTP method (GET, POST, PUT, DELETE, etc.)"
    )
    
    response_status = models.IntegerField(
        null=True,
        blank=True,
        help_text="HTTP response status code"
    )
    
    duration_ms = models.IntegerField(
        null=True,
        blank=True,
        help_text="Request duration in milliseconds (for performance tracking)"
    )
    
    class Meta:
        db_table = 'system_events'
        ordering = ['-timestamp']
        verbose_name = 'System Event'
        verbose_name_plural = 'System Events'
        indexes = [
            models.Index(fields=['-timestamp'], name='events_timestamp_idx'),
            models.Index(fields=['event_type', '-timestamp'], name='events_type_time_idx'),
            models.Index(fields=['user', '-timestamp'], name='events_user_time_idx'),
            models.Index(fields=['project', '-timestamp'], name='events_project_time_idx'),
            models.Index(fields=['organization', '-timestamp'], name='events_org_time_idx'),
            models.Index(fields=['entity_type', 'entity_id'], name='events_entity_idx'),
        ]
    
    def __str__(self):
        """String representation of the event"""
        user_str = self.user.get_full_name() if self.user else 'System'
        return f"{user_str} - {self.get_event_type_display()} at {self.timestamp.strftime('%Y-%m-%d %H:%M:%S')}"
    
    @property
    def category(self):
        """Get the category for this event type"""
        return self.EVENT_CATEGORIES.get(self.event_type, 'other')
    
    @property
    def entity_display(self):
        """Get a display name for the related entity"""
        if self.entity:
            return str(self.entity)
        return None
    
    @property
    def time_since(self):
        """Get human-readable time since event occurred"""
        from django.utils.timesince import timesince
        return timesince(self.timestamp)
    
    def get_metadata_value(self, key, default=None):
        """Safely get a value from metadata JSON"""
        return self.metadata.get(key, default)
    
    def set_metadata_value(self, key, value):
        """Set a value in metadata JSON"""
        self.metadata[key] = value
        self.save(update_fields=['metadata'])
