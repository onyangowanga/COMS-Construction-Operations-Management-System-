# Reporting Engine Module

The Reporting Engine provides comprehensive reporting capabilities for the COMS platform, including automated report generation, multiple export formats, scheduled execution, and dashboard widgets.

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Report Types](#report-types)
4. [Export Formats](#export-formats)
5. [API Reference](#api-reference)
6. [Scheduling](#scheduling)
7. [Dashboard Widgets](#dashboard-widgets)
8. [Usage Examples](#usage-examples)
9. [Deployment](#deployment)

---

## Overview

### Key Features

- **6 Pre-built Report Types**: Project Financial, Cash Flow, Variation Impact, Subcontractor Payment, Document Audit, Procurement Summary
- **4 Export Formats**: PDF, Excel, CSV, JSON
- **Scheduled Execution**: Daily, Weekly, Monthly, Quarterly, Custom (cron)
- **Redis Caching**: Configurable cache duration for improved performance
- **Dashboard Widgets**: 6 built-in data sources for KPIs and charts
- **Pandas Integration**: Advanced data aggregation and DataFrame processing
- **Query Optimization**: select_related/prefetch_related throughout
- **Email Delivery**: Support for scheduled report delivery
- **Execution Tracking**: Comprehensive history with error logging

### Technology Stack

- **Django 4.2+** with PostgreSQL
- **Django REST Framework** for API endpoints
- **Pandas** for data aggregation
- **ReportLab** for PDF generation
- **openpyxl** for Excel export
- **Redis** for caching
- **Celery** for scheduled execution

---

## Architecture

### Layer Structure

```
apps/reporting/
├── models.py           # 4 models (Report, ReportSchedule, ReportExecution, ReportWidget)
├── selectors.py        # 8 selector classes with optimized queries
├── services.py         # 5 service classes (generation, export, scheduling)
├── admin.py            # Admin interface with status badges
├── tasks.py            # Celery tasks for scheduled execution
└── migrations/         # Database migrations

api/
├── serializers/
│   └── reporting.py    # 10+ serializers for API
└── views/
    └── reporting.py    # 4 ViewSets with custom actions
```

### Models

#### 1. Report
Configuration for report types and parameters.

**Key Fields:**
- `report_type`: PROJECT_FINANCIAL, CASH_FLOW, VARIATION_IMPACT, SUBCONTRACTOR_PAYMENT, DOCUMENT_AUDIT, PROCUREMENT_SUMMARY, CUSTOM
- `export_format`: PDF, EXCEL, CSV, JSON (default format)
- `default_parameters`: JSONField for default report parameters
- `cache_duration`: Cache duration in seconds (0 = no caching)
- `is_public`: Public visibility flag
- `is_active`: Active status

**Properties:**
- `total_executions`: Total execution count
- `last_execution`: Most recent execution

#### 2. ReportSchedule
Scheduled report execution configuration.

**Key Fields:**
- `frequency`: DAILY, WEEKLY, MONTHLY, QUARTERLY, CUSTOM
- `cron_expression`: For custom frequency (requires croniter)
- `delivery_method`: EMAIL, DASHBOARD, STORAGE, ALL
- `recipients`: ArrayField of email addresses
- `next_run`: Next scheduled execution time

**Properties:**
- `is_due`: True if next_run <= now

#### 3. ReportExecution
Execution history and results.

**Key Fields:**
- `status`: PENDING, PROCESSING, COMPLETED, FAILED, CACHED
- `file_path`: Generated file path
- `file_size`: File size in bytes
- `row_count`: Number of data rows
- `execution_time`: Execution duration in seconds
- `error_message`: Error description (if failed)
- `stack_trace`: Full stack trace for debugging
- `cache_key`: Redis cache key (MD5 hash)

**Properties:**
- `is_cached`: True if execution was served from cache
- `was_successful`: True if status is COMPLETED or CACHED
- `duration`: timedelta between created_at and completed_at

#### 4. ReportWidget
Dashboard widget configuration.

**Key Fields:**
- `widget_type`: KPI, CHART, TABLE, GAUGE, TREND
- `chart_type`: LINE, BAR, PIE, DONUT, AREA
- `data_source`: Built-in data source identifier
- `query_parameters`: JSONField for custom parameters
- `display_order`: Widget sort order
- `refresh_interval`: Auto-refresh interval in seconds

---

## Report Types

### 1. Project Financial Summary

**Description:** Comprehensive financial overview of a project.

**Data Sources:**
- Valuations (certified, paid, retention)
- Variation Orders (approved, pending)
- Subcontracts (certified, paid costs)
- Supplier Invoices (invoiced, paid)
- Consultant Payments
- Other Expenses

**Metrics (20+):**
- Contract Value
- Approved Variations
- Revised Contract Value
- Total Certified Revenue
- Total Received Revenue
- Retention Held
- Outstanding Receivables
- Subcontractor Costs (certified, paid, outstanding)
- Supplier Costs (invoiced, paid, outstanding)
- Consultant Costs
- Other Expenses
- Total Costs
- Gross Profit
- Profit Margin %
- Completion Percentage
- Net Cash Flow

**Parameters:**
```json
{
  "project_id": "uuid",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

**Export Formats:**
- **PDF**: Styled table with financial summary
- **Excel**: Formatted metrics with £ number format
- **CSV/JSON**: Raw data export

### 2. Cash Flow Forecast

**Description:** Revenue and expense forecasts for upcoming periods.

**Data Sources:**
- Pending Valuation Claims
- Pending Subcontractor Claims
- Pending Supplier Invoices

**Metrics:**
- Revenue Forecast (by month)
- Expense Forecast (by month)
- Net Cash Flow (by month)
- Outstanding Claims
- Upcoming Payments

**Parameters:**
```json
{
  "project_id": "uuid",
  "months": 12
}
```

### 3. Variation Impact Report

**Description:** Analysis of variation orders and their financial impact.

**Data Sources:**
- Variation Orders

**Metrics:**
- Total Variation Count
- Approved Count / Value
- Rejected Count / Value
- Pending Count / Value
- Average Variation Value
- Variation DataFrame (all variations with details)

**Parameters:**
```json
{
  "project_id": "uuid",
  "status": "APPROVED" // Optional filter
}
```

### 4. Subcontractor Payment Report

**Description:** Payment tracking by subcontractor.

**Data Sources:**
- Subcontract Agreements
- Subcontract Claims

**Metrics (Per Subcontractor):**
- Total Claimed
- Total Certified
- Total Paid
- Outstanding Balance
- Claim Count

**Parameters:**
```json
{
  "project_id": "uuid",
  "organization_id": "uuid",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

### 5. Document Audit Report

**Description:** Document activity audit trail.

**Data Sources:**
- Project Documents

**Metrics:**
- Total Document Count
- Total Signed Count
- Total File Size (MB)
- Documents by Type
- Documents DataFrame (with details)

**Parameters:**
```json
{
  "project_id": "uuid",
  "organization_id": "uuid",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

### 6. Procurement Summary

**Description:** Purchase orders and supplier invoice summary.

**Data Sources:**
- Local Purchase Orders
- Supplier Invoices

**Metrics:**
- Total PO Count / Value
- Approved PO Count / Value
- Pending PO Count / Value
- Total Invoice Count
- Total Invoiced / Paid
- Top 10 Suppliers (by value)
- Procurement DataFrame

**Parameters:**
```json
{
  "project_id": "uuid",
  "organization_id": "uuid",
  "start_date": "2026-01-01",
  "end_date": "2026-03-31"
}
```

---

## Export Formats

### 1. PDF

**Technology:** ReportLab

**Features:**
- A4 page size
- Custom title with organization branding
- Styled tables with:
  - Blue headers (#3498db)
  - White header text
  - Grey borders (#7f8c8d)
  - Alternating row backgrounds
  - Right-aligned numbers
- Information section (generated date, project, period)
- Page numbers (optional)

**Sample Usage:**
```python
from apps.reporting.services import ReportService

execution = ReportService.generate_report(
    report=report,
    parameters={'project_id': project.id},
    export_format='PDF',
    executed_by=user
)

# File saved to: MEDIA_ROOT/reports/report_{execution_id}.pdf
```

### 2. Excel

**Technology:** openpyxl

**Features:**
- Formatted workbook with:
  - Bold white headers
  - Blue header fill (#3498DB)
  - Thin borders
  - Number format: £#,##0.00 for currency
  - Auto-sized columns (max 50 width)
- Merged title cell
- Generated date and project info
- Multiple sheets for complex reports

**Sample Usage:**
```python
execution = ReportService.generate_report(
    report=report,
    parameters={'project_id': project.id},
    export_format='EXCEL',
    executed_by=user
)

# File saved to: MEDIA_ROOT/reports/report_{execution_id}.xlsx
```

### 3. CSV

**Technology:** Pandas DataFrame

**Features:**
- Simple CSV export
- UTF-8 encoding
- Header row included
- Ideal for data analysis and import into other systems

**Sample Usage:**
```python
execution = ReportService.generate_report(
    report=report,
    parameters={'project_id': project.id},
    export_format='CSV',
    executed_by=user
)

# File saved to: MEDIA_ROOT/reports/report_{execution_id}.csv
```

### 4. JSON

**Technology:** Custom DecimalEncoder

**Features:**
- Structured JSON export
- Decimal → float conversion
- datetime → ISO format
- Indented output (2 spaces)
- Ideal for API consumption and data exchange

**Sample Usage:**
```python
execution = ReportService.generate_report(
    report=report,
    parameters={'project_id': project.id},
    export_format='JSON',
    executed_by=user
)

# File saved to: MEDIA_ROOT/reports/report_{execution_id}.json
```

---

## API Reference

### Base URL

```
https://api.example.com/api/
```

### Authentication

All endpoints require JWT authentication:

```
Authorization: Bearer {access_token}
```

---

### Report Endpoints

#### List Reports

```http
GET /api/reports/
```

**Query Parameters:**
- `report_type`: Filter by report type (e.g., PROJECT_FINANCIAL)
- `is_active`: Filter by active status (true/false)
- `is_public`: Filter by public visibility (true/false)
- `search`: Search by name or description

**Response:**
```json
[
  {
    "id": "uuid",
    "organization": "uuid",
    "name": "Project Financial Summary",
    "description": "Comprehensive financial overview",
    "report_type": "PROJECT_FINANCIAL",
    "default_parameters": {},
    "is_active": true,
    "is_public": false,
    "cache_duration": 300,
    "created_by": {
      "id": "uuid",
      "username": "john.doe",
      "first_name": "John",
      "last_name": "Doe"
    },
    "created_at": "2026-03-10T10:00:00Z",
    "updated_at": "2026-03-10T10:00:00Z",
    "total_executions": 15,
    "last_execution": {
      "status": "COMPLETED",
      "created_at": "2026-03-11T09:30:00Z"
    }
  }
]
```

#### Create Report

```http
POST /api/reports/
```

**Request Body:**
```json
{
  "name": "Monthly Financial Report",
  "description": "Monthly financial summary for all projects",
  "report_type": "PROJECT_FINANCIAL",
  "default_parameters": {
    "start_date": "2026-03-01",
    "end_date": "2026-03-31"
  },
  "is_public": false,
  "cache_duration": 600
}
```

**Response:** 201 Created

#### Get Report

```http
GET /api/reports/{id}/
```

**Response:** Report object (see above)

#### Update Report

```http
PUT /api/reports/{id}/
PATCH /api/reports/{id}/
```

**Request Body:** Same as create

**Response:** 200 OK

#### Delete Report

```http
DELETE /api/reports/{id}/
```

**Response:** 204 No Content

#### Execute Report

```http
POST /api/reports/{id}/execute/
```

**Request Body:**
```json
{
  "parameters": {
    "project_id": "uuid",
    "start_date": "2026-01-01",
    "end_date": "2026-03-31"
  },
  "export_format": "PDF",
  "use_cache": true
}
```

**Response:**
```json
{
  "id": "uuid",
  "report": { /* report object */ },
  "status": "COMPLETED",
  "export_format": "PDF",
  "parameters": { /* as submitted */ },
  "file_path": "reports/report_a1b2c3d4.pdf",
  "file_size": 45678,
  "row_count": 25,
  "execution_time": 2.34,
  "executed_by": { /* user object */ },
  "created_at": "2026-03-11T10:00:00Z",
  "completed_at": "2026-03-11T10:00:02Z",
  "duration": "0:00:02.340000",
  "was_successful": true
}
```

#### Get Execution History

```http
GET /api/reports/{id}/executions/
```

**Response:** Array of execution objects (last 20)

---

### Report Execution Endpoints

#### List All Executions

```http
GET /api/report-executions/
```

**Query Parameters:**
- `report`: Filter by report ID
- `status`: Filter by status (COMPLETED, FAILED, etc.)
- `export_format`: Filter by export format

**Response:** Array of execution objects

#### Get Execution

```http
GET /api/report-executions/{id}/
```

**Response:** Execution object

---

### Report Schedule Endpoints

#### List Schedules

```http
GET /api/report-schedules/
```

**Query Parameters:**
- `report`: Filter by report ID
- `frequency`: Filter by frequency
- `is_active`: Filter by active status

**Response:**
```json
[
  {
    "id": "uuid",
    "report": { /* report object */ },
    "name": "Weekly Financial Report",
    "frequency": "WEEKLY",
    "cron_expression": null,
    "export_format": "PDF",
    "parameters": {
      "project_id": "uuid"
    },
    "delivery_method": "EMAIL",
    "recipients": ["john.doe@example.com", "jane.smith@example.com"],
    "is_active": true,
    "last_run": "2026-03-04T09:00:00Z",
    "next_run": "2026-03-11T09:00:00Z",
    "created_by": { /* user object */ },
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-03-04T09:00:00Z",
    "is_due": false
  }
]
```

#### Create Schedule

```http
POST /api/report-schedules/
```

**Request Body:**
```json
{
  "report_id": "uuid",
  "name": "Weekly Financial Report",
  "frequency": "WEEKLY",
  "export_format": "PDF",
  "parameters": {
    "project_id": "uuid"
  },
  "delivery_method": "EMAIL",
  "recipients": ["john.doe@example.com"]
}
```

**Response:** 201 Created

#### Update Schedule

```http
PUT /api/report-schedules/{id}/
PATCH /api/report-schedules/{id}/
```

**Response:** 200 OK

#### Delete Schedule

```http
DELETE /api/report-schedules/{id}/
```

**Response:** 204 No Content

---

### Widget Endpoints

#### List Widgets

```http
GET /api/widgets/
```

**Query Parameters:**
- `widget_type`: Filter by type
- `is_active`: Filter by active status

**Response:**
```json
[
  {
    "id": "uuid",
    "organization": "uuid",
    "report": "uuid",
    "name": "Active Projects",
    "widget_type": "KPI",
    "chart_type": null,
    "data_source": "active_project_count",
    "query_parameters": {},
    "display_order": 1,
    "refresh_interval": 300,
    "icon": "📊",
    "color": "#3498db",
    "is_active": true,
    "created_by": { /* user object */ },
    "created_at": "2026-01-15T10:00:00Z",
    "updated_at": "2026-01-15T10:00:00Z"
  }
]
```

#### Get Widget Data

```http
GET /api/widgets/{id}/data/
```

**Response:**
```json
{
  "value": 15,
  "widget_type": "KPI",
  "chart_type": null,
  "timestamp": "2026-03-11T10:00:00Z"
}
```

#### Get Dashboard

```http
GET /api/widgets/dashboard/
```

**Response:** Array of widgets with their data

```json
[
  {
    "widget": { /* widget object */ },
    "data": {
      "value": 15,
      "widget_type": "KPI",
      "chart_type": null,
      "timestamp": "2026-03-11T10:00:00Z"
    }
  }
]
```

---

## Scheduling

### Frequency Options

1. **DAILY**: Executes every 24 hours
2. **WEEKLY**: Executes every 7 days
3. **MONTHLY**: Executes every 30 days
4. **QUARTERLY**: Executes every 90 days
5. **CUSTOM**: Uses cron expression (requires croniter package)

### Delivery Methods

1. **EMAIL**: Send report via email to recipients
2. **DASHBOARD**: Display on dashboard
3. **STORAGE**: Save to file storage only
4. **ALL**: All of the above

### Celery Configuration

Add to `config/settings.py`:

```python
# Celery Configuration
CELERY_BROKER_URL = 'redis://localhost:6379/0'
CELERY_RESULT_BACKEND = 'redis://localhost:6379/0'
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = 'UTC'

# Celery Beat Schedule
CELERY_BEAT_SCHEDULE = {
    'execute-scheduled-reports': {
        'task': 'reporting.execute_scheduled_reports',
        'schedule': crontab(minute='*/15'),  # Every 15 minutes
    },
    'cleanup-old-executions': {
        'task': 'reporting.cleanup_old_executions',
        'schedule': crontab(hour=2, minute=0),  # Daily at 2 AM
    },
    'cleanup-failed-executions': {
        'task': 'reporting.cleanup_failed_executions',
        'schedule': crontab(hour=3, minute=0),  # Daily at 3 AM
    },
}
```

### Running Celery

**Development:**
```bash
# Worker
celery -A config worker -l info

# Beat (scheduler)
celery -A config beat -l info
```

**Production (Docker):**
```yaml
# docker-compose.yml
services:
  celery-worker:
    build: .
    command: celery -A config worker -l info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379/0

  celery-beat:
    build: .
    command: celery -A config beat -l info
    depends_on:
      - db
      - redis
    environment:
      - DATABASE_URL=postgresql://...
      - REDIS_URL=redis://redis:6379/0
```

---

## Dashboard Widgets

### Built-in Data Sources

1. **project_count**: Total project count
2. **active_project_count**: Active projects
3. **total_contract_value**: Sum of all contract values
4. **total_revenue**: Total certified revenue
5. **pending_variations**: Pending variation count
6. **outstanding_receivables**: Total outstanding receivables

### Creating Custom Widgets

```python
# Example: Create KPI widget
from apps.reporting.models import ReportWidget

widget = ReportWidget.objects.create(
    organization=org,
    name="Active Projects",
    widget_type=ReportWidget.WidgetType.KPI,
    data_source="active_project_count",
    display_order=1,
    refresh_interval=300,  # 5 minutes
    icon="📊",
    color="#3498db",
    is_active=True,
    created_by=user
)
```

### Widget Types

1. **KPI**: Single metric display
2. **CHART**: Visual chart (line, bar, pie, donut, area)
3. **TABLE**: Tabular data display
4. **GAUGE**: Progress/percentage gauge
5. **TREND**: Trend indicator (up/down)

---

## Usage Examples

### Example 1: Execute Project Financial Report

```python
from apps.reporting.models import Report
from apps.reporting.services import ReportService

# Get report
report = Report.objects.get(report_type=Report.ReportType.PROJECT_FINANCIAL)

# Execute with parameters
execution = ReportService.generate_report(
    report=report,
    parameters={
        'project_id': 'your-project-uuid',
        'start_date': '2026-01-01',
        'end_date': '2026-03-31'
    },
    export_format=Report.ExportFormat.PDF,
    executed_by=request.user,
    use_cache=True
)

# Check status
print(f"Status: {execution.status}")
print(f"File: {execution.file_path}")
print(f"Rows: {execution.row_count}")
print(f"Time: {execution.execution_time}s")
```

### Example 2: Create Scheduled Report

```python
from apps.reporting.models import Report, ReportSchedule
from apps.reporting.services import ReportScheduleService

# Get report
report = Report.objects.get(name="Monthly Financial Report")

# Create schedule
schedule = ReportScheduleService.create_schedule(
    report=report,
    created_by=user,
    name="Monthly Financial Email",
    frequency=ReportSchedule.Frequency.MONTHLY,
    export_format=Report.ExportFormat.EXCEL,
    parameters={'project_id': 'your-project-uuid'},
    delivery_method=ReportSchedule.DeliveryMethod.EMAIL,
    recipients=['manager@example.com', 'director@example.com']
)

print(f"Next run: {schedule.next_run}")
```

### Example 3: Fetch Widget Data

```python
from apps.reporting.models import ReportWidget
from apps.reporting.selectors import DashboardWidgetDataSelector

# Get widget
widget = ReportWidget.objects.get(name="Active Projects")

# Fetch data
data = DashboardWidgetDataSelector.get_widget_data(widget)

print(f"Value: {data['value']}")
print(f"Timestamp: {data['timestamp']}")
```

---

## Deployment

### 1. Install Dependencies

```bash
pip install pandas>=2.0 reportlab>=4.0 openpyxl>=3.1
```

### 2. Run Migrations

```bash
python manage.py migrate reporting
```

### 3. Configure Redis

**Docker:**
```yaml
services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
```

**Settings:**
```python
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}
```

### 4. Configure Celery

See [Scheduling](#scheduling) section above.

### 5. Create Initial Reports

```python
# Run in Django shell: python manage.py shell

from apps.reporting.models import Report
from apps.authentication.models import Organization

org = Organization.objects.first()
user = org.users.first()

# Create default reports
reports = [
    {
        'name': 'Project Financial Summary',
        'description': 'Comprehensive financial overview of project performance',
        'report_type': Report.ReportType.PROJECT_FINANCIAL,
    },
    {
        'name': 'Cash Flow Forecast',
        'description': '12-month cash flow forecast',
        'report_type': Report.ReportType.CASH_FLOW,
    },
    {
        'name': 'Variation Impact Report',
        'description': 'Analysis of all variation orders',
        'report_type': Report.ReportType.VARIATION_IMPACT,
    },
    {
        'name': 'Subcontractor Payment Tracker',
        'description': 'Track subcontractor claims and payments',
        'report_type': Report.ReportType.SUBCONTRACTOR_PAYMENT,
    },
    {
        'name': 'Document Audit Log',
        'description': 'Audit trail of all document activity',
        'report_type': Report.ReportType.DOCUMENT_AUDIT,
    },
    {
        'name': 'Procurement Summary',
        'description': 'Purchase orders and supplier invoices summary',
        'report_type': Report.ReportType.PROCUREMENT_SUMMARY,
    },
]

for report_data in reports:
    Report.objects.create(
        organization=org,
        created_by=user,
        **report_data
    )

print("✅ Default reports created")
```

### 6. Monitor Execution

**Admin Interface:**
- Navigate to `/admin/reporting/reportexecution/`
- View execution history with status badges
- Check error messages and stack traces

**API:**
```http
GET /api/report-executions/?status=FAILED
```

---

## Performance Optimization

### 1. Caching

Enable caching for frequently run reports:

```python
report.cache_duration = 600  # 10 minutes
report.save()
```

### 2. Query Optimization

All selectors use `select_related()` and `prefetch_related()` for optimal database queries.

### 3. Asynchronous Execution

For large reports, consider executing asynchronously:

```python
from apps.reporting.tasks import execute_report_async

# Celery task (to be implemented)
result = execute_report_async.delay(report_id, parameters, format, user_id)
```

### 4. Cleanup Tasks

Run cleanup tasks regularly to free storage:

```bash
# Cleanup executions older than 90 days
python manage.py shell -c "from apps.reporting.tasks import cleanup_old_executions; cleanup_old_executions()"

# Cleanup failed executions older than 24 hours
python manage.py shell -c "from apps.reporting.tasks import cleanup_failed_executions; cleanup_failed_executions()"
```

---

## Troubleshooting

### PDF Generation Issues

**Problem:** PDF files are too large

**Solution:**
- Limit data to top 20 rows in tables
- Use pagination for large datasets
- Consider PDF compression

### Excel Formatting Issues

**Problem:** Currency not displaying correctly

**Solution:**
```python
from openpyxl.styles import numbers

cell.number_format = numbers.FORMAT_CURRENCY_GBP_SIMPLE  # £#,##0.00
```

### Celery Beat Not Running

**Problem:** Scheduled reports not executing

**Solution:**
1. Check Celery beat is running: `ps aux | grep celery`
2. Check beat schedule in settings
3. Verify Redis connection
4. Check Celery worker logs

### Cache Issues

**Problem:** Reports not updating

**Solution:**
1. Disable caching: `report.cache_duration = 0`
2. Clear cache: `python manage.py shell -c "from django.core.cache import cache; cache.clear()"`
3. Check Redis connection: `redis-cli ping`

---

## Future Enhancements

- [ ] Custom report builder UI
- [ ] Report templates with variables
- [ ] Chart generation in PDF/Excel
- [ ] Scheduled report preview
- [ ] Report versioning
- [ ] Data source plugins
- [ ] Multi-language support
- [ ] Report sharing with external users
- [ ] Advanced filtering UI
- [ ] Real-time report execution status

---

## Support

For issues or questions:
- **Documentation:** See `/docs/`
- **API Reference:** Navigate to `/api/schema/swagger-ui/`
- **Admin Interface:** Navigate to `/admin/reporting/`

**Module Version:** 1.0.0  
**Last Updated:** 2026-03-11  
**Author:** COMS Development Team
