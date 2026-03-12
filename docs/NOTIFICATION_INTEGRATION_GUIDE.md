# Notification Engine - Quick Integration Guide

This guide shows how to integrate the Notification Engine with existing COMS modules.

## Quick Start

### 1. Import Services

```python
from apps.notifications.services import NotificationService
from apps.notifications.models import NotificationType, NotificationPriority
```

### 2. Basic Notification

```python
# Send a simple notification
NotificationService.create_notification(
    user=user,
    title="Title Here",
    message="Message here",
    notification_type=NotificationType.WORKFLOW,
    send_email=True
)
```

## Integration Examples by Module

### Variations Module

```python
# apps/variations/services.py

from apps.notifications.services import NotificationService

class VariationService:
    
    @staticmethod
    def approve_variation(variation_id, approver):
        """Approve variation and notify creator"""
        variation = Variation.objects.get(id=variation_id)
        variation.status = 'APPROVED'
        variation.approved_by = approver
        variation.save()
        
        # Notify variation creator
        NotificationService.create_notification(
            user=variation.created_by,
            title=f"Variation {variation.number} Approved",
            message=f"Your variation {variation.number} for £{variation.amount:,.2f} has been approved by {approver.get_full_name()}.",
            notification_type=NotificationType.VARIATION,
            priority=NotificationPriority.NORMAL,
            entity_object=variation,
            action_url=f"/projects/{variation.project.id}/variations/{variation.id}/",
            action_label="View Variation",
            metadata={
                'variation_id': variation.id,
                'variation_number': variation.number,
                'amount': str(variation.amount),
                'approver': approver.username
            },
            send_email=True
        )
        
        return variation
```

### Valuations Module

```python
# apps/valuations/services.py

from apps.notifications.services import NotificationService

class ValuationService:
    
    @staticmethod
    def certify_claim(claim_id, certifier, certified_amount):
        """Certify claim and notify contractor"""
        claim = Claim.objects.get(id=claim_id)
        claim.status = 'CERTIFIED'
        claim.certified_by = certifier
        claim.certified_amount = certified_amount
        claim.certified_at = timezone.now()
        claim.save()
        
        # Notify contractor
        NotificationService.create_notification(
            user=claim.contractor,
            title=f"Claim {claim.number} Certified",
            message=f"Your claim {claim.number} for £{certified_amount:,.2f} has been certified.",
            notification_type=NotificationType.FINANCIAL,
            priority=NotificationPriority.HIGH,
            entity_object=claim,
            action_url=f"/projects/{claim.project.id}/claims/{claim.id}/",
            action_label="View Claim",
            send_email=True
        )
        
        return claim
```

### Documents Module

```python
# apps/documents/services.py

from apps.notifications.services import NotificationService

class DocumentService:
    
    @staticmethod
    def notify_document_signed(document_id, signer):
        """Notify stakeholders when document is signed"""
        document = Document.objects.get(id=document_id)
        
        # Get stakeholders to notify
        stakeholders = document.get_stakeholders()
        
        for stakeholder in stakeholders:
            NotificationService.create_notification(
                user=stakeholder,
                title=f"Document Signed: {document.name}",
                message=f"{signer.get_full_name()} has signed {document.name}.",
                notification_type=NotificationType.DOCUMENT,
                priority=NotificationPriority.HIGH,
                entity_object=document,
                action_url=f"/documents/{document.id}/",
                action_label="View Document",
                metadata={
                    'document_id': document.id,
                    'signer': signer.username,
                    'signature_timestamp': str(timezone.now())
                },
                send_email=True
            )
```

### Approvals Module

```python
# apps/approvals/services.py

from apps.notifications.services import NotificationService

class ApprovalService:
    
    @staticmethod
    def request_approval(approval_request):
        """Send approval request notification"""
        for approver in approval_request.approvers.all():
            NotificationService.create_notification(
                user=approver,
                title=f"Approval Required: {approval_request.item_type}",
                message=f"{approval_request.requester.get_full_name()} is requesting your approval for {approval_request.item_description}.",
                notification_type=NotificationType.APPROVAL,
                priority=NotificationPriority.HIGH,
                entity_object=approval_request,
                action_url=f"/approvals/{approval_request.id}/",
                action_label="Review & Approve",
                metadata={
                    'approval_id': approval_request.id,
                    'requester': approval_request.requester.username
                },
                send_email=True
            )
    
    @staticmethod
    def notify_approval_decision(approval_request, approver, decision):
        """Notify requester of approval decision"""
        NotificationService.create_notification(
            user=approval_request.requester,
            title=f"Approval {decision}: {approval_request.item_type}",
            message=f"Your approval request for {approval_request.item_description} has been {decision.lower()} by {approver.get_full_name()}.",
            notification_type=NotificationType.WORKFLOW,
            priority=NotificationPriority.NORMAL,
            entity_object=approval_request,
            action_url=f"/approvals/{approval_request.id}/",
            action_label="View Details",
            send_email=True
        )
```

### Reporting Module

```python
# apps/reporting/tasks.py

from apps.notifications.services import NotificationService

@shared_task
def execute_scheduled_report(report_schedule_id):
    """Execute scheduled report and notify user"""
    schedule = ReportSchedule.objects.get(id=report_schedule_id)
    
    # Generate report
    execution = ReportService.generate_report(
        report=schedule.report,
        user=schedule.created_by
    )
    
    if execution.status == 'COMPLETED':
        # Notify user
        NotificationService.create_notification(
            user=schedule.created_by,
            title=f"Report Ready: {schedule.report.name}",
            message=f"Your scheduled report '{schedule.report.name}' has been generated successfully.",
            notification_type=NotificationType.REPORT,
            priority=NotificationPriority.NORMAL,
            entity_object=execution,
            action_url=f"/reports/executions/{execution.id}/download/",
            action_label="Download Report",
            metadata={
                'report_id': schedule.report.id,
                'execution_id': execution.id,
                'file_size': execution.file_size,
                'row_count': execution.row_count
            },
            send_email=True
        )
```

### Subcontracts Module

```python
# apps/subcontracts/services.py

from apps.notifications.services import NotificationService

class SubcontractService:
    
    @staticmethod
    def notify_payment_due(subcontract_payment):
        """Notify about upcoming payment"""
        NotificationService.create_notification(
            user=subcontract_payment.subcontract.manager,
            title=f"Payment Due: {subcontract_payment.subcontract.contractor_name}",
            message=f"Payment of £{subcontract_payment.amount:,.2f} is due on {subcontract_payment.due_date.strftime('%d %b %Y')}.",
            notification_type=NotificationType.FINANCIAL,
            priority=NotificationPriority.HIGH,
            entity_object=subcontract_payment,
            action_url=f"/subcontracts/{subcontract_payment.subcontract.id}/payments/{subcontract_payment.id}/",
            action_label="Process Payment",
            metadata={
                'payment_id': subcontract_payment.id,
                'amount': str(subcontract_payment.amount),
                'due_date': str(subcontract_payment.due_date)
            },
            send_email=True
        )
```

### Procurement Module (LPO)

```python
# apps.procurement.services.py (hypothetical)

from apps.notifications.services import NotificationService

class ProcurementService:
    
    @staticmethod
    def create_lpo(lpo_data, created_by):
        """Create LPO and notify approvers"""
        lpo = LPO.objects.create(**lpo_data)
        
        # Notify approvers
        approvers = lpo.get_required_approvers()
        
        for approver in approvers:
            NotificationService.create_notification(
                user=approver,
                title=f"LPO Awaiting Approval: {lpo.number}",
                message=f"LPO {lpo.number} for {lpo.supplier_name} (£{lpo.amount:,.2f}) requires your approval.",
                notification_type=NotificationType.PROCUREMENT,
                priority=NotificationPriority.NORMAL,
                entity_object=lpo,
                action_url=f"/procurement/lpo/{lpo.id}/",
                action_label="Review LPO",
                send_email=True
            )
        
        return lpo
```

## Using Templates

### 1. Create Template (One-time setup)

```python
from apps.notifications.services import NotificationTemplateService

template = NotificationTemplateService.create_template(
    code='variation_approved',
    name='Variation Approved',
    notification_type='VARIATION',
    priority='NORMAL',
    title_template='Variation {variation_number} Approved',
    message_template='Hello {user_name}, your variation {variation_number} for £{amount} has been approved by {approver_name}.',
    email_subject_template='Variation {variation_number} Approved',
    email_body_template='''
        <h2>Variation Approved</h2>
        <p>Hello {user_name},</p>
        <p>Your variation <strong>{variation_number}</strong> for <strong>£{amount}</strong> has been approved.</p>
        <p><a href="{action_url}">View Variation</a></p>
    ''',
    action_url_template='/projects/{project_id}/variations/{variation_id}/',
    action_label='View Variation',
    variables=['user_name', 'variation_number', 'amount', 'approver_name', 'project_id', 'variation_id']
)
```

### 2. Use Template

```python
# Instead of creating notification manually
NotificationService.create_from_template(
    template_code='variation_approved',
    user=user,
    context={
        'user_name': user.get_full_name(),
        'variation_number': variation.number,
        'amount': f'{variation.amount:,.2f}',
        'approver_name': approver.get_full_name(),
        'project_id': variation.project.id,
        'variation_id': variation.id
    },
    entity_object=variation,
    send_email=True
)
```

## Deadline Reminders

### Scheduled Task for Contract Expiry

```python
# Add to Celery Beat schedule in settings.py

from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'contract-expiry-reminders': {
        'task': 'apps.contracts.tasks.send_contract_expiry_reminders',
        'schedule': crontab(hour=8, minute=0),  # Daily at 8am
    },
}
```

```python
# apps/contracts/tasks.py

from celery import shared_task
from apps.notifications.services import NotificationService
from apps.contracts.models import Contract
from django.utils import timezone
from datetime import timedelta

@shared_task
def send_contract_expiry_reminders():
    """Send reminders for contracts expiring soon"""
    
    # Contracts expiring in 30 days
    thirty_days = timezone.now() + timedelta(days=30)
    expiring_contracts = Contract.objects.filter(
        end_date__lte=thirty_days,
        end_date__gte=timezone.now(),
        status='ACTIVE'
    )
    
    for contract in expiring_contracts:
        days_remaining = (contract.end_date - timezone.now().date()).days
        
        NotificationService.create_notification(
            user=contract.manager,
            title=f"Contract Expiring: {contract.name}",
            message=f"Contract {contract.number} expires in {days_remaining} days on {contract.end_date.strftime('%d %b %Y')}.",
            notification_type=NotificationType.DEADLINE,
            priority=NotificationPriority.HIGH if days_remaining <= 7 else NotificationPriority.NORMAL,
            entity_object=contract,
            action_url=f"/contracts/{contract.id}/",
            action_label="Review Contract",
            metadata={
                'contract_id': contract.id,
                'days_remaining': days_remaining,
                'end_date': str(contract.end_date)
            },
            send_email=True
        )
```

## Bulk Notifications

### Example: System Maintenance Notice

```python
from apps.notifications.services import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

# Get all active users
active_users = User.objects.filter(is_active=True)

# Send to all
NotificationService.create_bulk_notifications(
    users=list(active_users),
    title="Scheduled Maintenance: March 15, 2026",
    message="COMS will undergo scheduled maintenance on March 15 from 2:00 AM to 6:00 AM. The system will be unavailable during this time.",
    notification_type=NotificationType.SYSTEM,
    priority=NotificationPriority.HIGH,
    expires_in_days=7,
    send_email=True
)
```

## Frontend Integration

### Get Unread Count (for Badge)

```javascript
// JavaScript example
fetch('/api/notifications/unread_count/')
    .then(response => response.json())
    .then(data => {
        // Update badge
        document.getElementById('notification-badge').textContent = data.total;
        
        // Update by type
        console.log('Workflow:', data.by_type.WORKFLOW);
        console.log('Financial:', data.by_type.FINANCIAL);
    });
```

### Display Recent Notifications

```javascript
fetch('/api/notifications/recent/?limit=5')
    .then(response => response.json())
    .then(notifications => {
        notifications.forEach(notification => {
            console.log(notification.title);
            console.log(notification.message);
            console.log(notification.action_url);
        });
    });
```

### Mark as Read

```javascript
// Mark single notification as read
fetch(`/api/notifications/${notificationId}/mark_read/`, {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    }
})
.then(response => response.json())
.then(data => console.log(data.message));

// Mark all as read
fetch('/api/notifications/mark_all_read/', {
    method: 'POST',
    headers: {
        'Content-Type': 'application/json',
        'X-CSRFToken': getCookie('csrftoken')
    }
})
.then(response => response.json())
.then(data => console.log(`${data.count} notifications marked as read`));
```

## Testing

### Unit Test Example

```python
# tests/test_notifications.py

from django.test import TestCase
from apps.notifications.services import NotificationService
from apps.notifications.models import Notification
from django.contrib.auth import get_user_model

User = get_user_model()

class NotificationServiceTests(TestCase):
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com'
        )
    
    def test_create_notification(self):
        """Test basic notification creation"""
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test Notification",
            message="This is a test",
            notification_type='SYSTEM'
        )
        
        self.assertIsNotNone(notification.id)
        self.assertEqual(notification.user, self.user)
        self.assertEqual(notification.title, "Test Notification")
        self.assertFalse(notification.is_read)
    
    def test_mark_as_read(self):
        """Test marking notification as read"""
        notification = NotificationService.create_notification(
            user=self.user,
            title="Test",
            message="Test"
        )
        
        success = NotificationService.mark_as_read(notification.id, self.user)
        
        self.assertTrue(success)
        notification.refresh_from_db()
        self.assertTrue(notification.is_read)
        self.assertIsNotNone(notification.read_at)
```

## Best Practices

1. **Always link to entities** - Use `entity_object` parameter
2. **Set appropriate priorities** - URGENT for immediate action required
3. **Include action URLs** - Make notifications actionable
4. **Use templates** for common notifications
5. **Add rich metadata** - Store additional context
6. **Set expiration dates** - Use `expires_in_days` for temporary notifications
7. **Respect user preferences** - Always pass `send_email=True`, the service checks preferences
8. **Use bulk operations** - For multiple users, use `create_bulk_notifications()`

## Configuration

### Add to Django Settings

```python
# config/settings.py

# Email configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'COMS System <noreply@coms.example.com>'

# Celery Beat Schedule
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    'cleanup-old-notifications': {
        'task': 'apps.notifications.tasks.cleanup_old_notifications_task',
        'schedule': crontab(hour=2, minute=0),
        'args': (90,)
    },
    'send-daily-digest': {
        'task': 'apps.notifications.tasks.send_daily_digest_task',
        'schedule': crontab(hour=9, minute=0),
    },
}
```

## Need More Help?

See the comprehensive documentation: [docs/NOTIFICATION_ENGINE.md](NOTIFICATION_ENGINE.md)
