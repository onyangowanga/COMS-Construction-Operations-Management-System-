# COMS Notification Engine

Comprehensive notification system for COMS (Construction Operations Management System).

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [API Reference](#api-reference)
5. [Integration Examples](#integration-examples)
6. [Notification Templates](#notification-templates)
7. [Celery Tasks](#celery-tasks)
8. [Deployment](#deployment)
9. [Admin Interface](#admin-interface)

---

## Overview

The Notification Engine provides multi-channel notification delivery across all COMS modules:

### Features

- **Multi-Channel Delivery**
  - In-app notifications
  - Email notifications
  - SMS notifications
  
- **User Preferences**
  - Channel-specific settings (email, in-app, SMS)
  - Notification type filters
  - Quiet hours
  - Daily digest option
  
- **Template System**
  - Reusable notification templates
  - Variable substitution
  - Multi-channel content
  
- **Async Delivery**
  - Celery-powered background tasks
  - Batch notifications
  - Retry mechanisms
  
- **Rich Metadata**
  - Entity linking via GenericForeignKey
  - Priority levels
  - Expiration dates
  - Action URLs

### Notification Types

| Type | Description | Use Cases |
|------|-------------|-----------|
| SYSTEM | System-level notifications | Maintenance, updates |
| WORKFLOW | Workflow events | Approvals, status changes |
| FINANCIAL | Financial alerts | Budget warnings, payment due |
| DOCUMENT | Document activity | Signatures, uploads |
| REPORT | Report generation | Report ready for download |
| DEADLINE | Deadline reminders | Contract expiry, claim deadlines |
| APPROVAL | Approval requests | Variation approval, claim certification |
| VARIATION | Variation updates | New variation, status change |
| CONTRACT | Contract events | Contract signed, milestone reached |
| PROCUREMENT | Procurement activity | LPO created, invoice received |

### Priority Levels

| Priority | Description | Behavior |
|----------|-------------|----------|
| LOW | Low priority | Standard delivery |
| NORMAL | Normal priority (default) | Standard delivery |
| HIGH | High priority | Highlighted in UI |
| URGENT | Urgent | Push notifications, highlighted |

---

## Architecture

### Module Structure

```
apps/notifications/
├── __init__.py
├── apps.py
├── models.py            # Data models
├── selectors.py         # Data retrieval layer
├── services.py          # Business logic layer
├── tasks.py             # Celery async tasks
└── admin.py             # Django admin interface

api/
├── serializers/
│   └── notifications.py # REST serializers
└── views/
    └── notifications.py # REST API views

docs/
└── NOTIFICATION_ENGINE.md
```

### 3-Layer Architecture (COMS Pattern)

```
┌─────────────────────────────────────┐
│         API Views Layer             │
│  - REST endpoints                   │
│  - Request validation               │
│  - Response formatting              │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│       Services Layer                │
│  - Business logic                   │
│  - Notification creation            │
│  - Multi-channel delivery           │
│  - Template rendering               │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│       Selectors Layer               │
│  - Data retrieval                   │
│  - Query optimization               │
│  - Filtering & search               │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│         Models Layer                │
│  - Notification                     │
│  - NotificationPreference           │
│  - NotificationTemplate             │
│  - NotificationBatch                │
└─────────────────────────────────────┘
```

### Integration Flow

```
Module Event
    ↓
Service creates notification
    ↓
Check user preferences
    ↓
┌─────────────────────────────────────┐
│ In-App: Save to database            │
│ Email: Queue Celery task            │
│ SMS: Queue Celery task              │
└─────────────────────────────────────┘
    ↓
Celery workers deliver
    ↓
Update delivery status
```

---

## Data Models

### Notification

Core notification model with multi-channel tracking.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| user | ForeignKey | Recipient user |
| title | CharField(200) | Notification title |
| message | TextField | Notification message |
| notification_type | CharField | Type of notification |
| priority | CharField | Priority level |
| entity_type | ForeignKey(ContentType) | Related entity type |
| entity_id | CharField | Related entity ID |
| is_read | BooleanField | Read status |
| read_at | DateTimeField | When read |
| email_sent | BooleanField | Email delivery status |
| email_sent_at | DateTimeField | Email sent time |
| sms_sent | BooleanField | SMS delivery status |
| sms_sent_at | DateTimeField | SMS sent time |
| metadata | JSONField | Additional data |
| action_url | CharField | Action button URL |
| action_label | CharField | Action button label |
| expires_at | DateTimeField | Expiration date |
| created_at | DateTimeField | Creation timestamp |
| updated_at | DateTimeField | Update timestamp |

**Properties:**

- `is_expired` - Check if notification expired
- `age_in_days` - Age in days
- `is_urgent` - Check if urgent priority

**Methods:**

- `mark_as_read()` - Mark as read
- `mark_as_unread()` - Mark as unread

**Indexes:**

```python
# Optimized for common queries
- user, -created_at
- user, is_read
- notification_type
- entity_type, entity_id
- expires_at
```

### NotificationPreference

User preferences for notification delivery.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| user | OneToOneField | User |
| email_enabled | BooleanField | Receive emails |
| in_app_enabled | BooleanField | Receive in-app |
| sms_enabled | BooleanField | Receive SMS |
| system_notifications | BooleanField | System notifications |
| workflow_notifications | BooleanField | Workflow notifications |
| financial_notifications | BooleanField | Financial notifications |
| document_notifications | BooleanField | Document notifications |
| report_notifications | BooleanField | Report notifications |
| deadline_notifications | BooleanField | Deadline notifications |
| approval_notifications | BooleanField | Approval notifications |
| digest_enabled | BooleanField | Daily digest |
| digest_time | TimeField | Digest delivery time |
| quiet_hours_enabled | BooleanField | Quiet hours enabled |
| quiet_hours_start | TimeField | Quiet hours start |
| quiet_hours_end | TimeField | Quiet hours end |
| sms_phone_number | CharField | SMS phone number |

**Methods:**

- `is_type_enabled(notification_type)` - Check if type enabled
- `is_in_quiet_hours()` - Check if in quiet hours

### NotificationTemplate

Reusable templates for common notifications.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| code | CharField(100) | Unique template code |
| name | CharField(200) | Template name |
| description | TextField | Description |
| notification_type | CharField | Type |
| priority | CharField | Default priority |
| title_template | CharField | Title with variables |
| message_template | TextField | Message with variables |
| email_subject_template | CharField | Email subject |
| email_body_template | TextField | Email body (HTML) |
| sms_template | CharField(160) | SMS message |
| action_url_template | CharField | Action URL template |
| action_label | CharField | Action button label |
| is_active | BooleanField | Active status |
| variables | JSONField | Required variables |

**Methods:**

- `render(context)` - Render template with context
- `validate_context(context)` - Validate required variables

**Template Syntax:**

```python
title_template = "Variation {variation_number} Approved"
message_template = "Hello {user_name}, your variation {variation_number} for £{amount} has been approved."

context = {
    'user_name': 'John Smith',
    'variation_number': 'VAR-001',
    'amount': '25000.00'
}

# Renders to:
# Title: "Variation VAR-001 Approved"
# Message: "Hello John Smith, your variation VAR-001 for £25000.00 has been approved."
```

### NotificationBatch

Batch notification tracking.

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| id | UUID | Primary key |
| name | CharField | Batch name |
| template | ForeignKey | Template used |
| total_recipients | PositiveIntegerField | Total recipients |
| sent_count | PositiveIntegerField | Successfully sent |
| failed_count | PositiveIntegerField | Failed |
| status | CharField | Batch status |
| created_by | ForeignKey(User) | Creator |
| created_at | DateTimeField | Created timestamp |
| completed_at | DateTimeField | Completed timestamp |

**Properties:**

- `success_rate` - Success percentage
- `is_complete` - Check if complete

---

## API Reference

### Base URL

```
/api/notifications/
```

### Authentication

All endpoints require authentication using Django's session authentication or token authentication.

### Endpoints

#### 1. List Notifications

Get user's notifications with optional filtering.

**Endpoint:** `GET /api/notifications/`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by notification type |
| priority | string | Filter by priority |
| is_read | boolean | Filter by read status |
| days | integer | Last N days |
| search | string | Search in title/message |
| page | integer | Page number |
| page_size | integer | Items per page (max 100) |

**Example Request:**

```bash
GET /api/notifications/?is_read=false&type=APPROVAL&page=1&page_size=20
```

**Example Response:**

```json
{
  "count": 45,
  "next": "/api/notifications/?page=2",
  "previous": null,
  "results": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Variation VAR-001 Approved",
      "notification_type": "VARIATION",
      "type_display": "Variation Update",
      "priority": "NORMAL",
      "priority_display": "Normal Priority",
      "is_read": false,
      "created_at": "2026-03-12T10:30:00Z",
      "action_url": "/projects/123/variations/1/",
      "action_label": "View Variation"
    }
  ]
}
```

#### 2. Get Unread Notifications

Get user's unread notifications.

**Endpoint:** `GET /api/notifications/unread/`

**Example Request:**

```bash
GET /api/notifications/unread/
```

#### 3. Get Recent Notifications

Get most recent notifications.

**Endpoint:** `GET /api/notifications/recent/`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| limit | integer | Number of notifications (default: 10) |

**Example Request:**

```bash
GET /api/notifications/recent/?limit=5
```

#### 4. Get Unread Count

Get count of unread notifications by type.

**Endpoint:** `GET /api/notifications/unread_count/`

**Example Response:**

```json
{
  "total": 12,
  "by_type": {
    "WORKFLOW": 5,
    "FINANCIAL": 3,
    "APPROVAL": 4
  }
}
```

#### 5. Get Notification Details

Get specific notification.

**Endpoint:** `GET /api/notifications/{id}/`

**Example Response:**

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "user": 1,
  "user_display": "John Smith",
  "title": "Claim CLAIM-001 Certified",
  "message": "Your claim CLAIM-001 for £15,000 has been certified by the client.",
  "notification_type": "FINANCIAL",
  "type_display": "Financial Alert",
  "priority": "HIGH",
  "priority_display": "High Priority",
  "entity_type": 10,
  "entity_id": "1",
  "is_read": false,
  "read_at": null,
  "email_sent": true,
  "email_sent_at": "2026-03-12T10:31:00Z",
  "sms_sent": false,
  "sms_sent_at": null,
  "metadata": {
    "claim_number": "CLAIM-001",
    "amount": "15000.00"
  },
  "action_url": "/projects/123/claims/1/",
  "action_label": "View Claim",
  "created_at": "2026-03-12T10:30:00Z",
  "updated_at": "2026-03-12T10:30:00Z",
  "expires_at": null,
  "age_in_days": 0,
  "is_urgent": false,
  "is_expired": false
}
```

#### 6. Create Notification

Create a new notification.

**Endpoint:** `POST /api/notifications/`

**Request Body:**

```json
{
  "user_id": 1,
  "title": "New Document Available",
  "message": "A new contract document has been uploaded for your review.",
  "notification_type": "DOCUMENT",
  "priority": "NORMAL",
  "action_url": "/documents/123/",
  "action_label": "View Document",
  "metadata": {
    "document_id": 123,
    "document_name": "Contract Amendment.pdf"
  },
  "send_email": true,
  "send_sms": false
}
```

**Example Response:**

```json
{
  "id": "660f9511-f3ac-52e5-b827-557766551111",
  "title": "New Document Available",
  "notification_type": "DOCUMENT",
  "is_read": false,
  "created_at": "2026-03-12T11:00:00Z"
}
```

#### 7. Create Bulk Notifications

Create notifications for multiple users.

**Endpoint:** `POST /api/notifications/`

**Request Body:**

```json
{
  "user_ids": [1, 2, 3, 4, 5],
  "title": "System Maintenance Notice",
  "message": "COMS will be undergoing maintenance on Saturday from 2am-6am.",
  "notification_type": "SYSTEM",
  "priority": "HIGH",
  "expires_in_days": 7,
  "send_email": true
}
```

**Example Response:**

```json
{
  "message": "Created 5 notifications",
  "count": 5
}
```

#### 8. Mark Notification as Read

Mark a notification as read.

**Endpoint:** `POST /api/notifications/{id}/mark_read/`

**Example Response:**

```json
{
  "message": "Notification marked as read"
}
```

#### 9. Mark All as Read

Mark all user's notifications as read.

**Endpoint:** `POST /api/notifications/mark_all_read/`

**Example Response:**

```json
{
  "message": "Marked 12 notifications as read",
  "count": 12
}
```

#### 10. Mark Multiple as Read

Mark multiple notifications as read.

**Endpoint:** `POST /api/notifications/mark_multiple_read/`

**Request Body:**

```json
{
  "notification_ids": [
    "550e8400-e29b-41d4-a716-446655440000",
    "660f9511-f3ac-52e5-b827-557766551111"
  ]
}
```

**Example Response:**

```json
{
  "message": "Marked 2 notifications as read",
  "count": 2
}
```

#### 11. Delete Notification

Delete a notification.

**Endpoint:** `DELETE /api/notifications/{id}/`

**Example Response:**

```
204 No Content
```

#### 12. Get Statistics

Get notification statistics for the user.

**Endpoint:** `GET /api/notifications/stats/`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| days | integer | Analysis period (default: 30) |

**Example Response:**

```json
{
  "total": 156,
  "unread": 12,
  "urgent": 3,
  "read_rate": 92.3,
  "by_type": {
    "WORKFLOW": 45,
    "FINANCIAL": 30,
    "DOCUMENT": 25,
    "APPROVAL": 20,
    "SYSTEM": 15,
    "VARIATION": 12,
    "REPORT": 9
  }
}
```

### Notification Preferences API

#### 1. Get User Preferences

**Endpoint:** `GET /api/notifications/preferences/`

**Example Response:**

```json
{
  "id": 1,
  "user": 1,
  "user_display": "John Smith",
  "email_enabled": true,
  "in_app_enabled": true,
  "sms_enabled": false,
  "system_notifications": true,
  "workflow_notifications": true,
  "financial_notifications": true,
  "document_notifications": true,
  "report_notifications": true,
  "deadline_notifications": true,
  "approval_notifications": true,
  "digest_enabled": false,
  "digest_time": null,
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "08:00:00",
  "sms_phone_number": null,
  "created_at": "2026-01-01T00:00:00Z",
  "updated_at": "2026-03-12T11:00:00Z"
}
```

#### 2. Update Preferences

**Endpoint:** `PUT /api/notifications/preferences/`

**Request Body:**

```json
{
  "email_enabled": true,
  "sms_enabled": true,
  "sms_phone_number": "+447700900123",
  "quiet_hours_enabled": true,
  "quiet_hours_start": "22:00:00",
  "quiet_hours_end": "07:00:00",
  "digest_enabled": true,
  "digest_time": "09:00:00"
}
```

#### 3. Enable Channel

**Endpoint:** `POST /api/notifications/preferences/enable_channel/`

**Request Body:**

```json
{
  "channel": "email"
}
```

#### 4. Disable Channel

**Endpoint:** `POST /api/notifications/preferences/disable_channel/`

**Request Body:**

```json
{
  "channel": "sms"
}
```

### Notification Templates API

#### 1. List Templates

**Endpoint:** `GET /api/notifications/templates/`

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| type | string | Filter by notification type |
| search | string | Search templates |

#### 2. Get Template Details

**Endpoint:** `GET /api/notifications/templates/{id}/`

### Notification Batches API

#### 1. Create Batch

**Endpoint:** `POST /api/notifications/batches/`

**Request Body:**

```json
{
  "name": "Contract Expiry Reminders - March 2026",
  "template_code": "contract_expiring",
  "user_ids": [1, 2, 3, 4, 5],
  "context": {
    "month": "March",
    "year": "2026"
  },
  "send_email": true,
  "send_sms": false
}
```

#### 2. List Batches

**Endpoint:** `GET /api/notifications/batches/`

#### 3. Get Batch Status

**Endpoint:** `GET /api/notifications/batches/{id}/`

---

## Integration Examples

### Example 1: Variation Approved Notification

```python
from apps.notifications.services import NotificationService
from apps.variations.models import Variation

def approve_variation(variation_id, approver):
    """Approve variation and send notification"""
    variation = Variation.objects.get(id=variation_id)
    variation.status = 'APPROVED'
    variation.approved_by = approver
    variation.save()
    
    # Create notification
    NotificationService.create_notification(
        user=variation.created_by,
        title=f"Variation {variation.number} Approved",
        message=f"Your variation {variation.number} for £{variation.amount:,.2f} has been approved by {approver.get_full_name()}.",
        notification_type='VARIATION',
        priority='NORMAL',
        entity_object=variation,
        action_url=f"/projects/{variation.project.id}/variations/{variation.id}/",
        action_label="View Variation",
        metadata={
            'variation_id': variation.id,
            'variation_number': variation.number,
            'amount': str(variation.amount)
        },
        send_email=True
    )
```

### Example 2: Using Templates

```python
from apps.notifications.services import NotificationService

# Create notification from template
NotificationService.create_from_template(
    template_code='claim_certified',
    user=claim.contractor,
    context={
        'user_name': claim.contractor.get_full_name(),
        'claim_number': claim.number,
        'amount': f'{claim.certified_amount:,.2f}',
        'project_name': claim.project.name
    },
    entity_object=claim,
    send_email=True,
    send_sms=False
)
```

### Example 3: Bulk Notifications

```python
from apps.notifications.services import NotificationService
from django.contrib.auth import get_user_model

User = get_user_model()

# Get all project managers
project_managers = User.objects.filter(role='PM')

# Send system notification to all PMs
NotificationService.create_bulk_notifications(
    users=list(project_managers),
    title="New Feature: Cashflow Forecasting",
    message="A new cashflow forecasting module is now available in COMS. Check it out!",
    notification_type='SYSTEM',
    priority='NORMAL',
    action_url="/cashflow/",
    action_label="Try It Now",
    expires_in_days=30,
    send_email=True
)
```

### Example 4: Document Signed Notification

```python
from apps.notifications.services import NotificationService
from apps.documents.models import Document

def notify_document_signed(document_id, signer):
    """Notify stakeholders when document is signed"""
    document = Document.objects.get(id=document_id)
    
    # Notify document creator
    NotificationService.create_notification(
        user=document.created_by,
        title=f"Document Signed: {document.name}",
        message=f"{signer.get_full_name()} has signed {document.name}.",
        notification_type='DOCUMENT',
        priority='HIGH',
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

### Example 5: Deadline Reminders

```python
from apps.notifications.services import NotificationService
from apps.contracts.models import Contract
from django.utils import timezone
from datetime import timedelta

def send_contract_expiry_reminders():
    """Send reminders for contracts expiring in 30 days"""
    thirty_days_from_now = timezone.now() + timedelta(days=30)
    
    expiring_contracts = Contract.objects.filter(
        end_date__lte=thirty_days_from_now,
        end_date__gte=timezone.now(),
        status='ACTIVE'
    )
    
    for contract in expiring_contracts:
        NotificationService.create_notification(
            user=contract.manager,
            title=f"Contract Expiring: {contract.name}",
            message=f"Contract {contract.number} expires on {contract.end_date.strftime('%d %b %Y')} (30 days).",
            notification_type='DEADLINE',
            priority='HIGH',
            entity_object=contract,
            action_url=f"/contracts/{contract.id}/",
            action_label="Review Contract",
            send_email=True
        )
```

---

## Notification Templates

### Creating Templates

Templates can be created via Django admin or programmatically:

```python
from apps.notifications.services import NotificationTemplateService

template = NotificationTemplateService.create_template(
    code='variation_approved',
    name='Variation Approved',
    description='Notification sent when a variation is approved',
    notification_type='VARIATION',
    priority='NORMAL',
    title_template='Variation {variation_number} Approved',
    message_template='Hello {user_name}, your variation {variation_number} for £{amount} has been approved by {approver_name}.',
    email_subject_template='Variation {variation_number} Approved',
    email_body_template='''
        <h2>Variation Approved</h2>
        <p>Hello {user_name},</p>
        <p>Your variation <strong>{variation_number}</strong> for <strong>£{amount}</strong> has been approved by {approver_name}.</p>
        <p><a href="{action_url}">View Variation</a></p>
    ''',
    sms_template='Variation {variation_number} for £{amount} approved',
    action_url_template='/projects/{project_id}/variations/{variation_id}/',
    action_label='View Variation',
    variables=['user_name', 'variation_number', 'amount', 'approver_name', 'project_id', 'variation_id']
)
```

### Pre-configured Templates

| Code | Name | Type | Variables |
|------|------|------|-----------|
| variation_approved | Variation Approved | VARIATION | user_name, variation_number, amount, approver_name |
| claim_certified | Claim Certified | FINANCIAL | user_name, claim_number, amount, project_name |
| document_signed | Document Signed | DOCUMENT | user_name, document_name, signer_name |
| report_generated | Report Generated | REPORT | user_name, report_name, report_type |
| contract_expiring | Contract Expiring Soon | DEADLINE | user_name, contract_number, days_remaining, end_date |
| approval_request | Approval Request | APPROVAL | user_name, item_type, item_number, requester_name |
| payment_due | Payment Due | FINANCIAL | user_name, invoice_number, amount, due_date |
| lpo_created | LPO Created | PROCUREMENT | user_name, lpo_number, supplier_name, amount |

---

## Celery Tasks

### Task Configuration

Add to `config/settings.py`:

```python
# Celery Beat Schedule
from celery.schedules import crontab

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
```

### Available Tasks

| Task | Description | Schedule |
|------|-------------|----------|
| send_email_task | Send email notification | On-demand |
| send_sms_task | Send SMS notification | On-demand |
| send_batch_notifications_task | Process batch notifications | On-demand |
| cleanup_old_notifications_task | Delete old read notifications | Daily at 2am |
| cleanup_expired_notifications_task | Delete expired notifications | Daily at 3am |
| send_daily_digest_task | Send daily digests | Daily at 9am |
| send_deadline_reminders_task | Send deadline reminders | Daily at 8am |
| process_pending_batches_task | Process pending batches | Every 30min |

### Manual Task Invocation

```python
from apps.notifications.tasks import send_email_task

# Send email asynchronously
send_email_task.delay('notification-uuid-here')
```

---

## Deployment

### 1. Add to INSTALLED_APPS

```python
# config/settings.py

INSTALLED_APPS = [
    ...
    'apps.notifications',
    ...
]
```

### 2. Configure URLs

```python
# config/urls.py

from rest_framework.routers import DefaultRouter
from api.views.notifications import (
    NotificationViewSet,
    NotificationPreferenceViewSet,
    NotificationTemplateViewSet,
    NotificationBatchViewSet
)

router = DefaultRouter()
router.register(r'notifications', NotificationViewSet, basename='notification')
router.register(r'notifications/preferences', NotificationPreferenceViewSet, basename='notification-preference')
router.register(r'notifications/templates', NotificationTemplateViewSet, basename='notification-template')
router.register(r'notifications/batches', NotificationBatchViewSet, basename='notification-batch')

urlpatterns = [
    ...
    path('api/', include(router.urls)),
    ...
]
```

### 3. Run Migrations

```bash
python manage.py makemigrations notifications
python manage.py migrate notifications
```

### 4. Create Default Templates

```python
python manage.py shell

from apps.notifications.services import NotificationTemplateService

# Create default templates
templates = [
    {
        'code': 'variation_approved',
        'name': 'Variation Approved',
        'notification_type': 'VARIATION',
        'title_template': 'Variation {variation_number} Approved',
        'message_template': 'Your variation {variation_number} for £{amount} has been approved.',
        'variables': ['variation_number', 'amount']
    },
    # Add more templates...
]

for template_data in templates:
    NotificationTemplateService.create_template(**template_data)
```

### 5. Configure Email Settings

```python
# config/settings.py

EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = 'COMS System <noreply@coms.example.com>'
```

### 6. Configure SMS (Optional)

For SMS delivery, integrate with a provider like Twilio:

```python
# config/settings.py

TWILIO_ACCOUNT_SID = env('TWILIO_ACCOUNT_SID')
TWILIO_AUTH_TOKEN = env('TWILIO_AUTH_TOKEN')
TWILIO_PHONE_NUMBER = env('TWILIO_PHONE_NUMBER')
```

Update `apps/notifications/services.py`:

```python
from twilio.rest import Client

def send_sms_notification(notification):
    # ... existing code ...
    
    client = Client(settings.TWILIO_ACCOUNT_SID, settings.TWILIO_AUTH_TOKEN)
    
    message = client.messages.create(
        body=sms_body,
        from_=settings.TWILIO_PHONE_NUMBER,
        to=preferences.sms_phone_number
    )
    
    # ... update notification ...
```

### 7. Start Celery Workers

```bash
# Start Celery worker
celery -A config worker -l info

# Start Celery beat scheduler
celery -A config beat -l info
```

---

## Admin Interface

The notification engine includes a comprehensive Django admin interface.

### Features

- **Color-coded badges** for types, priorities, and status
- **Advanced filtering** by type, priority, read status, user
- **Bulk actions** (mark as read, send email/SMS, delete)
- **Search** across titles, messages, users
- **Date hierarchy** for created_at
- **Progress bars** for batches
- **Statistics display**

### Access

```
/admin/notifications/
```

### Available Sections

1. **Notifications** - View and manage all notifications
2. **Preferences** - User notification preferences
3. **Templates** - Notification templates
4. **Batches** - Batch notification tracking

---

## Best Practices

### 1. Use Templates for Common Notifications

```python
# Instead of:
NotificationService.create_notification(
    user=user,
    title=f"Variation {var.number} Approved",
    message=f"Your variation {var.number} has been approved",
    ...
)

# Use:
NotificationService.create_from_template(
    template_code='variation_approved',
    user=user,
    context={'variation_number': var.number, ...}
)
```

### 2. Link to Entities

```python
NotificationService.create_notification(
    user=user,
    title="Document Updated",
    message="Your document has been updated",
    entity_object=document,  # ← Link to document
    action_url=f"/documents/{document.id}/"
)
```

### 3. Set Appropriate Priorities

```python
# Urgent: Requires immediate action
priority='URGENT'  # Contract expiring today

# High: Important but not urgent
priority='HIGH'    # Payment due soon

# Normal: Standard notifications
priority='NORMAL'  # Status update

# Low: FYI notifications
priority='LOW'     # System update
```

### 4. Respect User Preferences

The service layer automatically checks preferences before sending emails/SMS. Always pass `send_email=True` to enable email delivery - it will only send if the user has opted in.

### 5. Use Expiration Dates

```python
NotificationService.create_notification(
    ...,
    expires_in_days=30  # Auto-cleanup after 30 days
)
```

### 6. Add Rich Metadata

```python
metadata={
    'claim_id': claim.id,
    'claim_number': claim.number,
    'amount': str(claim.amount),
    'project_name': claim.project.name,
    'certification_date': str(claim.certified_at)
}
```

---

## Troubleshooting

### Notifications Not Appearing

1. Check user preferences: `GET /api/notifications/preferences/`
2. Verify notification created: Check Django admin
3. Check filters in API call

### Emails Not Sending

1. Verify email settings in `settings.py`
2. Check Celery worker is running
3. Check Celery logs for errors
4. Verify user has email address
5. Check user preferences (email_enabled)

### SMS Not Sending

1. Verify SMS provider configuration
2. Check user has phone number in preferences
3. Verify SMS provider credentials
4. Check Celery worker logs

### Slow Notification Queries

1. Ensure database indexes are created (run migrations)
2. Use list serializer for list views (lighter)
3. Add pagination
4. Filter by date range

---

## Performance Considerations

### Database Indexes

All critical queries are indexed:

```sql
-- Most common: Get user notifications
CREATE INDEX idx_notifications_user_created ON notifications(user_id, created_at DESC);

-- Filter unread
CREATE INDEX idx_notifications_user_read ON notifications(user_id, is_read);

-- Type filtering
CREATE INDEX idx_notifications_type ON notifications(notification_type);

-- Cleanup queries
CREATE INDEX idx_notifications_expires ON notifications(expires_at);
```

### Query Optimization

All selectors use `select_related()` and `prefetch_related()`:

```python
Notification.objects.select_related(
    'user',
    'entity_type'
).filter(user=user)
```

### Caching

Consider adding Redis caching for unread counts:

```python
from django.core.cache import cache

def get_unread_count_cached(user):
    cache_key = f'unread_count_{user.id}'
    count = cache.get(cache_key)
    
    if count is None:
        count = NotificationSelector.get_unread_count(user)
        cache.set(cache_key, count, timeout=300)  # 5 minutes
    
    return count
```

---

## Security

### Access Control

- Users can only access their own notifications
- Admin users can access all notifications via Django admin
- Bulk operations respect user ownership

### Data Privacy

- Email/SMS content is not logged
- Phone numbers are stored securely
- Metadata should not contain sensitive passwords/tokens

---

## Future Enhancements

1. **WebSocket Support** - Real-time in-app notifications
2. **Push Notifications** - Mobile app integration
3. **Notification Groups** - Group related notifications
4. **Read Receipts** - Track when notifications are seen
5. **Rich Media** - Support for images, attachments
6. **Notification Routing** - Custom routing rules per user
7. **A/B Testing** - Test different notification templates
8. **Analytics Dashboard** - Notification delivery analytics

---

## Support

For questions or issues with the notification engine:

1. Check this documentation
2. Review Django admin logs
3. Check Celery worker logs
4. Contact the development team

---

**Last Updated:** March 12, 2026  
**Version:** 1.0.0  
**Module:** apps.notifications
