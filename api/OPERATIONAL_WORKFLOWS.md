# Operational Workflow Layer

## Overview

The Operational Workflow Layer provides automated business process management for the Construction Operations Management System (COMS). This layer implements workflow automation, approval chains, budget control, and activity tracking.

## Architecture

```
┌──────────────────┐
│  API Endpoints   │  ← REST API actions
└────────┬─────────┘
         │
    ┌────┴────┐
    │         │
┌───▼────┐  ┌▼─────────┐
│Services│  │ Signals  │  ← Business logic & automation
└───┬────┘  └──┬───────┘
    │          │
┌───▼──────────▼───┐
│     Models       │  ← Data layer
│  - Approval      │
│  - ProjectActivity│
└──────────────────┘
```

## Components

### 1. Models

#### Approval Model
Manages approval workflows for expenses, payments, and LPOs.

**Fields:**
- `approval_type`: EXPENSE, SUPPLIER_PAYMENT, CONSULTANT_PAYMENT, LPO, BUDGET_OVERRIDE
- `status`: PENDING, APPROVED, REJECTED
- `amount`: Amount requiring approval
- `requested_by`: User who requested approval
- `approved_by`: User who approved/rejected
- `reason`: Reason for approval request

#### ProjectActivity Model
Tracks all project events for audit trail and timeline.

**Fields:**
- `project_id`: Associated project
- `activity_type`: Type of activity (EXPENSE_CREATED, LPO_ISSUED, etc.)
- `description`: Human-readable description
- `amount`: Monetary amount if applicable
- `performed_by`: User who performed the action
- `metadata`: Additional JSON metadata

### 2. Services

#### Budget Control Service (`api/services/budget_control.py`)

**Functions:**
- `check_budget_overrun(expense, bq_item_id)` - Validates expense against BQ budget
- `validate_expense_budget(expense, allocations)` - Validates against multiple BQ items

**Returns:**
```python
{
    'is_overrun': bool,
    'budget': Decimal,
    'allocated': Decimal,
    'new_total': Decimal,
    'variance': Decimal,
    'message': str
}
```

#### Procurement Workflow Service (`api/services/procurement_workflow.py`)

**LPO Lifecycle:** DRAFT → APPROVED → DELIVERED → INVOICED → PAID

**Functions:**
- `approve_lpo(lpo, approved_by)` - Approve draft LPO
- `mark_lpo_delivered(lpo, delivered_by)` - Mark as delivered
- `mark_lpo_invoiced(lpo, invoiced_by, invoice_number)` - Mark as invoiced
- `mark_lpo_paid(lpo, paid_by, payment_reference)` - Mark as paid

#### Approval Workflow Service (`api/services/approval_workflow.py`)

**Functions:**
- `create_approval_request(...)` - Create approval request
- `approve_request(approval, approved_by, notes)` - Approve request
- `reject_request(approval, rejected_by, reason)` - Reject request
- `get_pending_approvals(user, approval_type)` - Get pending approvals

#### Notification Service (`api/services/notification_service.py`)

**Functions:**
- `check_budget_overruns(project_id)` - Check for budget overruns
- `check_unpaid_supplier_invoices(days_overdue)` - Check overdue invoices
- `check_expiring_approvals(days_ahead)` - Check expiring approvals
- `get_all_notifications(project_id)` - Get all notifications

#### Activity Service (`api/services/activity_service.py`)

**Functions:**
- `log_activity(...)` - Log project activity
- `get_project_activity_timeline(project_id, limit)` - Get activity timeline

### 3. Signals (`apps/workflows/signals.py`)

Automatic activity logging for:
- ✅ Expense created
- ✅ LPO issued
- ✅ Client payment received
- ✅ Photo uploaded
- ✅ Stage completed

## API Endpoints

### Budget Control

No direct endpoints - integrated into expense creation workflow.

**Usage in Expense Creation:**
```python
POST /api/expenses/
{
    "project": "uuid",
    "expense_type": "MATERIALS",
    "amount": 100000,
    "allocations": [
        {"bq_item_id": "uuid", "amount": 100000}
    ]
}

# Response includes budget validation:
{
    "expense": {...},
    "budget_check": {
        "requires_approval": true,
        "overruns": [...]
    }
}
```

### Procurement Workflow

#### 1. Approve LPO
```
POST /api/purchase-orders/{id}/approve/
```

**Transitions:** DRAFT → APPROVED

**Response:**
```json
{
    "status": "success",
    "message": "LPO LPO-001 approved successfully",
    "new_status": "APPROVED",
    "lpo_id": "uuid"
}
```

#### 2. Mark LPO as Delivered
```
POST /api/purchase-orders/{id}/mark-delivered/
```

**Transitions:** APPROVED/ISSUED → DELIVERED

#### 3. Mark LPO as Invoiced
```
POST /api/purchase-orders/{id}/mark-invoiced/
```

**Body:**
```json
{
    "invoice_number": "INV-12345"
}
```

**Transitions:** DELIVERED → INVOICED

#### 4. Mark LPO as Paid
```
POST /api/purchase-orders/{id}/mark-paid/
```

**Body:**
```json
{
    "payment_reference": "PAY-67890"
}
```

**Transitions:** INVOICED → PAID

### Approval Workflow

#### 1. Create Approval (Automatic)
Approvals are created automatically when budget overruns are detected.

#### 2. Approve Request
```
POST /api/workflow-approvals/{id}/approve/
```

**Body:**
```json
{
    "notes": "Approved due to urgent project requirements"
}
```

**Response:**
```json
{
    "status": "success",
    "message": "Approval granted successfully",
    "approval_id": "uuid",
    "approved_by": "admin@example.com",
    "approved_at": "2026-03-11T10:30:00Z"
}
```

#### 3. Reject Request
```
POST /api/workflow-approvals/{id}/reject/
```

**Body:**
```json
{
    "reason": "Budget cannot be exceeded without project sponsor approval"
}
```

#### 4. Get Pending Approvals
```
GET /api/workflow-approvals/pending/
```

**Response:**
```json
[
    {
        "id": "uuid",
        "approval_type": "EXPENSE",
        "status": "PENDING",
        "amount": 150000.00,
        "requested_by_email": "user@example.com",
        "requested_at": "2026-03-11T09:00:00Z"
    }
]
```

### Project Activity Timeline

#### Get Project Activities
```
GET /api/projects/{id}/activity/?limit=50
```

**Response:**
```json
{
    "project_id": "uuid",
    "total_activities": 120,
    "activities": [
        {
            "id": "uuid",
            "activity_type": "EXPENSE_CREATED",
            "activity_type_display": "Expense Created",
            "description": "Expense created: Materials - 100000.00",
            "amount": 100000.00,
            "performed_by_name": "John Doe",
            "created_at": "2026-03-11T10:00:00Z"
        },
        {
            "id": "uuid",
            "activity_type": "LPO_APPROVED",
            "description": "LPO LPO-001 approved for ABC Suppliers",
            "amount": 500000.00,
            "performed_by_name": "Jane Smith",
            "created_at": "2026-03-11T09:30:00Z"
        }
    ]
}
```

### Notifications

#### Get Project Notifications
```
GET /api/projects/{id}/notifications/
```

**Response:**
```json
{
    "budget_overruns": [
        {
            "type": "budget_overrun",
            "severity": "high",
            "project_id": "uuid",
            "bq_item": "Foundation Excavation",
            "message": "Foundation Excavation: Over budget by 25000.00",
            "variance": -25000.00,
            "variance_percentage": -16.67
        }
    ],
    "unpaid_invoices": [
        {
            "type": "unpaid_invoice",
            "severity": "high",
            "invoice_number": "INV-001",
            "supplier": "ABC Cement Ltd",
            "amount": 400000.00,
            "days_past_due": 45,
            "message": "Invoice INV-001 from ABC Cement Ltd is 45 days overdue"
        }
    ],
    "expiring_approvals": [
        {
            "type": "expiring_approval",
            "severity": "medium",
            "approval_type": "NCA Approval",
            "project_code": "PRJ-001",
            "days_until_expiry": 15,
            "message": "NCA Approval for PRJ-001 expires in 15 days"
        }
    ],
    "total_count": 12,
    "high_severity_count": 5
}
```

## Usage Examples

### Budget Control Integration

```python
# When creating an expense
from api.services.budget_control import validate_expense_budget

expense = Expense.objects.create(...)
allocations = [
    {'bq_item_id': bq_item_1.id, 'amount': 50000},
    {'bq_item_id': bq_item_2.id, 'amount': 50000}
]

validation = validate_expense_budget(expense, allocations)

if validation['requires_approval']:
    # Create approval request
    approval = create_approval_request(
        approval_type='EXPENSE',
        amount=expense.amount,
        requested_by=request.user,
        reason='Budget overrun detected',
        expense_id=expense.id
    )
    expense.approval_status = 'REQUIRES_APPROVAL'
    expense.save()
```

### Procurement Workflow

```python
# LPO workflow
from api.services.procurement_workflow import (
    approve_lpo, mark_lpo_delivered, mark_lpo_invoiced, mark_lpo_paid
)

# Step 1: Approve draft LPO
result = approve_lpo(lpo, approved_by=manager)

# Step 2: Mark as delivered
result = mark_lpo_delivered(lpo, delivered_by=site_engineer)

# Step 3: Mark as invoiced
result = mark_lpo_invoiced(lpo, invoiced_by=accountant, invoice_number='INV-123')

# Step 4: Mark as paid
result = mark_lpo_paid(lpo, paid_by=accountant, payment_reference='PAY-456')
```

### Activity Logging

```python
# Manual activity logging
from api.services.activity_service import log_activity

log_activity(
    project_id=project.id,
    activity_type='EXPENSE_CREATED',
    description=f'Equipment hire: {equipment_name}',
    amount=hire_cost,
    performed_by=request.user,
    related_object_type='Expense',
    related_object_id=expense.id,
    metadata={'equipment': equipment_name}
)
```

### Notifications

```python
# Check for alerts
from api.services.notification_service import get_all_notifications

notifications = get_all_notifications(project_id=project.id)

if notifications['high_severity_count'] > 0:
    send_alert_email(project_manager.email, notifications)
```

## Model Changes

### Expense Model
**New Field:**
- `approval_status`: APPROVED, PENDING_APPROVAL, REQUIRES_APPROVAL, REJECTED

### LocalPurchaseOrder Model
**Updated Statuses:**
- DRAFT
- APPROVED (new)
- ISSUED
- PARTIALLY_DELIVERED
- DELIVERED
- INVOICED (new)
- PAID (new)
- CANCELLED

## Workflow Diagrams

### LPO Procurement Workflow
```
DRAFT
  │
  ├─ approve_lpo() ──> APPROVED
  │                      │
  │                      │
  │                      ├─ mark_delivered() ──> DELIVERED
  │                                                │
  │                                                │
  │                                                ├─ mark_invoiced() ──> INVOICED
  │                                                                           │
  │                                                                           │
  │                                                                           ├─ mark_paid() ──> PAID
  │
  └─ (cancel) ──> CANCELLED
```

### Expense Approval Workflow
```
Create Expense
  │
  ├─ Budget Check
  │    │
  │    ├─ Within Budget ──> APPROVED (auto)
  │    │
  │    └─ Over Budget ──> REQUIRES_APPROVAL
  │                          │
  │                          ├─ Create Approval Request
  │                          │    │
  │                          │    ├─ approve_request() ──> APPROVED
  │                          │    │
  │                          │    └─ reject_request() ──> REJECTED
  │
  └─ Complete
```

## Testing

### Test Budget Control
```python
from api.services.budget_control import check_budget_overrun

expense = Expense(amount=150000, ...)
result = check_budget_overrun(expense, bq_item_id)

assert result['is_overrun'] == True
assert result['variance'] < 0
```

### Test Procurement Workflow
```python
from api.services.procurement_workflow import approve_lpo

lpo = LocalPurchaseOrder(status='DRAFT', ...)
result = approve_lpo(lpo, user)

assert lpo.status == 'APPROVED'
assert result['status'] == 'success'
```

## Security Considerations

1. **Approval Authorization**: Implement permission checks for approval actions
2. **Activity Tampering**: ProjectActivity is read-only via API
3. **Workflow State Validation**: All state transitions validated
4. **Audit Trail**: All activities logged with user and timestamp

## Performance Notes

- Activity logging is asynchronous via signals
- Notifications use optimized queries with select_related/prefetch_related
- Budget checks cached during request lifecycle
- Activity timeline paginated by default

## Future Enhancements

- [ ] Email notifications for approvals
- [ ] SMS alerts for high-severity notifications
- [ ] Approval delegation chains
- [ ] Workflow customization per organization
- [ ] Dashboard widgets for notifications
- [ ] Scheduled notification reports
- [ ] Approval reminder notifications

## Related Documentation

- [Domain Intelligence Layer](./DOMAIN_INTELLIGENCE.md)
- [REST API Documentation](./README.md)
- [Model Documentation](../apps/README.md)
