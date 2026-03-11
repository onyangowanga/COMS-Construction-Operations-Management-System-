# COMS REST API Documentation

Complete REST API implementation for the Construction Operations Management System (COMS).

## Overview

The API provides comprehensive CRUD operations and custom endpoints for managing construction projects, including:
- Projects and stages
- Bill of Quantities (BQ)
- Consultants and fees
- Suppliers and procurement
- Workers and labour records
- Expenses and allocations
- Client payments
- Documents and photos
- Statutory approvals

## Base URL

```
http://your-server.com/api/
```

## Authentication

All API endpoints require JWT authentication. Include the access token in the Authorization header:

```
Authorization: Bearer <your_access_token>
```

Get tokens from:
```
POST /api/auth/login/
```

## API Documentation

Interactive API documentation is available at:
- **Swagger UI**: `/api/docs/`
- **ReDoc**: `/api/redoc/`
- **OpenAPI Schema**: `/api/schema/`

## Main Endpoints

### Projects

**List/Create Projects**
```
GET  /api/projects/
POST /api/projects/
```

**Project Details**
```
GET    /api/projects/{id}/
PUT    /api/projects/{id}/
PATCH  /api/projects/{id}/
DELETE /api/projects/{id}/
```

**Custom Project Endpoints**
```
GET /api/projects/{id}/stages/              # Get all stages
GET /api/projects/{id}/expenses/            # Get all expenses
GET /api/projects/{id}/payments/            # Get client payments
GET /api/projects/{id}/photos/              # Get project photos
GET /api/projects/{id}/financial_summary/   # Financial summary
```

**Filtering & Search**
```
GET /api/projects/?status=ACTIVE
GET /api/projects/?contract_type=LUMP_SUM
GET /api/projects/?project_type=RESIDENTIAL
GET /api/projects/?search=nairobi
GET /api/projects/?ordering=-created_at
```

### Bill of Quantities (BQ)

**BQ Sections**
```
GET  /api/bq-sections/
POST /api/bq-sections/
GET  /api/bq-sections/{id}/
GET  /api/bq-sections/{id}/elements/   # Get elements in section
```

**BQ Elements**
```
GET  /api/bq-elements/
POST /api/bq-elements/
GET  /api/bq-elements/{id}/
GET  /api/bq-elements/{id}/items/      # Get items in element
```

**BQ Items**
```
GET  /api/bq-items/
POST /api/bq-items/
GET  /api/bq-items/{id}/
```

**Filtering**
```
GET /api/bq-sections/?project={project_id}
GET /api/bq-elements/?section={section_id}
GET /api/bq-items/?element={element_id}
```

### Consultants

**Consultants**
```
GET  /api/consultants/
POST /api/consultants/
GET  /api/consultants/{id}/
GET  /api/consultants/{id}/fees/       # Get consultant fees
```

**Consultant Fees**
```
GET  /api/consultant-fees/
POST /api/consultant-fees/
GET  /api/consultant-fees/{id}/
GET  /api/consultant-fees/{id}/payments/   # Get payments for fee
```

**Consultant Payments**
```
GET  /api/consultant-payments/
POST /api/consultant-payments/
GET  /api/consultant-payments/{id}/
```

**Filtering**
```
GET /api/consultants/?consultant_type=ARCHITECT
GET /api/consultants/?is_active=true
GET /api/consultant-fees/?project={project_id}
GET /api/consultant-fees/?fee_type=DESIGN
```

### Suppliers

**Suppliers**
```
GET  /api/suppliers/
POST /api/suppliers/
GET  /api/suppliers/{id}/
GET  /api/suppliers/{id}/purchase_orders/  # Get supplier LPOs
GET  /api/suppliers/{id}/invoices/         # Get supplier invoices
```

**Local Purchase Orders (LPOs)**
```
GET  /api/purchase-orders/
POST /api/purchase-orders/
GET  /api/purchase-orders/{id}/
```

**Supplier Invoices**
```
GET  /api/supplier-invoices/
POST /api/supplier-invoices/
GET  /api/supplier-invoices/{id}/
```

**Filtering**
```
GET /api/purchase-orders/?project={project_id}
GET /api/purchase-orders/?status=APPROVED
GET /api/supplier-invoices/?supplier={supplier_id}
GET /api/supplier-invoices/?status=PENDING
```

### Workers

**Workers**
```
GET  /api/workers/
POST /api/workers/
GET  /api/workers/{id}/
GET  /api/workers/{id}/records/        # Get labour records
GET  /api/workers/{id}/unpaid_wages/   # Get unpaid wages
```

**Daily Labour Records**
```
GET  /api/labour-records/
POST /api/labour-records/
GET  /api/labour-records/{id}/
```

**Filtering**
```
GET /api/workers/?role=MASON
GET /api/workers/?is_active=true
GET /api/labour-records/?project={project_id}
GET /api/labour-records/?paid=false
GET /api/labour-records/?date=2026-03-01
```

### Ledger (Expenses)

**Expenses**
```
GET  /api/expenses/
POST /api/expenses/
GET  /api/expenses/{id}/
GET  /api/expenses/{id}/allocations/   # Get BQ allocations
GET  /api/expenses/unallocated/        # Get unallocated expenses
```

**Expense Allocations**
```
GET  /api/expense-allocations/
POST /api/expense-allocations/
GET  /api/expense-allocations/{id}/
```

**Filtering**
```
GET /api/expenses/?project={project_id}
GET /api/expenses/?expense_type=MATERIALS
GET /api/expenses/?date=2026-03-01
GET /api/expense-allocations/?expense={expense_id}
```

### Clients

**Client Payments**
```
GET  /api/client-payments/
POST /api/client-payments/
GET  /api/client-payments/{id}/
GET  /api/client-payments/{id}/receipt/    # Get payment receipt
```

**Client Receipts**
```
GET  /api/client-receipts/
POST /api/client-receipts/
GET  /api/client-receipts/{id}/
```

**Filtering**
```
GET /api/client-payments/?project={project_id}
GET /api/client-payments/?payment_method=BANK_TRANSFER
GET /api/client-payments/?payment_date=2026-03-01
```

### Documents

**Documents**
```
GET  /api/documents/
POST /api/documents/
GET  /api/documents/{id}/
GET  /api/documents/{id}/versions/         # Get all versions
GET  /api/documents/{id}/latest_version/   # Get latest version
```

**Document Versions**
```
GET  /api/document-versions/
POST /api/document-versions/
GET  /api/document-versions/{id}/
```

**Filtering**
```
GET /api/documents/?project={project_id}
GET /api/documents/?document_type=DRAWINGS
GET /api/document-versions/?is_latest=true
```

### Media

**Project Photos**
```
GET  /api/photos/
POST /api/photos/
GET  /api/photos/{id}/
```

**Filtering**
```
GET /api/photos/?project={project_id}
GET /api/photos/?stage={stage_id}
GET /api/photos/?uploaded_at=2026-03-01
```

### Approvals

**Project Approvals**
```
GET  /api/approvals/
POST /api/approvals/
GET  /api/approvals/{id}/
GET  /api/approvals/expired/           # Get expired approvals
GET  /api/approvals/expiring_soon/     # Get approvals expiring in 30 days
```

**Filtering**
```
GET /api/approvals/?project={project_id}
GET /api/approvals/?approval_type=NCA
GET /api/approvals/?status=APPROVED
```

## Common Query Parameters

All list endpoints support:

**Pagination**
```
?page=1
?page_size=20
```

**Searching**
```
?search=keyword
```

**Ordering**
```
?ordering=created_at          # Ascending
?ordering=-created_at         # Descending
?ordering=name,-created_at    # Multiple fields
```

**Filtering**
```
?field_name=value
?status=ACTIVE
?is_active=true
?date=2026-03-01
```

## Response Format

### Success Response (200 OK)

**List View:**
```json
{
  "count": 100,
  "next": "http://api.example.com/api/projects/?page=2",
  "previous": null,
  "results": [...]
}
```

**Detail View:**
```json
{
  "id": "uuid-here",
  "name": "Project Name",
  ...
}
```

### Error Response (400 Bad Request)

```json
{
  "field_name": ["Error message"]
}
```

### Error Response (404 Not Found)

```json
{
  "detail": "Not found."
}
```

## Example Requests

### Create a Project

```bash
curl -X POST http://your-server.com/api/projects/ \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{
    "organization": "org-uuid",
    "code": "PRJ-001",
    "name": "New Office Building",
    "client_name": "ABC Corporation",
    "location": "Nairobi",
    "project_type": "COMMERCIAL",
    "contract_type": "LUMP_SUM",
    "project_value": "50000000.00",
    "start_date": "2026-04-01",
    "status": "ACTIVE"
  }'
```

### Get Project Financial Summary

```bash
curl -X GET http://your-server.com/api/projects/{id}/financial_summary/ \
  -H "Authorization: Bearer <token>"
```

Response:
```json
{
  "project_value": "50000000.00",
  "total_expenses": "35000000.00",
  "total_payments": "40000000.00",
  "outstanding_balance": "10000000.00",
  "profit_loss": "5000000.00"
}
```

### Filter Projects

```bash
curl -X GET "http://your-server.com/api/projects/?status=ACTIVE&contract_type=LUMP_SUM&ordering=-created_at" \
  -H "Authorization: Bearer <token>"
```

## Notes

1. **Pagination**: Default page size is set in Django settings (typically 20-50 items)
2. **Permissions**: All endpoints require authentication
3. **UUIDs**: All models use UUID primary keys
4. **Timestamps**: All models include `created_at` and `updated_at` fields
5. **Read-only Fields**: Computed fields and timestamps are read-only
6. **Nested Relationships**: Related objects can be expanded in detail views

## Architecture

```
api/
├── serializers/          # Data serialization layer
│   ├── projects.py
│   ├── bq.py
│   ├── consultants.py
│   ├── suppliers.py
│   ├── workers.py
│   ├── ledger.py
│   ├── clients.py
│   ├── documents.py
│   ├── media.py
│   └── approvals.py
├── views/               # API endpoints logic
│   ├── projects.py
│   ├── bq.py
│   ├── consultants.py
│   ├── suppliers.py
│   ├── workers.py
│   ├── ledger.py
│   ├── clients.py
│   ├── documents.py
│   ├── media.py
│   └── approvals.py
├── routers.py          # URL routing configuration
├── urls.py             # URL patterns
└── __init__.py
```

## Future Enhancements

- [ ] Bulk operations endpoints
- [ ] Export endpoints (PDF, Excel)
- [ ] Webhooks for real-time notifications
- [ ] GraphQL support
- [ ] Rate limiting
- [ ] API versioning (/api/v1/, /api/v2/)
