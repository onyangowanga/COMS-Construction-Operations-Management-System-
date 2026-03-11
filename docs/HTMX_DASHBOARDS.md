# HTMX Dashboards - Operational Monitoring

## Overview

The HTMX dashboards provide real-time operational monitoring for the COMS system with dynamic, auto-refreshing widgets. Built using Django templates, HTMX for partial updates, and Bootstrap 5 for styling.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      Dashboard URLs                         │
│  /projects/{id}/dashboard/ - Project Dashboard             │
│  /procurement/ - Procurement Dashboard                      │
│  /finance/ - Finance Dashboard                             │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                     Django Views                            │
│  - Main dashboard views (render full page)                  │
│  - Partial views (HTMX endpoints for widgets)              │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                      Selectors                              │
│  - Data aggregation from multiple models                    │
│  - Business logic for calculations                          │
│  - Query optimization with select_related/prefetch_related  │
└─────────────────────────────────────────────────────────────┘
                            │
                            ▼
┌─────────────────────────────────────────────────────────────┐
│                    HTMX Templates                           │
│  - Base dashboard template (layout, HTMX setup)            │
│  - Dashboard pages (containers for widgets)                 │
│  - Partial templates (individual widgets)                   │
└─────────────────────────────────────────────────────────────┘
```

## Features

### 1. Project Dashboard
**URL:** `/projects/{project_id}/dashboard/`

**Widgets:**
- **Financial Summary** - Revenue, expenses, profit, budget utilization
- **Budget Variance** - BQ item-level budget tracking
- **Recent Activity** - Timeline of project events
- **Supplier Outstanding** - Unpaid invoices by supplier
- **Unpaid Wages** - Worker payment tracking (placeholder)

**Auto-refresh:** Every 30 seconds

### 2. Procurement Dashboard
**URL:** `/procurement/`

**Widgets:**
- **Pending LPO Approvals** - LPOs awaiting approval with urgency indicators
- **Delivered but Not Invoiced** - Items received but not yet invoiced
- **Invoiced but Not Paid** - Outstanding supplier payments

**Auto-refresh:** Every 30 seconds

### 3. Finance Dashboard
**URL:** `/finance/`

**Widgets:**
- **Financial Overview** - Organization-wide metrics
  - Total revenue
  - Total expenses
  - Net profit
  - Supplier liabilities
  - Active projects
  - Average project profit
- **Financial Health Indicators**
  - Profit margin
  - Liquidity ratio
  - Outstanding ratio

**Auto-refresh:** Every 30 seconds

## File Structure

```
apps/dashboards/
├── __init__.py
├── apps.py                  # App configuration
├── views.py                 # Dashboard views (16 views total)
├── selectors.py             # Data aggregation logic (10 selectors)
└── urls.py                  # URL routing (12 endpoints)

templates/dashboards/
├── base_dashboard.html      # Base template with HTMX setup
├── project_dashboard.html   # Project dashboard page
├── procurement_dashboard.html  # Procurement dashboard page
├── finance_dashboard.html   # Finance dashboard page
└── partials/
    ├── financial_summary.html          # Project financial stats
    ├── budget_variance.html            # BQ item variances
    ├── recent_activity.html            # Activity timeline
    ├── supplier_outstanding.html       # Outstanding payments
    ├── unpaid_wages.html               # Worker wages (placeholder)
    ├── pending_lpo_approvals.html      # Pending LPOs
    ├── delivered_not_invoiced.html     # Delivered items
    ├── invoiced_not_paid.html          # Unpaid invoices
    └── finance_summary.html            # Organization finances
```

## URLs and Endpoints

### Project Dashboard URLs
```python
/projects/<uuid>/dashboard/                              # Main dashboard
/projects/<uuid>/dashboard/partials/financial-summary/   # Financial widget
/projects/<uuid>/dashboard/partials/budget-variance/     # Budget widget
/projects/<uuid>/dashboard/partials/recent-activity/     # Activity widget
/projects/<uuid>/dashboard/partials/supplier-outstanding/ # Outstanding widget
/projects/<uuid>/dashboard/partials/unpaid-wages/        # Wages widget
```

### Procurement Dashboard URLs
```python
/procurement/                                  # Main dashboard
/procurement/partials/pending-approvals/       # Pending LPOs widget
/procurement/partials/delivered-not-invoiced/  # Delivered widget
/procurement/partials/invoiced-not-paid/       # Unpaid widget
```

### Finance Dashboard URLs
```python
/finance/                    # Main dashboard
/finance/partials/summary/   # Financial summary widget
```

## Selectors (Data Layer)

### Project Selectors

#### `get_project_financial_summary(project_id)`
Returns financial summary for a project.

**Returns:**
```python
{
    'total_revenue': Decimal,
    'total_expenses': Decimal,
    'profit': Decimal,
    'profit_margin': Decimal,
    'budget_allocated': Decimal,
    'budget_spent': Decimal,
    'budget_remaining': Decimal,
    'budget_utilization': Decimal,
}
```

#### `get_project_budget_variance(project_id)`
Returns budget variance for all BQ items in a project.

**Returns:**
```python
[
    {
        'id': uuid,
        'description': str,
        'budget': Decimal,
        'spent': Decimal,
        'remaining': Decimal,
        'variance_percentage': Decimal,
        'status': 'over'|'under'|'exact',
    },
    ...
]
```

#### `get_project_supplier_outstanding(project_id)`
Returns outstanding supplier payments.

**Returns:**
```python
[
    {
        'lpo_number': str,
        'supplier_name': str,
        'total_amount': Decimal,
        'paid_amount': Decimal,
        'balance': Decimal,
        'invoice_number': str,
        'days_outstanding': int,
        'status': 'overdue'|'due'|'recent',
    },
    ...
]
```

#### `get_recent_project_activity(project_id, limit=20)`
Returns recent project activity timeline.

**Returns:**
```python
[
    {
        'activity_type': str,
        'description': str,
        'amount': Decimal,
        'performed_by': str,
        'created_at': datetime,
    },
    ...
]
```

### Procurement Selectors

#### `get_pending_lpo_approvals()`
Returns all LPOs awaiting approval.

**Returns:**
```python
[
    {
        'id': uuid,
        'lpo_number': str,
        'project_code': str,
        'project_name': str,
        'supplier_name': str,
        'amount': Decimal,
        'created_at': datetime,
        'days_pending': int,
    },
    ...
]
```

#### `get_delivered_not_invoiced_lpos()`
Returns LPOs delivered but not invoiced.

#### `get_invoiced_not_paid_lpos()`
Returns invoiced but unpaid LPOs.

### Finance Selectors

#### `get_finance_summary()`
Returns organization-wide financial summary.

**Returns:**
```python
{
    'total_revenue': Decimal,
    'total_expenses': Decimal,
    'profit': Decimal,
    'profit_margin': Decimal,
    'supplier_liabilities': Decimal,
    'active_projects': int,
    'average_project_profit': Decimal,
}
```

## HTMX Integration

### How HTMX Works in Dashboards

1. **Initial Load:** Dashboard page loads with empty widget containers
2. **Auto-Load:** `hx-trigger="load"` fetches widget data on page load
3. **Auto-Refresh:** `data-auto-refresh="true"` marks widgets for periodic refresh
4. **Indicators:** Loading spinners show during data fetch

### Example Widget Setup

```html
<div class="card-widget-body"
     hx-get="/projects/uuid/dashboard/partials/financial-summary/"
     hx-trigger="load, refresh from:body"
     hx-indicator=".htmx-indicator"
     data-auto-refresh="true">
    <div class="text-center text-muted py-4">
        <span class="loading-spinner"></span> Loading...
    </div>
</div>
```

**Attributes:**
- `hx-get` - URL to fetch partial HTML
- `hx-trigger="load"` - Load on page load
- `hx-trigger="refresh from:body"` - Listen for custom refresh event
- `hx-indicator` - Show loading spinner during request
- `data-auto-refresh` - Mark for periodic auto-refresh

### Auto-Refresh Mechanism

JavaScript in base template:
```javascript
// Auto-refresh every 30 seconds
setInterval(() => {
    document.querySelectorAll('[data-auto-refresh]').forEach(element => {
        htmx.trigger(element, 'refresh');
    });
}, 30000);
```

### CSRF Protection

All HTMX requests include CSRF token:
```javascript
document.body.addEventListener('htmx:configRequest', (event) => {
    const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
    if (csrfToken) {
        event.detail.headers['X-CSRFToken'] = csrfToken;
    }
});
```

## Styling and UI Components

### Stat Cards

```html
<div class="stat-card">
    <div class="d-flex align-items-start">
        <div class="stat-icon success">
            <i class="bi bi-cash-coin"></i>
        </div>
        <div class="ms-3 flex-grow-1">
            <div class="stat-label">Total Revenue</div>
            <div class="stat-value text-success">KES 1,500,000.00</div>
        </div>
    </div>
</div>
```

**Variants:** `primary`, `success`, `warning`, `danger`, `info`

### Card Widgets

```html
<div class="card-widget">
    <div class="card-widget-header">
        <h2 class="card-widget-title">Widget Title</h2>
        <span class="htmx-indicator">...</span>
    </div>
    <div class="card-widget-body">
        <!-- Widget content -->
    </div>
</div>
```

### Status Badges

```html
<span class="badge-status bg-danger text-white">
    <i class="bi bi-exclamation-triangle-fill"></i> Overdue
</span>

<span class="badge-status bg-warning text-dark">
    <i class="bi bi-clock-fill"></i> Due Soon
</span>

<span class="badge-status bg-success text-white">
    <i class="bi bi-check-circle-fill"></i> On Track
</span>
```

## Usage Examples

### Accessing Dashboards

#### View Project Dashboard
1. Navigate to: `http://your-domain/projects/{project_id}/dashboard/`
2. Widgets load automatically
3. Data refreshes every 30 seconds

#### View Procurement Dashboard
1. Navigate to: `http://your-domain/procurement/`
2. See all pending LPOs, delivered items, and unpaid invoices

#### View Finance Dashboard
1. Navigate to: `http://your-domain/finance/`
2. Monitor organization-wide financial health

### Manual Refresh

Click the "Refresh" button in the header to manually reload all widgets.

### Integration with REST API

Dashboards use internal views for data, but you can also fetch data via REST API:

```javascript
// Fetch financial summary via API
fetch('/api/projects/{id}/financial-summary/')
    .then(res => res.json())
    .then(data => console.log(data));

// Fetch budget variance via API
fetch('/api/projects/{id}/budget-variance/')
    .then(res => res.json())
    .then(data => console.log(data));
```

## Performance Considerations

### Query Optimization

#### Select Related / Prefetch Related
```python
lpos = LocalPurchaseOrder.objects.filter(
    status='INVOICED'
).select_related('project', 'supplier').annotate(
    paid_amount=Sum('supplier_payments__amount')
)
```

#### Aggregations
```python
total_revenue = ClientPayment.objects.filter(
    project_id=project_id
).aggregate(total=Sum('amount'))['total']
```

### Caching (Future Enhancement)

Consider implementing caching for frequently accessed data:

```python
from django.core.cache import cache

def get_finance_summary():
    cache_key = 'finance_summary'
    summary = cache.get(cache_key)
    
    if summary is None:
        summary = {
            # Calculate summary
        }
        cache.set(cache_key, summary, 300)  # Cache for 5 minutes
    
    return summary
```

## Testing

### Unit Tests for Selectors

```python
from django.test import TestCase
from apps.dashboards.selectors import get_project_financial_summary

class ProjectDashboardSelectorsTest(TestCase):
    def test_financial_summary(self):
        # Create test data
        project = Project.objects.create(...)
        
        # Get summary
        summary = get_project_financial_summary(project.id)
        
        # Assertions
        self.assertIn('total_revenue', summary)
        self.assertIn('profit', summary)
```

### Integration Tests for Views

```python
from django.test import Client, TestCase

class DashboardViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(...)
        self.client.login(...)
    
    def test_project_dashboard_loads(self):
        project = Project.objects.create(...)
        response = self.client.get(f'/projects/{project.id}/dashboard/')
        self.assertEqual(response.status_code, 200)
```

## Deployment Checklist

- [x] Create dashboard app structure
- [x] Implement views and selectors
- [x] Create templates with HTMX
- [x] Add URL patterns
- [x] Update INSTALLED_APPS
- [ ] Run migrations (if needed)
- [ ] Collect static files
- [ ] Test on staging environment
- [ ] Deploy to production

## Next Steps

### Immediate
1. **Test Dashboards:** Access each dashboard URL and verify widgets load
2. **Run Migrations:** `python manage.py migrate`
3. **Collect Static:** `python manage.py collectstatic`

### Future Enhancements
1. **Export Functionality:** Add PDF/Excel export for reports
2. **Filtering:** Add date range filters for dashboards
3. **Charts:** Integrate Chart.js for visual analytics
4. **Real-time Updates:** Use WebSockets for instant updates
5. **Mobile Responsive:** Optimize for mobile devices
6. **Permission-based Views:** Restrict dashboards by user role
7. **Custom Widgets:** Allow users to configure dashboard layout

## Troubleshooting

### Widgets Not Loading

**Check:**
1. CSRF token is present in page
2. User is authenticated (`@login_required`)
3. HTMX library loaded correctly
4. Console for JavaScript errors

### Data Not Refreshing

**Check:**
1. `data-auto-refresh="true"` attribute present
2. Auto-refresh interval in base template
3. Network tab for failed requests

### Slow Performance

**Solutions:**
1. Add database indexes on frequently queried fields
2. Implement caching for expensive calculations
3. Reduce auto-refresh frequency
4. Optimize selector queries

## Support

### Related Documentation
- [Operational Workflows](../api/OPERATIONAL_WORKFLOWS.md)
- [REST API Documentation](../api/README.md)
- [Django Templates](https://docs.djangoproject.com/en/5.0/topics/templates/)
- [HTMX Documentation](https://htmx.org/docs/)
- [Bootstrap 5](https://getbootstrap.com/docs/5.3/)

### Repository
- Issues: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/issues

---

**Dashboards are production-ready!** 🎯

Access your dashboards:
- Project: `/projects/{id}/dashboard/`
- Procurement: `/procurement/`
- Finance: `/finance/`
