# Cash Flow Forecasting Module Documentation

Complete guide to the COMS Cash Flow Forecasting Module for construction project cash management and financial planning.

---

## Table of Contents

1. [Overview](#overview)
2. [Features](#features)
3. [Architecture](#architecture)
4. [Data Models](#data-models)
5. [Cash Flow Engine](#cash-flow-engine)
6. [Forecast Calculations](#forecast-calculations)
7. [API Endpoints](#api-endpoints)
8. [Dashboard](#dashboard)
9. [Usage Examples](#usage-examples)
10. [Deployment](#deployment)
11. [Troubleshooting](#troubleshooting)

---

## Overview

The Cash Flow Forecasting Module provides comprehensive cash flow projection and monitoring capabilities for construction projects. It analyzes historical financial data, project schedules, and procurement patterns to generate accurate cash flow forecasts for 3, 6, and 12-month horizons.

### Key Capabilities

- **Monthly Cash Flow Forecasting**: Project-level and portfolio-wide forecasts
- **Inflow Tracking**: Valuations, client payments, retention releases, variation orders
- **Outflow Tracking**: Supplier payments, labour costs, consultant fees, procurement, site expenses
- **Risk Identification**: Negative cash flow alerts and cumulative balance warnings
- **Trend Analysis**: Historical patterns and future projections
- **Interactive Dashboard**: Real-time HTMX-powered visualization with charts

### Business Value

- **Liquidity Management**: Predict cash shortfalls before they occur
- **Project Planning**: Align procurement and payment schedules with cash availability
- **Risk Mitigation**: Identify projects with severe cash flow issues
- **Portfolio Optimization**: Balance cash flow across multiple projects
- **Stakeholder Reporting**: Provide accurate financial forecasts to management and investors

---

## Features

### 1. Forecast Horizons

Generate forecasts for three time periods:

- **3 Months**: Short-term liquidity planning
- **6 Months**: Medium-term financial management (default)
- **12 Months**: Long-term strategic planning

### 2. Inflow Sources

The system tracks and forecasts five primary cash inflow sources:

1. **Expected Valuations**: Based on project progress and contract schedules
2. **Client Payments**: Expected payment receipts on approved valuations
3. **Retention Releases**: Scheduled release of retention money
4. **Variation Order Payments**: Payments from approved change orders

### 3. Outflow Categories

Six categories of cash outflows are tracked and forecasted:

1. **Supplier Payments**: Invoices and purchase order payments
2. **Labour Costs**: Payroll and subcontractor fees
3. **Consultant Fees**: Professional services payments
4. **Procurement Payments**: Material and equipment purchases
5. **Site Expenses**: Operational costs (utilities, equipment rental, etc.)
6. **Other Expenses**: Miscellaneous project costs

### 4. Risk Alerts

Automatic alerts for:

- **Negative Cumulative Balance**: Projects with overall negative cash position
- **Severe Negative Monthly Flow**: Projects with cash deficit > KES 100,000/month
- **Multiple Negative Months**: Projects with sustained cash flow problems

### 5. Portfolio Analytics

- Aggregated portfolio-wide cash flow summaries
- Project-level trend analysis
- Comparative project performance
- Critical project identification

---

## Architecture

The Cash Flow module follows the standard COMS architecture pattern:

```
apps/cashflow/
├── models.py              # Data models (CashFlowForecast, PortfolioCashFlowSummary)
├── services.py            # Business logic (CashFlowService)
├── selectors.py           # Query functions (get_project_forecast, etc.)
├── admin.py               # Django admin interface
├── apps.py                # App configuration
└── migrations/            # Database migrations

api/
├── serializers/
│   └── cashflow.py        # API serializers
└── views/
    └── cashflow.py        # API viewsets (ProjectCashFlowViewSet, PortfolioCashFlowViewSet)

templates/dashboards/
├── cashflow_dashboard.html                     # Main dashboard
└── partials/
    ├── cashflow_summary.html                   # Summary cards
    ├── cashflow_negative_projects.html         # Negative flow projects table
    ├── cashflow_alerts.html                    # Critical alerts
    └── cashflow_generate_success.html          # Generation success message
```

### Design Patterns

1. **Service Layer**: All business logic in `CashFlowService`
2. **Selector Layer**: Database queries in `selectors.py`
3. **Thin Views**: Controllers delegate to services and selectors
4. **RESTful API**: DRF viewsets for API endpoints
5. **HTMX**: Progressive enhancement for dashboard interactivity

---

## Data Models

### CashFlowForecast

Stores monthly cash flow forecast for a single project.

**Fields:**

```python
# Relationship
project = ForeignKey(Project)

# Period
forecast_month = DateField()              # First day of month (YYYY-MM-01)
forecast_generated_at = DateTimeField()   # When forecast was computed

# Inflows
expected_valuations = DecimalField()
expected_client_payments = DecimalField()
expected_retention_releases = DecimalField()
expected_variation_order_payments = DecimalField()
total_inflow = DecimalField()             # Auto-computed sum

# Outflows
expected_supplier_payments = DecimalField()
expected_labour_costs = DecimalField()
expected_consultant_fees = DecimalField()
expected_procurement_payments = DecimalField()
expected_site_expenses = DecimalField()
expected_other_expenses = DecimalField()
total_outflow = DecimalField()            # Auto-computed sum

# Metrics
net_cash_flow = DecimalField()            # total_inflow - total_outflow
cumulative_cash_balance = DecimalField()  # Running balance

# Metadata
is_actual = BooleanField()                # True if actual data (not forecast)
updated_at = DateTimeField()
```

**Indexes:**

- `(project, forecast_month)` - Unique together
- `forecast_month`
- `is_actual`

**Auto-Calculation:**

The model automatically computes `total_inflow`, `total_outflow`, and `net_cash_flow` on save.

### PortfolioCashFlowSummary

Portfolio-wide aggregated cash flow for a given month.

**Fields:**

```python
forecast_month = DateField(unique=True)

# Aggregates
total_portfolio_inflow = DecimalField()
total_portfolio_outflow = DecimalField()
net_portfolio_cash_flow = DecimalField()
cumulative_portfolio_balance = DecimalField()

# Statistics
active_projects_count = IntegerField()
projects_with_negative_flow = IntegerField()

# Metadata
forecast_generated_at = DateTimeField()
updated_at = DateTimeField()
```

---

## Cash Flow Engine

The `CashFlowService` in `services.py` implements the forecasting engine.

### Core Methods

#### 1. `generate_project_forecast(project_id, horizon_months, start_date)`

Generate cash flow forecast for a single project.

**Parameters:**
- `project_id` (str): UUID of the project
- `horizon_months` (int): Number of months to forecast (3, 6, or 12)
- `start_date` (datetime, optional): Start date (defaults to current month)

**Returns:**
- List of `CashFlowForecast` instances

**Process:**
1. Retrieve project and related data
2. Delete existing forecasts for the period
3. For each month in horizon:
   - Compute monthly inflows (via `_compute_monthly_inflows`)
   - Compute monthly outflows (via `_compute_monthly_outflows`)
   - Calculate cumulative balance
   - Create forecast record
4. Return list of forecasts

**Example:**

```python
from apps.cashflow.services import CashFlowService

# Generate 6-month forecast for a project
forecasts = CashFlowService.generate_project_forecast(
    project_id='550e8400-e29b-41d4-a716-446655440000',
    horizon_months=6
)

print(f"Generated {len(forecasts)} monthly forecasts")
# Output: Generated 6 monthly forecasts
```

#### 2. `generate_portfolio_forecast(horizon_months, start_date)`

Generate portfolio-wide cash flow forecast for all active projects.

**Parameters:**
- `horizon_months` (int): Number of months to forecast
- `start_date` (datetime, optional): Start date

**Returns:**
- List of `PortfolioCashFlowSummary` instances

**Process:**
1. Get all active projects
2. Generate individual project forecasts
3. Aggregate monthly totals across all projects
4. Calculate cumulative portfolio balance
5. Create portfolio summary records

**Example:**

```python
# Generate 12-month portfolio forecast
summaries = CashFlowService.generate_portfolio_forecast(
    horizon_months=12
)

print(f"Generated {len(summaries)} months of portfolio forecasts")
```

#### 3. `update_all_forecasts(horizon_months)`

Convenience method to update forecasts for all active projects.

**Parameters:**
- `horizon_months` (int): Forecast horizon

**Returns:**
- Dictionary with update statistics:
  - `updated_projects`: Number of projects forecasted
  - `forecast_months`: Number of summary months created
  - `horizon_months`: Horizon used

**Example:**

```python
result = CashFlowService.update_all_forecasts(horizon_months=6)

print(f"Updated {result['updated_projects']} projects")
print(f"Created {result['forecast_months']} monthly summaries")
```

### Private Helper Methods

#### `_compute_monthly_inflows(project, forecast_month)`

Calculates expected inflows for a specific month.

**Inflow Calculation Logic:**

1. **Expected Valuations**:
   ```
   remaining_value = contract_value - approved_valuations
   months_remaining = project.end_date - forecast_month
   monthly_valuation = remaining_value / months_remaining
   
   # Apply S-curve weighting:
   if progress < 20%: monthly_valuation *= 0.7  (slow start)
   if progress > 80%: monthly_valuation *= 0.5  (slow finish)
   ```

2. **Client Payments**:
   ```
   recent_valuations = valuations approved in previous month
   retention_rate = 5% (default)
   expected_payment = recent_valuations * (1 - retention_rate)
   ```

3. **Retention Releases**:
   ```
   if progress > 95%:
       total_retention = approved_valuations * 5%
       release_per_month = total_retention / 3  (over 3 months)
   ```

4. **Variation Orders**:
   ```
   Currently simplified (10% of variations paid monthly)
   ```

**Returns:**

```python
{
    'valuations': Decimal,
    'client_payments': Decimal,
    'retention_releases': Decimal,
    'variation_orders': Decimal,
    'total_inflow': Decimal
}
```

#### `_compute_monthly_outflows(project, forecast_month)`

Calculates expected outflows for a specific month.

**Outflow Calculation Logic:**

Based on historical 3-month average expenses:

1. **Supplier Payments**: 40% of average monthly expenses
2. **Labour Costs**: 30% of average monthly expenses
3. **Consultant Fees**: 10% of average monthly expenses
4. **Procurement Payments**: 10% of average monthly expenses
5. **Site Expenses**: 8% of average monthly expenses
6. **Other Expenses**: 2% of average monthly expenses

**Calculation:**

```python
# Get average monthly expense from last 3 months
avg_monthly_expense = Expense.objects.filter(
    project=project,
    date__gte=three_months_ago,
    status='APPROVED'
).aggregate(Avg('amount'))

# Distribute by category
supplier_payments = avg_monthly_expense * 0.40
labour_costs = avg_monthly_expense * 0.30
...
```

**Returns:**

```python
{
    'supplier_payments': Decimal,
    'labour_costs': Decimal,
    'consultant_fees': Decimal,
    'procurement_payments': Decimal,
    'site_expenses': Decimal,
    'other_expenses': Decimal,
    'total_outflow': Decimal
}
```

#### `_get_current_cash_balance(project)`

Calculates current cash position for a project.

**Formula:**

```
cash_balance = total_approved_valuations - total_approved_expenses
```

**Note:** In production, this would track actual payment receipts and disbursements rather than approvals.

#### `_get_months_remaining(project, current_date)`

Calculates months until project end date.

**Returns:** Integer (minimum 1 month)

---

## Forecast Calculations

### Net Cash Flow

For each forecast month:

```
Net Cash Flow = Total Inflow - Total Outflow

Where:
  Total Inflow = valuations + client_payments + retention_releases + variation_orders
  Total Outflow = supplier_payments + labour_costs + consultant_fees + 
                  procurement_payments + site_expenses + other_expenses
```

### Cumulative Cash Balance

Running total across forecast period:

```
Month 1: Cumulative Balance = Starting Balance + Net Cash Flow (Month 1)
Month 2: Cumulative Balance = Previous Balance + Net Cash Flow (Month 2)
...
Month N: Cumulative Balance = Previous Balance + Net Cash Flow (Month N)
```

**Example:**

```
Starting Balance: KES 500,000

Month 1: Net Flow = KES 200,000
  → Cumulative: KES 700,000

Month 2: Net Flow = -KES 150,000
  → Cumulative: KES 550,000

Month 3: Net Flow = KES 300,000
  → Cumulative: KES 850,000
```

### Portfolio Aggregation

Portfolio-level metrics sum across all projects:

```
Portfolio Total Inflow (Month N) = SUM(Project Inflows for Month N)
Portfolio Total Outflow (Month N) = SUM(Project Outflows for Month N)
Portfolio Net Flow (Month N) = Portfolio Inflow - Portfolio Outflow
Portfolio Cumulative Balance = Previous Balance + Portfolio Net Flow
```

---

## API Endpoints

### Project Cash Flow Endpoints

Base URL: `/api/cashflow/project/`

#### 1. GET `/api/cashflow/project/{id}/forecast/`

Get monthly cash flow forecast for a project.

**Query Parameters:**
- `months` (int, optional): Forecast horizon (3, 6, or 12). Default: 6

**Response:**

```json
[
  {
    "id": "uuid",
    "project": {
      "id": "uuid",
      "name": "Highway Construction Project",
      "project_code": "PRJ-2026-001",
      "status": "IMPLEMENTATION",
      "organization_name": "Main Contractor Ltd"
    },
    "forecast_month": "2026-03-01",
    "month": "2026-03",
    "month_label": "Mar 2026",
    "expected_valuations": "5000000.00",
    "expected_client_payments": "4750000.00",
    "expected_retention_releases": "0.00",
    "expected_variation_order_payments": "200000.00",
    "total_inflow": "4950000.00",
    "expected_supplier_payments": "2000000.00",
    "expected_labour_costs": "1500000.00",
    "expected_consultant_fees": "500000.00",
    "expected_procurement_payments": "500000.00",
    "expected_site_expenses": "400000.00",
    "expected_other_expenses": "100000.00",
    "total_outflow": "5000000.00",
    "net_cash_flow": "-50000.00",
    "cumulative_cash_balance": "3450000.00",
    "is_actual": false,
    "forecast_generated_at": "2026-03-11T12:00:00Z"
  },
  ...
]
```

**cURL Example:**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/project/550e8400-e29b-41d4-a716-446655440000/forecast/?months=12"
```

#### 2. GET `/api/cashflow/project/{id}/trend/`

Get time series data for charting.

**Query Parameters:**
- `months` (int, optional): Number of months. Default: 6

**Response:**

```json
[
  {
    "month": "2026-03",
    "month_label": "Mar 2026",
    "inflow": 4950000.00,
    "outflow": 5000000.00,
    "net_flow": -50000.00,
    "cumulative_balance": 3450000.00
  },
  ...
]
```

**Use Case:** Feed data directly to Chart.js or other visualization libraries.

#### 3. GET `/api/cashflow/project/{id}/summary/`

Get aggregated forecast summary for a project.

**Response:**

```json
{
  "total_expected_inflow": "29700000.00",
  "total_expected_outflow": "30000000.00",
  "net_cash_flow": "-300000.00",
  "final_cash_balance": "3200000.00",
  "months_with_negative_flow": 2
}
```

#### 4. GET `/api/cashflow/project/{id}/breakdown/`

Get detailed inflow/outflow breakdown for a specific month.

**Query Parameters:**
- `month` (date, optional): Forecast month (YYYY-MM-DD). Default: current month

**Response:**

```json
{
  "valuations": "5000000.00",
  "client_payments": "4750000.00",
  "retention_releases": "0.00",
  "variation_orders": "200000.00",
  "supplier_payments": "2000000.00",
  "labour_costs": "1500000.00",
  "consultant_fees": "500000.00",
  "procurement_payments": "500000.00",
  "site_expenses": "400000.00",
  "other_expenses": "100000.00"
}
```

**cURL Example:**

```bash
curl -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/project/550e8400-e29b-41d4-a716-446655440000/breakdown/?month=2026-04-01"
```

#### 5. POST `/api/cashflow/project/{id}/generate/`

Generate/update forecast for a project.

**Query Parameters:**
- `months` (int, optional): Forecast horizon (3, 6, or 12). Default: 6

**Response:**

```json
{
  "message": "Forecast generated successfully",
  "forecasts_created": 6,
  "horizon_months": 6
}
```

**cURL Example:**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/project/550e8400-e29b-41d4-a716-446655440000/generate/?months=12"
```

### Portfolio Cash Flow Endpoints

Base URL: `/api/cashflow/portfolio/`

#### 6. GET `/api/cashflow/portfolio/forecast/`

Get portfolio-wide cash flow forecast.

**Query Parameters:**
- `months` (int, optional): Forecast horizon. Default: 6

**Response:**

```json
[
  {
    "id": "uuid",
    "forecast_month": "2026-03-01",
    "month": "2026-03",
    "month_label": "Mar 2026",
    "total_portfolio_inflow": "24850000.00",
    "total_portfolio_outflow": "25000000.00",
    "net_portfolio_cash_flow": "-150000.00",
    "cumulative_portfolio_balance": "17250000.00",
    "active_projects_count": 5,
    "projects_with_negative_flow": 2,
    "forecast_generated_at": "2026-03-11T12:00:00Z"
  },
  ...
]
```

#### 7. GET `/api/cashflow/portfolio/trend/`

Get portfolio trend data for charting.

**Query Parameters:**
- `months` (int, optional): Number of months. Default: 6

**Response:**

```json
[
  {
    "month": "2026-03",
    "month_label": "Mar 2026",
    "inflow": 24850000.00,
    "outflow": 25000000.00,
    "net_flow": -150000.00,
    "cumulative_balance": 17250000.00,
    "active_projects": 5,
    "negative_projects": 2
  },
  ...
]
```

#### 8. GET `/api/cashflow/portfolio/summary/`

Get portfolio forecast summary.

**Response:**

```json
{
  "total_expected_inflow": "149100000.00",
  "total_expected_outflow": "150000000.00",
  "net_portfolio_cash_flow": "-900000.00",
  "final_portfolio_balance": "16500000.00",
  "months_with_negative_flow": 3,
  "total_forecast_months": 6
}
```

#### 9. GET `/api/cashflow/portfolio/alerts/`

Get critical cash flow alerts.

**Response:**

```json
[
  {
    "project_id": "550e8400-e29b-41d4-a716-446655440000",
    "project_name": "Highway Construction Project",
    "alert_type": "NEGATIVE_BALANCE",
    "severity": "CRITICAL",
    "message": "Cumulative cash balance: -200,000.00",
    "forecast_month": "2026-05-01"
  },
  {
    "project_id": "650e8400-e29b-41d4-a716-446655440001",
    "project_name": "Bridge Rehabilitation",
    "alert_type": "SEVERE_NEGATIVE_FLOW",
    "severity": "HIGH",
    "message": "Expected negative cash flow: -150,000.00",
    "forecast_month": "2026-04-01"
  }
]
```

#### 10. POST `/api/cashflow/portfolio/generate/`

Generate forecast for all active projects.

**Query Parameters:**
- `months` (int, optional): Forecast horizon. Default: 6

**Response:**

```json
{
  "message": "Portfolio forecast generated successfully",
  "updated_projects": 5,
  "forecast_months": 6,
  "horizon_months": 6
}
```

**cURL Example:**

```bash
curl -X POST -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/portfolio/generate/?months=6"
```

---

## Dashboard

### Main Dashboard

**URL:** `/portfolio/cashflow/`

The cash flow dashboard provides a comprehensive view of portfolio-wide cash flow health.

#### Features

1. **Portfolio Summary Cards**
   - Total Expected Inflow
   - Total Expected Outflow
   - Net Portfolio Cash Flow
   - Final Portfolio Balance
   - Months with Negative Flow
   - Overall Health Indicator

2. **Interactive Cash Flow Chart**
   - Multi-line chart showing inflows, outflows, net flow, and cumulative balance
   - Switchable forecast horizons (3, 6, 12 months)
   - Dual Y-axes for monthly flow and cumulative balance
   - Auto-refresh every 60 seconds

3. **Critical Alerts Section**
   - Projects with negative cumulative balance (CRITICAL)
   - Projects with severe negative monthly flow (HIGH)
   - Color-coded severity badges
   - Auto-refresh every 30 seconds

4. **Negative Cash Flow Projects Table**
   - Projects with negative flow for current month
   - Detailed breakdown: inflow, outflow, net flow, cumulative balance
   - Auto-refresh every 60 seconds

5. **Forecast Generation**
   - One-click forecast update button
   - Progress indicator during generation
   - Success notification with auto-dismiss

#### HTMX Features

- **Auto-Refresh**: Summary cards, alerts, and project tables update automatically
- **Lazy Loading**: Chart data loads asynchronously
- **Progressive Enhancement**: Works without JavaScript, enhanced with it
- **Partial Updates**: Only affected sections re-render on change

#### Dashboard Partials

1. **Summary Partial** (`/portfolio/cashflow/partials/summary/`)
   - Renders 6 metric cards
   - 60-second auto-refresh

2. **Chart Data Partial** (`/portfolio/cashflow/partials/chart-data/`)
   - Returns JSON for Chart.js
   - Called on horizon change

3. **Negative Projects Partial** (`/portfolio/cashflow/partials/negative-projects/`)
   - Table of projects with negative flow
   - 60-second auto-refresh

4. **Alerts Partial** (`/portfolio/cashflow/partials/alerts/`)
   - Critical cash flow warnings
   - 30-second auto-refresh

5. **Generate Success Partial** (`/portfolio/cashflow/generate/`)
   - Success message after forecast generation
   - Auto-dismisses after 5 seconds

---

## Usage Examples

### Example 1: Daily Forecast Update (Cron Job)

```python
#!/usr/bin/env python
"""
Daily cash flow forecast update script.
Run via cron: 0 6 * * * /path/to/update_forecast.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cashflow.services import CashFlowService

# Update all forecasts with 6-month horizon
result = CashFlowService.update_all_forecasts(horizon_months=6)

print(f"✅ Forecast update complete:")
print(f"  - Projects updated: {result['updated_projects']}")
print(f"  - Forecast months: {result['forecast_months']}")
print(f"  - Horizon: {result['horizon_months']} months")
```

### Example 2: Identify Projects Needing Cash Injection

```python
from apps.cashflow import selectors

# Get projects with negative cumulative balance
negative_balance_projects = selectors.get_projects_with_negative_cumulative_balance()

print(f"Projects needing cash injection: {negative_balance_projects.count()}")

for forecast in negative_balance_projects:
    print(f"\nProject: {forecast.project.name}")
    print(f"  Current Balance: KES {forecast.cumulative_cash_balance:,.2f}")
    print(f"  Monthly Net Flow: KES {forecast.net_cash_flow:,.2f}")
    print(f"  Required Injection: KES {abs(forecast.cumulative_cash_balance):,.2f}")
```

### Example 3: Export Cash Flow Report to CSV

```python
import csv
from apps.cashflow import selectors

# Get 12-month portfolio forecast
trend_data = selectors.get_portfolio_cash_flow_trend_data(months=12)

# Export to CSV
with open('portfolio_cashflow_forecast.csv', 'w', newline='') as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=[
        'month', 'inflow', 'outflow', 'net_flow', 
        'cumulative_balance', 'active_projects', 'negative_projects'
    ])
    
    writer.writeheader()
    for month_data in trend_data:
        writer.writerow(month_data)

print("✅ Cash flow report exported to portfolio_cashflow_forecast.csv")
```

### Example 4: JavaScript Chart Integration

```javascript
// Fetch cash flow trend data via API
fetch('/api/cashflow/portfolio/trend/?months=6', {
    headers: {
        'Authorization': `Bearer ${accessToken}`
    }
})
.then(response => response.json())
.then(data => {
    // Create Chart.js chart
    const ctx = document.getElementById('cashFlowChart').getContext('2d');
    
    new Chart(ctx, {
        type: 'line',
        data: {
            labels: data.map(d => d.month_label),
            datasets: [
                {
                    label: 'Inflow',
                    data: data.map(d => d.inflow),
                    borderColor: '#27ae60',
                    fill: false
                },
                {
                    label: 'Outflow',
                    data: data.map(d => d.outflow),
                    borderColor: '#e74c3c',
                    fill: false
                },
                {
                    label: 'Net Flow',
                    data: data.map(d => d.net_flow),
                    borderColor: '#3498db',
                    fill: false
                }
            ]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: {
                        callback: value => `KES ${value.toLocaleString()}`
                    }
                }
            }
        }
    });
});
```

---

## Deployment

### Step 1: Run Migrations

```bash
# On VPS (via Docker)
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate cashflow

# Expected output:
# Running migrations:
#   Applying cashflow.0001_initial... OK
```

### Step 2: Generate Initial Forecasts

```bash
# Access Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Generate forecasts
>>> from apps.cashflow.services import CashFlowService
>>> result = CashFlowService.update_all_forecasts(horizon_months=6)
>>> print(f"Initialized forecasts for {result['updated_projects']} projects")
>>> exit()
```

### Step 3: Verify Dashboard

```bash
# Visit cash flow dashboard
http://your-domain/portfolio/cashflow/

# Verify 6 summary cards display
# Verify chart renders with data
# Verify alerts and negative projects sections load
```

### Step 4: Setup Automated Updates (Optional)

```bash
# Add cron job for daily forecast updates
crontab -e

# Add this line (update forecast daily at 6 AM):
0 6 * * * cd /root/coms && docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell -c "from apps.cashflow.services import CashFlowService; CashFlowService.update_all_forecasts(horizon_months=6)"
```

### Step 5: Test API Endpoints

```bash
# Get JWT token
TOKEN=$(curl -s -X POST http://your-domain/api/auth/login/ \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@test.com","password":"TestPass123!"}' \
  | jq -r '.access')

# Test portfolio forecast endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/portfolio/forecast/?months=6" | jq

# Test alerts endpoint
curl -H "Authorization: Bearer $TOKEN" \
  "http://your-domain/api/cashflow/portfolio/alerts/" | jq
```

---

## Troubleshooting

### Issue 1: No Forecasts Generated

**Symptom:** Dashboard shows "No data available"

**Causes & Solutions:**

1. **No active projects**
   ```bash
   # Check active projects count
   >>> from apps.projects.models import Project
   >>> Project.objects.filter(status__in=['DESIGN', 'APPROVAL', 'IMPLEMENTATION']).count()
   ```

2. **Forecasts not generated**
   ```python
   # Manually generate forecasts
   >>> from apps.cashflow.services import CashFlowService
   >>> CashFlowService.update_all_forecasts(horizon_months=6)
   ```

3. **Database connection issue**
   ```bash
   # Check database connectivity
   docker-compose -f docker-compose.prod.yml exec db psql -U coms_user -d coms_db
   ```

### Issue 2: Inaccurate Forecasts

**Symptom:** Forecasts don't match expectations

**Causes & Solutions:**

1. **Insufficient historical data**
   - Forecasts rely on historical expense patterns
   - Ensure at least 3 months of approved expenses exist
   
2. **Missing valuation approvals**
   ```python
   # Check approved valuations
   >>> from apps.valuations.models import Valuation
   >>> Valuation.objects.filter(status='APPROVED').count()
   ```

3. **Outdated expense data**
   ```bash
   # Re-generate forecasts to use latest data
   curl -X POST -H "Authorization: Bearer $TOKEN" \
     "http://your-domain/api/cashflow/portfolio/generate/?months=6"
   ```

### Issue 3: Dashboard Not Loading

**Symptom:** Dashboard shows loading indicator continuously

**Causes & Solutions:**

1. **HTMX script not loaded**
   - Check browser console for errors
   - Ensure HTMX CDN is accessible
   - Check `base.html` includes HTMX script tag

2. **URL routing issue**
   ```python
   # Verify URL patterns registered
   >>> from django.urls import reverse
   >>> reverse('dashboards:cashflow_dashboard')
   '/portfolio/cashflow/'
   ```

3. **Permission error**
   - Ensure user is logged in
   - Check `@login_required` decorator on views

### Issue 4: Chart Not Rendering

**Symptom:** Chart container is empty

**Causes & Solutions:**

1. **Chart.js not loaded**
   ```html
   <!-- Verify Chart.js script in template -->
   <script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
   ```

2. **JSON data endpoint failing**
   ```bash
   # Test chart data endpoint
   curl "http://your-domain/portfolio/cashflow/partials/chart-data/?months=6"
   ```

3. **JavaScript error**
   - Check browser console for errors
   - Verify `cashFlowChart` canvas element exists

### Issue 5: Negative Balance Alerts Not Showing

**Symptom:** No alerts despite projects having negative balance

**Causes & Solutions:**

1. **Alert threshold too high**
   - Check `get_critical_cash_flow_alerts()` in selectors.py
   - Severe negative flow threshold is KES -100,000
   
2. **Forecasts outdated**
   ```python
   # Re-generate forecasts
   >>> CashFlowService.update_all_forecasts(horizon_months=6)
   ```

3. **All projects healthy**
   - Verify there actually are projects with issues
   ```python
   >>> from apps.cashflow import selectors
   >>> selectors.get_projects_with_negative_cumulative_balance().count()
   ```

---

## Summary

The Cash Flow Forecasting Module provides:

✅ **Complete forecasting engine** with configurable horizons  
✅ **10 RESTful API endpoints** for integrations  
✅ **Interactive HTMX dashboard** with real-time updates  
✅ **Risk identification** via automated alerts  
✅ **Portfolio-wide analytics** for strategic planning  
✅ **Detailed documentation** for developers and operators  

**Next Steps:**

1. Deploy module to VPS (run migrations)
2. Generate initial forecasts
3. Setup daily automated updates
4. Train users on dashboard features
5. Integrate with existing workflows

**Support:**

- API Documentation: `/api/schema/swagger/`
- Repository: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-
- Dashboard: `/portfolio/cashflow/`

---

**Module created:** March 11, 2026  
**Version:** 1.0.0  
**Django App:** `apps.cashflow`  
**Documentation:** Complete ✅
