# COMS Event Logging System

## Overview

The COMS Event Logging Module provides comprehensive activity tracking and audit logging across the entire platform. It automatically records user actions, system events, API requests, and entity changes, creating a complete audit trail for compliance, security, and analytics.

### Key Features

- **Comprehensive Event Tracking**: 75+ event types across 15 categories
- **Automatic Logging**: Middleware automatically logs API requests, logins, and logouts
- **Entity Linking**: Events can be linked to any model instance via GenericForeignKey
- **Performance Monitoring**: Tracks request duration and identifies slow API calls
- **Error Tracking**: Automatically logs failed requests and system errors
- **User Activity**: Complete activity history for each user
- **Project-Level Logs**: Aggregate all events within a project context
- **Analytics**: Built-in statistics and performance metrics
- **Immutable Audit Log**: Events cannot be modified once created

---

## Architecture

### 3-Layer Pattern

The Event Logging module follows COMS's standard 3-layer architecture:

```
┌─────────────────────────────────────┐
│         API Layer                   │
│  - SystemEventViewSet               │
│  - 10+ REST endpoints               │
│  - Pagination & filtering           │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│       Service Layer                 │
│  - EventLoggingService              │
│  - Specialized log functions        │
│  - Helper utilities                 │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│      Selector Layer                 │
│  - EventSelector                    │
│  - EventAnalyticsSelector           │
│  - Query optimization               │
└─────────────────────────────────────┘
                ↓
┌─────────────────────────────────────┐
│        Model Layer                  │
│  - SystemEvent                      │
│  - 6 database indexes               │
└─────────────────────────────────────┘
```

### Middleware Integration

```
Request → EventLoggingMiddleware → View → Response
    ↓                                         ↓
    Start timer                          Log event
                                         (with duration)
```

---

## Data Model

### SystemEvent Model

The `SystemEvent` model is the core of the logging system.

| Field | Type | Description |
|-------|------|-------------|
| `id` | UUIDField | Unique event identifier (primary key) |
| `event_type` | CharField | Type of event (75+ choices) |
| `entity_type` | ForeignKey | ContentType of related entity |
| `entity_id` | CharField | ID of related entity |
| `user` | ForeignKey | User who triggered the event |
| `organization` | ForeignKey | Organization context |
| `project` | ForeignKey | Project context (if applicable) |
| `timestamp` | DateTimeField | When the event occurred |
| `metadata` | JSONField | Additional event data |
| `ip_address` | GenericIPAddressField | IP address of request |
| `user_agent` | TextField | User agent string |
| `request_path` | CharField | API request path |
| `request_method` | CharField | HTTP method (GET, POST, etc.) |
| `response_status` | IntegerField | HTTP response status code |
| `duration_ms` | IntegerField | Request duration in milliseconds |

### Event Types (75+ types across 15 categories)

| Category | Event Types |
|----------|-------------|
| **Authentication** | user_login, user_logout, user_created, user_updated, password_changed, password_reset |
| **Organization** | organization_created, organization_updated, organization_deleted |
| **Project** | project_created, project_updated, project_deleted, project_status_changed |
| **Contract** | contract_created, contract_updated, contract_signed, contract_terminated, contract_variation_added |
| **Subcontract** | subcontract_created, subcontract_updated, subcontract_approved, subcontract_rejected |
| **Document** | document_uploaded, document_downloaded, document_viewed, document_shared, document_signed, document_deleted |
| **Variation** | variation_created, variation_submitted, variation_approved, variation_rejected, variation_withdrawn, variation_revised |
| **Claim** | claim_created, claim_submitted, claim_certified, claim_rejected, claim_revised, claim_paid |
| **Payment** | payment_created, payment_recorded, payment_approved, payment_processed, payment_reversed |
| **Approval** | approval_requested, approval_granted, approval_denied, approval_delegated |
| **Report** | report_generated, report_exported, report_scheduled |
| **Procurement** | lpo_created, lpo_approved, lpo_issued, lpo_received |
| **Notification** | notification_sent, notification_read |
| **System** | data_exported, data_imported, backup_created, settings_changed |
| **API** | api_request, api_error |

### Database Indexes

Six optimized indexes for fast queries:

1. `events_timestamp_idx` - Events by timestamp (descending)
2. `events_type_time_idx` - Events by type and timestamp
3. `events_user_time_idx` - Events by user and timestamp
4. `events_project_time_idx` - Events by project and timestamp
5. `events_org_time_idx` - Events by organization and timestamp
6. `events_entity_idx` - Events by entity type and ID

---

## Usage Examples

### Manual Event Logging

#### Example 1: Log a Variation Approval

```python
from apps.events.models import SystemEvent
from apps.events.services import EventLoggingService, get_client_ip

# In your variation service
def approve_variation(variation, user, request):
    # ... approval logic ...
    
    # Log the event
    EventLoggingService.log_variation_event(
        event_type=SystemEvent.VARIATION_APPROVED,
        variation=variation,
        user=user,
        metadata={
            'approved_amount': str(variation.amount),
            'approval_notes': 'Reviewed and approved',
        },
        ip_address=get_client_ip(request)
    )
```

#### Example 2: Log a Document Upload

```python
from apps.events.services import EventLoggingService
from apps.events.models import SystemEvent

def upload_document(document, user, request):
    # ... upload logic ...
    
    # Log the event
    EventLoggingService.log_document_event(
        event_type=SystemEvent.DOCUMENT_UPLOADED,
        document=document,
        user=user,
        metadata={
            'file_size_mb': round(document.file.size / 1024 / 1024, 2),
            'file_type': document.file.content_type,
        },
        ip_address=get_client_ip(request)
    )
```

#### Example 3: Log a Generic Event

```python
from apps.events.services import EventLoggingService
from apps.events.models import SystemEvent

# Log any custom event
event = EventLoggingService.log_event(
    event_type=SystemEvent.PROJECT_STATUS_CHANGED,
    user=request.user,
    organization=project.organization,
    project=project,
    entity=project,  # Link to the project
    metadata={
        'old_status': 'planning',
        'new_status': 'active',
        'changed_by': request.user.get_full_name(),
    },
    ip_address=get_client_ip(request)
)
```

### Automatic Event Logging

The `EventLoggingMiddleware` automatically logs:

1. **User Logins** - Via Django signal
2. **User Logouts** - Via Django signal  
3. **API Requests** - All requests to `/api/*` endpoints

#### Configuration

Add to `config/settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware ...
    'apps.events.middleware.EventLoggingMiddleware',  # Add this
    # ... rest of middleware ...
]
```

The middleware will automatically:
- Log all API requests
- Track request duration
- Log response status codes
- Identify slow requests (> 1000ms)
- Log errors (4xx, 5xx responses)

---

## API Endpoints

### Base URL: `/api/events/`

All endpoints require authentication.

### 1. List All Events

**GET** `/api/events/`

Query Parameters:
- `event_type` - Filter by event type
- `category` - Filter by category
- `user` - Filter by user ID
- `project` - Filter by project ID
- `start_date` - Filter from date (YYYY-MM-DD)
- `end_date` - Filter to date (YYYY-MM-DD)
- `days` - Filter last N days
- `page` - Page number
- `page_size` - Results per page (max 200)

**Example Request:**
```bash
GET /api/events/?category=variation&days=7&page_size=20
```

**Example Response:**
```json
{
  "count": 145,
  "next": "http://api/events/?page=2",
  "previous": null,
  "results": [
    {
      "id": "123e4567-e89b-12d3-a456-426614174000",
      "event_type": "variation_approved",
      "event_type_display": "Variation Approved",
      "category": "variation",
      "user_email": "john@example.com",
      "project_name": "Nairobi Highway Project",
      "timestamp": "2026-03-12T10:30:00Z",
      "time_since": "2 hours",
      "response_status": 200,
      "duration_ms": 145
    }
  ]
}
```

### 2. Get Event Detail

**GET** `/api/events/{id}/`

**Example Response:**
```json
{
  "id": "123e4567-e89b-12d3-a456-426614174000",
  "event_type": "variation_approved",
  "event_type_display": "Variation Approved",
  "category": "variation",
  "user": 42,
  "user_display": {
    "id": 42,
    "email": "john@example.com",
    "full_name": "John Doe"
  },
  "organization": 1,
  "organization_display": {
    "id": 1,
    "name": "ACME Construction"
  },
  "project": 5,
  "project_display": {
    "id": 5,
    "name": "Nairobi Highway Project",
    "code": "NHP-2026"
  },
  "entity_type": 12,
  "entity_id": "456",
  "entity_display": "Variation #VAR-001",
  "timestamp": "2026-03-12T10:30:00Z",
  "time_since": "2 hours",
  "metadata": {
    "variation_number": "VAR-001",
    "amount": "150000.00",
    "status": "approved",
    "title": "Additional Foundation Work"
  },
  "ip_address": "192.168.1.100",
  "user_agent": "Mozilla/5.0...",
  "request_path": "/api/variations/456/approve/",
  "request_method": "POST",
  "response_status": 200,
  "duration_ms": 145
}
```

### 3. Get Recent Events

**GET** `/api/events/recent/`

Query Parameters:
- `hours` - Hours to look back (default: 24)
- `limit` - Max results (default: 50)

**Example Request:**
```bash
GET /api/events/recent/?hours=6&limit=20
```

### 4. Get Project Events

**GET** `/api/events/project/{project_id}/`

Query Parameters:
- `event_types` - Comma-separated event types
- `days` - Days to look back

**Example Request:**
```bash
GET /api/events/project/5/?event_types=variation_created,variation_approved&days=30
```

### 5. Get Entity Events

**GET** `/api/events/entity/{entity_type}/{entity_id}/`

Get all events related to a specific entity.

**Example Request:**
```bash
GET /api/events/entity/variation/VAR-001/
```

**Example Response:**
```json
[
  {
    "id": "...",
    "event_type": "variation_created",
    "event_type_display": "Variation Created",
    "timestamp": "2026-03-01T09:00:00Z",
    "user_display": {...},
    "metadata": {...}
  },
  {
    "id": "...",
    "event_type": "variation_submitted",
    "timestamp": "2026-03-05T14:30:00Z",
    ...
  },
  {
    "id": "...",
    "event_type": "variation_approved",
    "timestamp": "2026-03-12T10:30:00Z",
    ...
  }
]
```

### 6. Get User Activity

**GET** `/api/events/user_activity/`

Get activity log for current user.

Query Parameters:
- `days` - Days to look back
- `limit` - Max results (default: 100)

**Example Request:**
```bash
GET /api/events/user_activity/?days=7&limit=50
```

### 7. Get User Statistics

**GET** `/api/events/user_stats/`

Get activity statistics for current user.

Query Parameters:
- `days` - Days to look back (default: 30)

**Example Response:**
```json
{
  "total_events": 342,
  "events_by_type": [
    {
      "event_type": "document_uploaded",
      "count": 45
    },
    {
      "event_type": "variation_created",
      "count": 23
    }
  ],
  "events_by_category": {
    "document": 67,
    "variation": 45,
    "claim": 32,
    "api": 198
  },
  "period_days": 30
}
```

### 8. Get Project Statistics

**GET** `/api/events/project/{project_id}/stats/`

Query Parameters:
- `days` - Days to look back (default: 30)

**Example Response:**
```json
{
  "total_events": 1523,
  "events_by_type": [...],
  "top_users": [
    {
      "user__first_name": "John",
      "user__last_name": "Doe",
      "user__email": "john@example.com",
      "count": 234
    }
  ],
  "period_days": 30
}
```

### 9. Get System Statistics

**GET** `/api/events/statistics/`

Get system-wide event statistics.

### 10. Get API Performance Stats

**GET** `/api/events/api_performance/`

Query Parameters:
- `days` - Days to look back (default: 7)

**Example Response:**
```json
{
  "total_requests": 15234,
  "average_duration_ms": 142.5,
  "slow_requests": 45,
  "error_requests": 23,
  "error_rate_percent": 0.15,
  "period_days": 7
}
```

### 11. Get Event Types List

**GET** `/api/events/event_types/`

Get list of all available event types and categories.

**Example Response:**
```json
{
  "event_types": [
    {
      "value": "user_login",
      "label": "User Login",
      "category": "authentication"
    },
    ...
  ],
  "categories": [
    "authentication",
    "document",
    "variation",
    ...
  ]
}
```

---

## Integration Examples

### Variation Module Integration

```python
# apps/variations/services.py

from apps.events.models import SystemEvent
from apps.events.services import EventLoggingService, get_client_ip

class VariationService:
    
    @staticmethod
    def create_variation(project, user, data, request=None):
        variation = Variation.objects.create(
            project=project,
            created_by=user,
            **data
        )
        
        # Log the creation
        EventLoggingService.log_variation_event(
            event_type=SystemEvent.VARIATION_CREATED,
            variation=variation,
            user=user,
            metadata={
                'variation_number': variation.variation_number,
                'amount': str(variation.amount),
            },
            ip_address=get_client_ip(request) if request else None
        )
        
        return variation
    
    @staticmethod
    def approve_variation(variation, user, request=None):
        variation.status = 'approved'
        variation.approved_by = user
        variation.approved_at = timezone.now()
        variation.save()
        
        # Log the approval
        EventLoggingService.log_variation_event(
            event_type=SystemEvent.VARIATION_APPROVED,
            variation=variation,
            user=user,
            metadata={
                'variation_number': variation.variation_number,
                'amount': str(variation.amount),
                'approved_by': user.get_full_name(),
            },
            ip_address=get_client_ip(request) if request else None
        )
        
        return variation
```

### Document Module Integration

```python
# apps/documents/services.py

from apps.events.models import SystemEvent
from apps.events.services import EventLoggingService, get_client_ip

class DocumentService:
    
    @staticmethod
    def upload_document(project, user, file, data, request=None):
        document = Document.objects.create(
            project=project,
            uploaded_by=user,
            file=file,
            **data
        )
        
        # Log the upload
        EventLoggingService.log_document_event(
            event_type=SystemEvent.DOCUMENT_UPLOADED,
            document=document,
            user=user,
            metadata={
                'file_name': file.name,
                'file_size_mb': round(file.size / 1024 / 1024, 2),
                'document_type': data.get('document_type'),
            },
            ip_address=get_client_ip(request) if request else None
        )
        
        return document
    
    @staticmethod
    def sign_document(document, user, signature_data, request=None):
        # ... signing logic ...
        
        # Log the signature
        EventLoggingService.log_document_event(
            event_type=SystemEvent.DOCUMENT_SIGNED,
            document=document,
            user=user,
            metadata={
                'signer_name': user.get_full_name(),
                'signature_timestamp': timezone.now().isoformat(),
            },
            ip_address=get_client_ip(request) if request else None
        )
```

### Claim Module Integration

```python
# apps/valuations/services.py

class ValuationService:
    
    @staticmethod
    def certify_claim(claim, user, certified_amount, request=None):
        claim.status = 'certified'
        claim.certified_amount = certified_amount
        claim.certified_by = user
        claim.certified_at = timezone.now()
        claim.save()
        
        # Log the certification
        EventLoggingService.log_claim_event(
            event_type=SystemEvent.CLAIM_CERTIFIED,
            claim=claim,
            user=user,
            metadata={
                'claim_number': claim.claim_number,
                'claimed_amount': str(claim.total_amount),
                'certified_amount': str(certified_amount),
                'certified_by': user.get_full_name(),
            },
            ip_address=get_client_ip(request) if request else None
        )
```

---

## Admin Interface

The admin interface provides a comprehensive view of all system events with:

### Features

1. **Color-Coded Badges**:
   - Event type badges (15 different colors by category)
   - Category badges
   - Status badges (success/error by HTTP status)
   - Performance badges (duration color-coded)

2. **Advanced Filters**:
   - By event category
   - By event type
   - By user
   - By organization
   - By project
   - By response status (2xx, 4xx, 5xx)
   - By date

3. **Search**:
   - Search across event types, users, projects, paths, IP addresses, metadata

4. **Date Hierarchy**: Browse events by year/month/day

5. **Read-Only**: Events cannot be modified (immutable audit log)

### Admin URL

Access at: `/admin/events/systemevent/`

---

## Performance Considerations

### Index Usage

The module uses 6 optimized indexes:

```python
indexes = [
    models.Index(fields=['-timestamp']),  # Most common query
    models.Index(fields=['event_type', '-timestamp']),
    models.Index(fields=['user', '-timestamp']),
    models.Index(fields=['project', '-timestamp']),
    models.Index(fields=['organization', '-timestamp']),
    models.Index(fields=['entity_type', 'entity_id']),
]
```

### Query Optimization

All selector methods use `select_related()` and `prefetch_related()`:

```python
queryset = SystemEvent.objects.select_related(
    'user',
    'organization',
    'project',
    'entity_type'
).all()
```

### Pagination

API endpoints use pagination (50 events per page by default, max 200).

### Cleanup Strategy

Regularly clean up old events to prevent table growth:

```python
from apps.events.services import EventLoggingService

# Delete events older than 365 days
deleted_count = EventLoggingService.cleanup_old_events(days=365)
```

Create a Celery task for automatic cleanup:

```python
# apps/events/tasks.py

from celery import shared_task
from apps.events.services import EventLoggingService

@shared_task
def cleanup_old_events():
    """Delete events older than 1 year"""
    deleted_count = EventLoggingService.cleanup_old_events(days=365)
    return f"Deleted {deleted_count} old events"
```

Schedule in `config/settings.py`:

```python
CELERY_BEAT_SCHEDULE = {
    'cleanup-old-events': {
        'task': 'apps.events.tasks.cleanup_old_events',
        'schedule': crontab(hour=3, minute=0, day_of_month=1),  # 1st of month at 3am
    },
}
```

---

## Security Considerations

### 1. Organization Filtering

Events are filtered by organization for non-superusers:

```python
if not request.user.is_superuser:
    queryset = queryset.filter(
        organization=request.user.organization
    )
```

### 2. Read-Only API

The EventViewSet is read-only. Events can only be created via services or middleware.

### 3. Sensitive Data

Avoid logging sensitive data in metadata:
- ❌ Passwords, tokens, credit card numbers
- ✅ Non-sensitive context, amounts, status changes

### 4. IP Address Logging

IP addresses are logged for security audit purposes. Comply with GDPR/privacy regulations.

---

## Deployment Checklist

### 1. Add to INSTALLED_APPS

```python
# config/settings.py

INSTALLED_APPS = [
    # ... other apps ...
    'apps.events',
]
```

### 2. Add Middleware

```python
# config/settings.py

MIDDLEWARE = [
    # ... other middleware ...
    'apps.events.middleware.EventLoggingMiddleware',
]
```

### 3. Add to URL Configuration

```python
# api/urls.py

from api.views.events import SystemEventViewSet

router.register(r'events', SystemEventViewSet, basename='events')
```

### 4. Run Migrations

```bash
python manage.py makemigrations events
python manage.py migrate events
```

### 5. Test Event Logging

```python
# In Django shell
from apps.events.models import SystemEvent
from apps.events.services import EventLoggingService
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.first()

# Create a test event
event = EventLoggingService.log_event(
    event_type=SystemEvent.USER_LOGIN,
    user=user,
    metadata={'test': True}
)

print(f"Created event: {event}")
```

---

## Troubleshooting

### Events Not Being Logged

1. **Check middleware is installed**:
   ```python
   # In settings.py
   'apps.events.middleware.EventLoggingMiddleware' in MIDDLEWARE
   ```

2. **Check path is included**:
   - Middleware only logs `/api/*` paths by default
   - Modify `INCLUDED_PATHS` in middleware if needed

3. **Check for errors in logs**:
   ```bash
   # Look for "Error logging event" messages
   docker-compose logs web | grep "Error logging"
   ```

### Slow Query Performance

1. **Check indexes exist**:
   ```sql
   \d+ system_events  -- In PostgreSQL
   ```

2. **Use select_related**:
   ```python
   events = SystemEvent.objects.select_related('user', 'project').all()
   ```

3. **Limit results**:
   ```python
   events = SystemEvent.objects.all()[:100]
   ```

### Database Table Growing Too Large

1. **Set up cleanup task** (see Performance section above)

2. **Manually clean old events**:
   ```python
   from apps.events.services import EventLoggingService
   deleted = EventLoggingService.cleanup_old_events(days=180)
   ```

---

## Best Practices

1. **Always log significant actions**: Create, update, delete, approvals, certifications
2. **Use specialized log functions**: `log_variation_event()`, `log_document_event()`, etc.
3. **Include relevant metadata**: Add context that will be useful for audit/debugging
4. **Link entities**: Always pass the `entity` parameter to link events to specific records
5. **Capture IP addresses**: Use `get_client_ip(request)` for security audit
6. **Regular cleanup**: Schedule periodic cleanup of old events
7. **Monitor performance**: Use API performance stats to identify slow endpoints
8. **Respect privacy**: Don't log sensitive personal data in metadata

---

## Future Enhancements

- Real-time event streaming (WebSocket support)
- Event replay/rollback capabilities
- Advanced analytics dashboard
- Machine learning for anomaly detection
- Export to external SIEM systems
- Retention policies by event type
- Event archiving to cold storage

---

## Summary

The Event Logging module provides:

- ✅ **75+ event types** across 15 categories
- ✅ **Automatic logging** via middleware
- ✅ **Entity linking** with GenericForeignKey
- ✅ **Performance tracking** (request duration)
- ✅ **10+ API endpoints** for querying events
- ✅ **Analytics** (user activity, project stats, API performance)
- ✅ **Admin interface** with advanced filters
- ✅ **6 database indexes** for fast queries
- ✅ **Immutable audit log** for compliance
- ✅ **Production-ready** with cleanup and security features

The module is fully integrated with COMS's 3-layer architecture and follows Django best practices.
