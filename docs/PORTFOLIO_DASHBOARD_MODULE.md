# Portfolio Dashboard and Forecasting Module

**Complete documentation for COMS Portfolio Analytics system**

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [Service Layer](#service-layer)
5. [Selector Layer](#selector-layer)
6. [API Endpoints](#api-endpoints)
7. [HTMX Dashboard](#htmx-dashboard)
8. [Earned Value Management (EVM)](#earned-value-management)
9. [Risk Assessment](#risk-assessment)
10. [Usage Examples](#usage-examples)
11. [Deployment](#deployment)

---

## Overview

The Portfolio Dashboard and Forecasting Module provides comprehensive analytics across all projects in the COMS platform. It enables:

- **Portfolio-wide financial metrics** - Aggregated revenue, expenses, profit across all projects
- **Project risk indicators** - Automated risk assessment based on multiple factors
- **Earned Value Management (EVM)** - Industry-standard project performance metrics
- **Real-time dashboards** - HTMX-powered interactive dashboards with auto-refresh
- **Forecasting** - Budget completion estimates using CPI/SPI

### Key Features

✅ Automated metric computation with transaction safety  
✅ Earned Value Management (PV, EV, AC, CPI, SPI)  
✅ Multi-factor risk assessment (budget, schedule, cost, profit)  
✅ RESTful API with comprehensive filtering  
✅ Interactive HTMX dashboard with real-time updates  
✅ Historical tracking of metrics over time  

---

## Architecture

### Application Structure

```
apps/portfolio/
├── __init__.py
├── apps.py
├── models.py           # ProjectMetrics model
├── services.py         # Business logic for metric computation
├── selectors.py        # Query optimization layer
├── admin.py            # Admin interface
├── tests.py            # Unit tests
└── migrations/
    └── 0001_initial.py

api/
├── serializers/
│   └── portfolio.py    # API serializers
└── views/
    └── portfolio.py    # ViewSets (PortfolioViewSet, ProjectMetricsViewSet)

templates/dashboards/
├── portfolio_dashboard.html
└── partials/
    ├── portfolio_summary.html
    ├── portfolio_projects_table.html
    ├── portfolio_risk_distribution.html
    └── portfolio_high_risk.html
```

### Design Patterns

**Service Pattern:**
- All business logic in `services.py`
- Transaction-safe operations with `@transaction.atomic`
- Clear separation of concerns

**Selector Pattern:**
- All queries in `selectors.py`
- Query optimization with `select_related()`, `prefetch_related()`
- No business logic in selectors

**Thin Views:**
- Controllers delegate to services and selectors
- Views handle HTTP concerns only

---

## Data Models

### ProjectMetrics Model

Stores computed performance metrics for each project.

```python
class ProjectMetrics(models.Model):
    """
    Stores computed metrics for project performance tracking
    Updated periodically (daily/weekly) or on-demand
    """
    
    # Relationship
    project = OneToOneField(Project, on_delete=CASCADE)
    
    # Financial Metrics
    total_contract_value = DecimalField(max_digits=15, decimal_places=2)
    total_expenses = DecimalField(max_digits=15, decimal_places=2)
    total_revenue = DecimalField(max_digits=15, decimal_places=2)
    total_profit = DecimalField(max_digits=15, decimal_places=2)
    
    # Performance Indicators
    budget_utilization = DecimalField(max_digits=5, decimal_places=2)  # %
    profit_margin = DecimalField(max_digits=5, decimal_places=2)       # %
    
    # Risk Assessment
    project_health = CharField(
        choices=['EXCELLENT', 'GOOD', 'WARNING', 'CRITICAL']
    )
    risk_level = CharField(
        choices=['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
    )
    
    # Earned Value Management
    planned_value = DecimalField(max_digits=15, decimal_places=2)      # PV
    earned_value = DecimalField(max_digits=15, decimal_places=2)       # EV
    actual_cost = DecimalField(max_digits=15, decimal_places=2)        # AC
    cost_performance_index = DecimalField(max_digits=5, decimal_places=2)      # CPI
    schedule_performance_index = DecimalField(max_digits=5, decimal_places=2)  # SPI
    
    # Schedule Metrics
    days_elapsed = IntegerField()
    days_remaining = IntegerField()
    schedule_variance_days = IntegerField()
    
    # Flags
    is_over_budget = BooleanField()
    is_behind_schedule = BooleanField()
    
    # Metadata
    last_updated = DateTimeField(auto_now=True)
    created_at = DateTimeField(auto_now_add=True)
```

**Database Table:** `project_metrics`

**Indexes:**
- `(project, last_updated)` - For efficient project lookups
- `risk_level` - For filtering by risk
- `project_health` - For filtering by health

**Unique Constraints:**
- `project` - OneToOne relationship ensures one metrics record per project

---

## Service Layer

### PortfolioAnalyticsService

All business logic for computing portfolio metrics.

#### compute_project_risk_indicators(project_id: str) → ProjectMetrics

Computes comprehensive risk indicators and performance metrics for a project.

**Business Rules:**

| Metric | Condition | Risk Impact |
|--------|-----------|-------------|
| Budget Utilization | > 100% | CRITICAL - Over budget |
| Budget Utilization | 90-100% | WARNING |
| CPI (Cost Performance) | < 0.8 | CRITICAL - Significant cost overrun |
| CPI | 0.8-0.9 | HIGH - Cost overrun |
| CPI | 0.9-0.95 | MEDIUM - Minor cost issue |
| SPI (Schedule Performance) | < 0.8 | CRITICAL - Significantly behind |
| SPI | 0.8-0.9 | HIGH - Behind schedule |
| Profit Margin | < 0% | CRITICAL - Losing money |
| Profit Margin | 0-5% | HIGH - Low margin |
| Profit Margin | 5-10% | MEDIUM |

**Example Usage:**

```python
from apps.portfolio.services import PortfolioAnalyticsService

# Compute metrics for a specific project
metrics = PortfolioAnalyticsService.compute_project_risk_indicators(
    project_id='550e8400-e29b-41d4-a716-446655440000'
)

print(f"Risk Level: {metrics.risk_level}")
print(f"Budget Utilization: {metrics.budget_utilization}%")
print(f"CPI: {metrics.cost_performance_index}")
print(f"SPI: {metrics.schedule_performance_index}")
```

**Computed Fields:**

1. **Financial Metrics**
   - `total_contract_value` - From `Project.project_value`
   - `total_expenses` - Sum of approved expenses
   - `total_revenue` - Sum of client payments
   - `total_profit` - Revenue - Expenses
   - `budget_utilization` - (Expenses / Contract Value) × 100
   - `profit_margin` - (Profit / Revenue) × 100

2. **EVM Metrics (via _compute_earned_value_metrics)**
   - `planned_value` - (Days Elapsed / Total Days) × Contract Value
   - `earned_value` - Latest approved valuation work value
   - `actual_cost` - Total approved expenses
   - `cost_performance_index` - EV / AC
   - `schedule_performance_index` - EV / PV

3. **Schedule Metrics (via _compute_schedule_metrics)**
   - `days_elapsed` - Today - Start Date
   - `days_remaining` - End Date - Today
   - `schedule_variance_days` - Based on work progress

4. **Risk & Health (via _determine_risk_level & _determine_project_health)**
   - Multi-factor assessment combining budget, cost, schedule, profit

---

#### compute_portfolio_summary() → Dict

Computes portfolio-wide summary statistics.

**Returns:**

```python
{
    'active_projects': 15,
    'total_contract_value': Decimal('50000000.00'),
    'total_expenses': Decimal('35000000.00'),
    'total_revenue': Decimal('40000000.00'),
    'total_profit': Decimal('5000000.00'),
    'projects_over_budget': 2,
    'projects_behind_schedule': 3,
    'high_risk_projects': 4,
    'avg_budget_utilization': Decimal('70.50'),
    'avg_profit_margin': Decimal('12.50'),
}
```

**Example Usage:**

```python
summary = PortfolioAnalyticsService.compute_portfolio_summary()
print(f"Active Projects: {summary['active_projects']}")
print(f"Total Profit: KES {summary['total_profit']:,.2f}")
print(f"High Risk Projects: {summary['high_risk_projects']}")
```

---

#### update_all_project_metrics() → int

Updates metrics for all active projects (batch operation).

**Returns:** Number of projects updated

**Example Usage:**

```python
# Update all project metrics (e.g., in a daily cron job)
updated_count = PortfolioAnalyticsService.update_all_project_metrics()
print(f"Updated {updated_count} projects")
```

**Recommended Schedule:**
- Run daily at off-peak hours
- Or trigger after major data changes (valuations, expenses, payments)

---

## Selector Layer

### Portfolio Selectors

All query operations with optimization.

#### get_portfolio_summary() → Dict

```python
from apps.portfolio import selectors

summary = selectors.get_portfolio_summary()
# Returns same as PortfolioAnalyticsService.compute_portfolio_summary()
```

#### get_high_risk_projects() → QuerySet[ProjectMetrics]

```python
high_risk = selectors.get_high_risk_projects()
# Returns projects with risk_level in ['HIGH', 'CRITICAL']
# Optimized with select_related('project', 'project__organization')
```

#### get_projects_over_budget() → QuerySet[ProjectMetrics]

```python
over_budget = selectors.get_projects_over_budget()
# Returns projects where is_over_budget=True
```

#### get_projects_behind_schedule() → QuerySet[ProjectMetrics]

```python
delayed = selectors.get_projects_behind_schedule()
# Returns projects where is_behind_schedule=True
```

#### get_project_metrics(project_id: str) → Optional[ProjectMetrics]

```python
metrics = selectors.get_project_metrics('550e8400-...')
if metrics:
    print(f"CPI: {metrics.cost_performance_index}")
```

#### get_evm_summary_for_project(project_id: str) → Dict

```python
evm = selectors.get_evm_summary_for_project('550e8400-...')
# Returns:
# {
#     'planned_value': ...,
#     'earned_value': ...,
#     'actual_cost': ...,
#     'cost_variance': EV - AC,
#     'schedule_variance': EV - PV,
#     'cost_performance_index': ...,
#     'schedule_performance_index': ...,
#     'estimate_at_completion': BAC / CPI,
#     'variance_at_completion': BAC - EAC,
#     'budget_at_completion': ...,
# }
```

---

## API Endpoints

### Portfolio Summary Endpoint

**Endpoint:** `GET /api/portfolio/summary/`

**Description:** Returns comprehensive portfolio-wide metrics.

**Response:**

```json
{
  "active_projects": 15,
  "total_contract_value": "50000000.00",
  "total_expenses": "35000000.00",
  "total_revenue": "40000000.00",
  "total_profit": "5000000.00",
  "projects_over_budget": 2,
  "projects_behind_schedule": 3,
  "high_risk_projects": 4,
  "avg_budget_utilization": "70.50",
  "avg_profit_margin": "12.50"
}
```

**Example cURL:**

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/api/portfolio/summary/
```

---

### Risk Distribution

**Endpoint:** `GET /api/portfolio/risk-distribution/`

**Response:**

```json
{
  "low": 5,
  "medium": 6,
  "high": 3,
  "critical": 1
}
```

---

### Health Distribution

**Endpoint:** `GET /api/portfolio/health-distribution/`

**Response:**

```json
{
  "excellent": 4,
  "good": 7,
  "warning": 3,
  "critical": 1
}
```

---

### Update All Metrics

**Endpoint:** `POST /api/portfolio/update-metrics/`

**Description:** Triggers recalculation of all project metrics.

**Response:**

```json
{
  "message": "Successfully updated metrics for 15 projects",
  "updated_count": 15
}
```

---

### Project Metrics List

**Endpoint:** `GET /api/project-metrics/`

**Query Parameters:**
- `risk_level` - Filter by: LOW, MEDIUM, HIGH, CRITICAL
- `health` - Filter by: EXCELLENT, GOOD, WARNING, CRITICAL
- `over_budget` - Filter: true/false
- `behind_schedule` - Filter: true/false

**Example:**

```bash
# Get all high-risk projects
GET /api/project-metrics/?risk_level=HIGH

# Get projects over budget
GET /api/project-metrics/?over_budget=true

# Get projects with critical health
GET /api/project-metrics/?health=CRITICAL
```

**Response:**

```json
{
  "count": 150,
  "next": "http://localhost:8000/api/project-metrics/?page=2",
  "previous": null,
  "results": [
    {
      "id": "uuid",
      "project_code": "PRJ-001",
      "project_name": "Residential Complex",
      "project_status": "IMPLEMENTATION",
      "risk_level": "HIGH",
      "project_health": "WARNING",
      "budget_utilization": "95.50",
      "profit_margin": "8.25",
      "cost_performance_index": "0.92",
      "schedule_performance_index": "0.88",
      "is_over_budget": false,
      "is_behind_schedule": true,
      "last_updated": "2026-03-11T10:30:00Z"
    }
  ]
}
```

---

### Project Metrics Detail

**Endpoint:** `GET /api/project-metrics/{id}/`

**Response:** Full metrics including project details and all EVM data.

---

### EVM Summary for Project

**Endpoint:** `GET /api/project-metrics/{id}/evm-summary/`

**Response:**

```json
{
  "planned_value": "25000000.00",
  "earned_value": "22000000.00",
  "actual_cost": "24000000.00",
  "cost_variance": "-2000000.00",
  "schedule_variance": "-3000000.00",
  "cost_performance_index": "0.92",
  "schedule_performance_index": "0.88",
  "estimate_at_completion": "54347826.09",
  "variance_at_completion": "-4347826.09",
  "budget_at_completion": "50000000.00"
}
```

**Interpretation:**
- `CPI = 0.92` → Project is over budget (spending $1.09 for every $1 of work)
- `SPI = 0.88` → Project is behind schedule (88% of planned work completed)
- `CV = -2M` → Cost overrun of 2 million
- `SV = -3M` → Behind schedule by 3 million in value
- `EAC = 54M` → Projected final cost will be 54M (4M over budget)

---

### Update Single Project Metrics

**Endpoint:** `POST /api/project-metrics/{id}/update/`

**Description:** Recalculates metrics for a specific project.

**Response:** Updated ProjectMetrics object

---

### High Risk Projects

**Endpoint:** `GET /api/project-metrics/high-risk/`

**Description:** Returns all HIGH and CRITICAL risk projects.

---

### Attention Required

**Endpoint:** `GET /api/project-metrics/attention-required/`

**Description:** Returns projects with any of: high risk, over budget, or behind schedule.

---

## HTMX Dashboard

### Main Dashboard

**URL:** `/portfolio/`

**Features:**
- Real-time portfolio summary with auto-refresh (every 30s)
- Risk distribution visualization
- High-risk projects alert list
- Complete projects table with filtering
- Manual metrics update button

**Filters:**
- Risk Level dropdown
- Health Status dropdown
- "Attention Required Only" checkbox

**HTMX Partials (auto-updated):**

1. **Portfolio Summary** - `/portfolio/partials/summary/` (30s refresh)
2. **Risk Distribution** - `/portfolio/partials/risk-distribution/` (60s refresh)
3. **High Risk Projects** - `/portfolio/partials/high-risk-projects/` (60s refresh)
4. **Projects Table** - `/portfolio/partials/projects-table/` (on filter change)

**Screenshots:**

![Portfolio Summary Cards](docs/images/portfolio-summary.png)
![Risk Distribution](docs/images/risk-distribution.png)
![Projects Table](docs/images/projects-table.png)

---

## Earned Value Management

### What is EVM?

Earned Value Management (EVM) is an industry-standard project management methodology that integrates schedule, cost, and work performance.

### Key Metrics

#### Planned Value (PV)
**Formula:** `(Days Elapsed / Total Days) × Contract Value`

**Meaning:** Budgeted amount for work scheduled to be completed by now.

**Example:** Project budget: $100K, 100 days total, 50 days elapsed → PV = $50K

---

#### Earned Value (EV)
**Formula:** Based on latest approved valuation's work completed value

**Meaning:** Budgeted amount for work actually completed.

**Example:** If 40% of work is done, and budget is $100K → EV = $40K

---

#### Actual Cost (AC)
**Formula:** Sum of all approved expenses

**Meaning:** Total money spent to date.

**Example:** All expenses sum to $55K → AC = $55K

---

#### Cost Performance Index (CPI)
**Formula:** `CPI = EV / AC`

**Interpretation:**
- `CPI > 1.0` → Under budget (good!)
- `CPI = 1.0` → On budget
- `CPI < 1.0` → Over budget (warning!)

**Example:** EV = $40K, AC = $55K → CPI = 0.73 (spending $1.37 for every $1 of work)

---

#### Schedule Performance Index (SPI)
**Formula:** `SPI = EV / PV`

**Interpretation:**
- `SPI > 1.0` → Ahead of schedule
- `SPI = 1.0` → On schedule
- `SPI < 1.0` → Behind schedule

**Example:** EV = $40K, PV = $50K → SPI = 0.80 (only 80% of planned work done)

---

#### Estimate at Completion (EAC)
**Formula:** `EAC = BAC / CPI`

where `BAC` (Budget at Completion) = Total Contract Value

**Meaning:** Projected final cost based on current performance.

**Example:** BAC = $100K, CPI = 0.73 → EAC = $137K (project will cost $37K more than budget)

---

#### Variance at Completion (VAC)
**Formula:** `VAC = BAC - EAC`

**Meaning:** Expected over/under budget at project completion.

**Example:** BAC = $100K, EAC = $137K → VAC = -$37K (will be $37K over budget)

---

### EVM Dashboard Visualization

The portfolio dashboard displays:

1. **CPI with color coding:**
   - Green (≥ 0.95): On budget
   - Yellow (0.90-0.95): Minor overrun
   - Red (< 0.90): Significant overrun

2. **SPI with color coding:**
   - Green (≥ 0.95): On schedule
   - Yellow (0.90-0.95): Minor delay
   - Red (< 0.90): Significant delay

3. **Budget Utilization Bar:**
   - Shows % of budget used with color alerts

---

## Risk Assessment

### Multi-Factor Risk Algorithm

The system uses a weighted scoring system across 4 dimensions:

#### 1. Budget Utilization Score

| Utilization | Flag | Weight |
|-------------|------|--------|
| > 100% | CRITICAL | 3 |
| 90-100% | HIGH | 2 |
| 80-90% | MEDIUM | 1 |
| < 80% | OK | 0 |

#### 2. Profit Margin Score

| Margin | Flag | Weight |
|--------|------|--------|
| < 0% | CRITICAL | 3 |
| 0-5% | HIGH | 2 |
| 5-10% | MEDIUM | 1 |
| > 10% | OK | 0 |

#### 3. Cost Performance (CPI) Score

| CPI | Flag | Weight |
|-----|------|--------|
| < 0.80 | CRITICAL | 3 |
| 0.80-0.90 | HIGH | 2 |
| 0.90-0.95 | MEDIUM | 1 |
| ≥ 0.95 | OK | 0 |

#### 4. Schedule Performance (SPI) Score

| SPI | Flag | Weight |
|-----|------|--------|
| < 0.80 | CRITICAL | 3 |
| 0.80-0.90 | HIGH | 2 |
| 0.90-0.95 | MEDIUM | 1 |
| ≥ 0.95 | OK | 0 |

### Final Risk Determination

```python
critical_flags = sum(flags with weight 3)
high_flags = sum(flags with weight 2)
medium_flags = sum(flags with weight 1)

if critical_flags >= 2 or (critical_flags >= 1 and high_flags >= 2):
    risk_level = 'CRITICAL'
elif critical_flags >= 1 or high_flags >= 2:
    risk_level = 'HIGH'
elif high_flags >= 1 or medium_flags >= 2:
    risk_level = 'MEDIUM'
else:
    risk_level = 'LOW'
```

---

## Usage Examples

### Example 1: Daily Metrics Update (Cron Job)

```python
# Script: update_portfolio_metrics.py
from apps.portfolio.services import PortfolioAnalyticsService

def main():
    """Daily portfolio metrics update"""
    print("Starting portfolio metrics update...")
    
    updated_count = PortfolioAnalyticsService.update_all_project_metrics()
    
    print(f"✓ Updated {updated_count} projects")
    
    # Get summary
    summary = PortfolioAnalyticsService.compute_portfolio_summary()
    print(f"Active Projects: {summary['active_projects']}")
    print(f"High Risk Projects: {summary['high_risk_projects']}")
    print(f"Projects Over Budget: {summary['projects_over_budget']}")

if __name__ == '__main__':
    main()
```

**Cron Schedule (Linux):**
```bash
# Run daily at 2 AM
0 2 * * * cd /path/to/coms && python manage.py shell < update_portfolio_metrics.py
```

---

### Example 2: Get High-Risk Projects Report

```python
from apps.portfolio import selectors

def generate_risk_report():
    """Generate high-risk projects report"""
    high_risk = selectors.get_high_risk_projects()
    
    print("HIGH RISK PROJECTS REPORT")
    print("=" * 60)
    
    for metrics in high_risk:
        print(f"\nProject: {metrics.project.code} - {metrics.project.name}")
        print(f"  Risk Level: {metrics.get_risk_level_display()}")
        print(f"  Health: {metrics.get_project_health_display()}")
        print(f"  Budget Utilization: {metrics.budget_utilization}%")
        print(f"  Profit Margin: {metrics.profit_margin}%")
        print(f"  CPI: {metrics.cost_performance_index}")
        print(f"  SPI: {metrics.schedule_performance_index}")
        
        if metrics.is_over_budget:
            print("  ⚠️ OVER BUDGET")
        if metrics.is_behind_schedule:
            print("  ⚠️ BEHIND SCHEDULE")

generate_risk_report()
```

---

### Example 3: Project EVM Analysis

```python
from apps.portfolio import selectors

def analyze_project_evm(project_id):
    """Detailed EVM analysis for a project"""
    evm = selectors.get_evm_summary_for_project(project_id)
    
    print("EARNED VALUE ANALYSIS")
    print("=" * 60)
    print(f"Budget at Completion (BAC): ${evm['budget_at_completion']:,.2f}")
    print(f"Planned Value (PV): ${evm['planned_value']:,.2f}")
    print(f"Earned Value (EV): ${evm['earned_value']:,.2f}")
    print(f"Actual Cost (AC): ${evm['actual_cost']:,.2f}")
    print()
    print(f"Cost Variance (CV): ${evm['cost_variance']:,.2f}")
    print(f"Schedule Variance (SV): ${evm['schedule_variance']:,.2f}")
    print()
    print(f"Cost Performance Index (CPI): {evm['cost_performance_index']:.2f}")
    print(f"Schedule Performance Index (SPI): {evm['schedule_performance_index']:.2f}")
    print()
    print(f"Estimate at Completion (EAC): ${evm['estimate_at_completion']:,.2f}")
    print(f"Variance at Completion (VAC): ${evm['variance_at_completion']:,.2f}")
    print()
    
    # Interpretation
    if evm['cost_performance_index'] < 1.0:
        print("⚠️ PROJECT IS OVER BUDGET")
        overspend_pct = (1 - evm['cost_performance_index']) * 100
        print(f"   Spending {overspend_pct:.1f}% more than planned")
    
    if evm['schedule_performance_index'] < 1.0:
        print("⚠️ PROJECT IS BEHIND SCHEDULE")
        behind_pct = (1 - evm['schedule_performance_index']) * 100
        print(f"   {behind_pct:.1f}% behind planned progress")

# Example: Analyze project
analyze_project_evm('550e8400-e29b-41d4-a716-446655440000')
```

---

### Example 4: API Integration (JavaScript)

```javascript
// Fetch portfolio summary
async function getPortfolioSummary() {
    const response = await fetch('/api/portfolio/summary/', {
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'Content-Type': 'application/json'
        }
    });
    
    const data = await response.json();
    
    console.log(`Active Projects: ${data.active_projects}`);
    console.log(`Total Revenue: KES ${data.total_revenue}`);
    console.log(`High Risk Projects: ${data.high_risk_projects}`);
    
    return data;
}

// Update all metrics
async function updateAllMetrics() {
    const response = await fetch('/api/portfolio/update-metrics/', {
        method: 'POST',
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`,
            'Content-Type': 'application/json'
        }
    });
    
    const result = await response.json();
    console.log(result.message);
    return result;
}

// Filter high-risk projects
async function getHighRiskProjects() {
    const response = await fetch('/api/project-metrics/?risk_level=HIGH', {
        headers: {
            'Authorization': `Bearer ${getJWTToken()}`
        }
    });
    
    const data = await response.json();
    return data.results;
}
```

---

## Deployment

### 1. Run Migrations

```bash
python manage.py migrate portfolio
```

### 2. Initial Metrics Computation

```bash
python manage.py shell
```

```python
from apps.portfolio.services import PortfolioAnalyticsService

# Update all project metrics
updated = PortfolioAnalyticsService.update_all_project_metrics()
print(f"Initialized metrics for {updated} projects")
```

### 3. Setup Cron Job (Optional)

For automatic daily updates:

```bash
crontab -e
```

Add:
```
0 2 * * * cd /path/to/coms && docker-compose exec web python manage.py shell -c "from apps.portfolio.services import PortfolioAnalyticsService; PortfolioAnalyticsService.update_all_project_metrics()"
```

### 4. Access Dashboard

Navigate to: `http://your-domain/portfolio/`

---

## Testing

### Unit Tests

```python
# tests.py
from django.test import TestCase
from apps.portfolio.services import PortfolioAnalyticsService
from apps.projects.models import Project

class PortfolioAnalyticsTestCase(TestCase):
    
    def test_compute_project_metrics(self):
        """Test project metrics computation"""
        project = Project.objects.create(
            name="Test Project",
            code="TST-001",
            project_value=1000000.00
        )
        
        metrics = PortfolioAnalyticsService.compute_project_risk_indicators(
            str(project.id)
        )
        
        self.assertIsNotNone(metrics)
        self.assertEqual(metrics.project, project)
        self.assertIn(metrics.risk_level, ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
```

Run tests:
```bash
python manage.py test apps.portfolio
```

---

## Troubleshooting

### Metrics Not Updating

**Problem:** Metrics show old data

**Solution:**
```python
from apps.portfolio.services import PortfolioAnalyticsService

# Force update for specific project
metrics = PortfolioAnalyticsService.compute_project_risk_indicators(project_id)

# Or update all
PortfolioAnalyticsService.update_all_project_metrics()
```

### Division by Zero Errors

**Problem:** CPI/SPI calculation errors

**Reason:** Project has no actual costs or planned value

**Solution:** Service handles this gracefully by defaulting to 1.0

### Missing Metrics Records

**Problem:** Project has no metrics

**Solution:** Metrics are created automatically on first computation. Run:
```python
PortfolioAnalyticsService.compute_project_risk_indicators(project_id)
```

---

## API Reference Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/portfolio/summary/` | GET | Portfolio-wide summary |
| `/api/portfolio/risk-distribution/` | GET | Risk distribution counts |
| `/api/portfolio/health-distribution/` | GET | Health distribution counts |
| `/api/portfolio/update-metrics/` | POST | Update all project metrics |
| `/api/project-metrics/` | GET | List all project metrics with filtering |
| `/api/project-metrics/{id}/` | GET | Get single project metrics |
| `/api/project-metrics/{id}/evm-summary/` | GET | Detailed EVM analysis |
| `/api/project-metrics/{id}/update/` | POST | Update single project metrics |
| `/api/project-metrics/high-risk/` | GET | High/critical risk projects |
| `/api/project-metrics/attention-required/` | GET | Projects needing attention |

---

## Dashboard URL Summary

| URL | Description |
|-----|-------------|
| `/portfolio/` | Main portfolio dashboard |
| `/portfolio/partials/summary/` | HTMX: Portfolio summary cards |
| `/portfolio/partials/projects-table/` | HTMX: All projects table |
| `/portfolio/partials/risk-distribution/` | HTMX: Risk distribution chart |
| `/portfolio/partials/high-risk-projects/` | HTMX: High risk projects list |

---

**Module Version:** 1.0.0  
**Last Updated:** March 11, 2026  
**Author:** COMS Team
