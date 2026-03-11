# Domain Intelligence Layer

## Overview

The Domain Intelligence Layer provides advanced analytics and business intelligence endpoints for the Construction Operations Management System (COMS). This layer implements clean architecture principles with separated concerns:

- **Selectors** (`api/selectors/`) - Complex database queries with optimizations
- **Services** (`api/services/`) - Business logic and analytics calculations
- **Views** - Thin presentation layer that orchestrates selectors and services

## Architecture

```
┌─────────────────┐
│     Views       │  ← Thin layer, orchestrates flow
└────────┬────────┘
         │
    ┌────┴────┐
    │         │
┌───▼──┐  ┌──▼───────┐
│Select│  │ Services │  ← Business logic
│ ors  │  └──────────┘
└──────┘       │
    │          │
    │      ┌───▼────┐
    └──────► Models │  ← Database layer
           └────────┘
```

### Design Principles

1. **Single Responsibility**: Each module has one clear purpose
2. **Query Optimization**: Use `select_related()` and `prefetch_related()` in selectors
3. **Business Logic Isolation**: All calculations in services, not views or models
4. **Testability**: Each layer can be tested independently
5. **Reusability**: Services can be called from views, tasks, or other services

## Analytics Endpoints

### 1. Project Financial Summary

**Endpoint**: `GET /api/projects/{id}/financial-summary/`

**Description**: Comprehensive financial overview of a project

**Response**:
```json
{
  "project_id": "uuid",
  "project_code": "PRJ-001",
  "project_name": "Office Building Construction",
  "contract_value": 15000000.00,
  "total_client_payments": 10000000.00,
  "outstanding_from_client": 5000000.00,
  "total_expenses": 8500000.00,
  "supplier_payments": 5000000.00,
  "consultant_payments": 2000000.00,
  "labour_cost": 1500000.00,
  "remaining_budget": 6500000.00,
  "profit": 1500000.00,
  "profit_margin": 10.0
}
```

**Use Cases**:
- Executive dashboard
- Financial reporting
- Budget monitoring
- Profitability analysis

---

### 2. Budget Variance Analysis

**Endpoint**: `GET /api/projects/{id}/budget-variance/`

**Description**: Detailed variance analysis comparing budgeted amounts (BQ) vs actual expenses

**Response**:
```json
{
  "project_id": "uuid",
  "summary": {
    "total_budget": 15000000.00,
    "total_actual": 8500000.00,
    "total_variance": 6500000.00,
    "variance_percentage": 43.33
  },
  "items": [
    {
      "bq_item_id": "uuid",
      "section": "Preliminary and General",
      "element": "Site Establishment",
      "item_name": "Site Clearing",
      "item_number": "1.1.1",
      "budgeted_amount": 50000.00,
      "actual_expenses": 52000.00,
      "variance": -2000.00,
      "variance_percentage": -4.0,
      "status": "OVER_BUDGET"
    },
    {
      "bq_item_id": "uuid",
      "section": "Substructure",
      "element": "Excavation",
      "item_name": "Foundation Excavation",
      "item_number": "2.1.1",
      "budgeted_amount": 150000.00,
      "actual_expenses": 140000.00,
      "variance": 10000.00,
      "variance_percentage": 6.67,
      "status": "UNDER_BUDGET"
    }
  ]
}
```

**Variance Status**:
- `SIGNIFICANTLY_UNDER_BUDGET` - More than 10% under budget
- `UNDER_BUDGET` - Under budget but within 10%
- `OVER_BUDGET` - Over budget but within 10%
- `SIGNIFICANTLY_OVER_BUDGET` - More than 10% over budget

**Use Cases**:
- Cost control
- Budget monitoring
- Identifying cost overruns
- Variance reporting

---

### 3. Project Health Indicator

**Endpoint**: `GET /api/projects/{id}/health/`

**Description**: Overall project health assessment based on multiple indicators

**Response**:
```json
{
  "project_id": "uuid",
  "project_code": "PRJ-001",
  "project_name": "Office Building Construction",
  "health_status": "YELLOW",
  "budget_utilization_percentage": 56.67,
  "payment_collection_percentage": 66.67,
  "completion_rate": 45.0,
  "delayed_milestones": 2,
  "red_flags": [],
  "yellow_flags": [
    "2 delayed milestone(s)",
    "Moderate deficit: 1500000.00"
  ],
  "summary": {
    "total_stages": 10,
    "completed_stages": 4,
    "contract_value": 15000000.00,
    "total_expenses": 8500000.00,
    "total_payments": 10000000.00
  }
}
```

**Health Status**:
- `GREEN` - Project is on track
- `YELLOW` - Some concerns, needs attention
- `RED` - Critical issues, immediate action required

**Red Flags** (triggers RED status):
- Budget exceeded (>100% utilization)
- High deficit (>30% of contract value)
- Many delayed milestones (>3)

**Yellow Flags** (triggers YELLOW status):
- Budget utilization >90%
- Moderate deficit (>15% of contract value)
- Any delayed milestones
- Low completion rate vs budget utilization

**Use Cases**:
- Executive dashboard
- Project monitoring
- Risk management
- Early warning system

---

### 4. Supplier Outstanding Payments

**Endpoint**: `GET /api/suppliers/outstanding-payments/`

**Description**: All suppliers with pending payment balances

**Response**:
```json
{
  "summary": {
    "total_suppliers_with_outstanding": 5,
    "total_outstanding_amount": 2500000.00,
    "total_invoiced_amount": 5000000.00
  },
  "suppliers": [
    {
      "supplier_id": "uuid",
      "supplier_name": "ABC Cement Ltd",
      "contact_person": "John Doe",
      "phone": "+254700000000",
      "email": "info@abccement.com",
      "total_invoiced": 1200000.00,
      "total_paid": 800000.00,
      "outstanding_balance": 400000.00,
      "payment_completion_percentage": 66.67
    }
  ]
}
```

**Use Cases**:
- Cash flow management
- Payment scheduling
- Supplier relationship management
- Accounts payable tracking

---

### 5. Unpaid Labour Wages

**Endpoint**: `GET /api/workers/unpaid-wages/`

**Description**: All workers with outstanding unpaid wages

**Response**:
```json
{
  "summary": {
    "total_workers_with_unpaid_wages": 15,
    "total_unpaid_amount": 450000.00
  },
  "workers": [
    {
      "worker_id": "uuid",
      "worker_name": "James Kamau",
      "worker_role": "MASON",
      "id_number": "12345678",
      "phone": "+254700000001",
      "total_days_worked": 45,
      "days_unpaid": 10,
      "total_unpaid_wages": 15000.00
    }
  ]
}
```

**Use Cases**:
- Payroll management
- Labour cost tracking
- Worker payment scheduling
- Compliance monitoring

## Code Examples

### Using in Custom Views

```python
from api.selectors.project_selectors import get_project_financial_data
from api.services.project_analytics import calculate_project_financial_summary

def my_custom_view(request, project_id):
    # Get optimized data from selector
    project = get_project_financial_data(project_id)
    
    # Calculate analytics using service
    summary = calculate_project_financial_summary(project)
    
    # Use the data
    return render(request, 'template.html', {'summary': summary})
```

### Using in Management Commands

```python
from django.core.management.base import BaseCommand
from api.selectors.worker_selectors import get_workers_unpaid_wages
from api.services.worker_analytics import calculate_unpaid_wages

class Command(BaseCommand):
    def handle(self, *args, **options):
        # Get workers with unpaid wages
        workers = get_workers_unpaid_wages()
        unpaid_data = calculate_unpaid_wages(workers)
        
        # Send notifications
        for worker_data in unpaid_data:
            self.send_payment_reminder(worker_data)
```

### Using in Celery Tasks

```python
from celery import shared_task
from api.selectors.project_selectors import get_project_health_data
from api.services.project_analytics import calculate_project_health

@shared_task
def check_project_health(project_id):
    health_data = get_project_health_data(project_id)
    health = calculate_project_health(health_data)
    
    if health['health_status'] == 'RED':
        send_alert_to_management(health)
```

## Performance Optimization

### Query Optimization

All selectors use Django ORM optimization techniques:

```python
# ✅ Good - Optimized query
Project.objects.select_related('client').prefetch_related(
    'expense_set',
    'clientpayment_set'
).get(id=project_id)

# ❌ Bad - N+1 queries
project = Project.objects.get(id=project_id)
for expense in project.expense_set.all():  # Additional query each iteration
    process(expense)
```

### Aggregation at Database Level

```python
# ✅ Good - Aggregate in database
workers = Worker.objects.annotate(
    total_unpaid_wages=Sum('dailylabourrecord__daily_wage', 
                          filter=Q(dailylabourrecord__paid=False))
)

# ❌ Bad - Calculate in Python
workers = Worker.objects.all()
for worker in workers:
    total = sum(r.daily_wage for r in worker.records.filter(paid=False))
```

## Testing

### Testing Selectors

```python
from django.test import TestCase
from api.selectors.project_selectors import get_project_financial_data

class ProjectSelectorTests(TestCase):
    def test_get_project_financial_data(self):
        project = create_test_project()
        result = get_project_financial_data(project.id)
        
        self.assertIsNotNone(result)
        self.assertEqual(result.id, project.id)
```

### Testing Services

```python
from django.test import TestCase
from api.services.project_analytics import calculate_project_financial_summary

class ProjectAnalyticsTests(TestCase):
    def test_calculate_financial_summary(self):
        project = create_test_project_with_data()
        summary = calculate_project_financial_summary(project)
        
        self.assertIn('contract_value', summary)
        self.assertIn('profit', summary)
        self.assertIn('profit_margin', summary)
```

## Extension Points

### Adding New Analytics

1. **Create Selector**:
```python
# api/selectors/project_selectors.py
def get_project_risk_data(project_id):
    """Get data needed for risk assessment"""
    pass
```

2. **Create Service**:
```python
# api/services/project_analytics.py
def calculate_project_risk_score(risk_data):
    """Calculate comprehensive risk score"""
    pass
```

3. **Add View Action**:
```python
# api/views/projects.py
@action(detail=True, methods=['get'], url_path='risk-assessment')
def risk_assessment(self, request, pk=None):
    risk_data = get_project_risk_data(pk)
    risk_score = calculate_project_risk_score(risk_data)
    return Response(risk_score)
```

## Best Practices

1. **Keep Views Thin**: Views should only orchestrate, not calculate
2. **Optimize Early**: Use `select_related()` and `prefetch_related()` in selectors
3. **Document Clearly**: Explain business logic in docstrings
4. **Test Independently**: Each layer should have its own tests
5. **Handle Errors**: Always check for None/empty results
6. **Cache Wisely**: Consider caching expensive calculations
7. **Monitor Performance**: Use Django Debug Toolbar in development

## API Documentation

All endpoints are automatically documented in:
- **Swagger UI**: `http://your-domain/api/docs/`
- **ReDoc**: `http://your-domain/api/redoc/`
- **OpenAPI Schema**: `http://your-domain/api/schema/`

## Related Documentation

- [REST API Documentation](./README.md)
- [Django Model Documentation](../apps/README.md)
- [Deployment Guide](../docs/deployment.md)
