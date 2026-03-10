# COMS Database Schema

## Overview
This document outlines the database schema for the COMS (Construction Operations Management System).

## Database: PostgreSQL 15

### Schema Conventions
- **Table Names**: Lowercase with underscores (`project_budgets`)
- **Primary Keys**: `id` (BigInt, Auto-increment)
- **Foreign Keys**: `{table}_id` format
- **Timestamps**: All tables include `created_at`, `updated_at`
- **Soft Deletes**: `deleted_at` for recoverable records
- **User Tracking**: `created_by_id`, `updated_by_id` where applicable

---

## Core Tables

### 1. Authentication Module

#### users
User accounts and authentication

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | Primary key |
| username | VARCHAR(150) | UNIQUE, NOT NULL | Login username |
| email | VARCHAR(254) | UNIQUE, NOT NULL | Email address |
| password | VARCHAR(128) | NOT NULL | Hashed password |
| first_name | VARCHAR(150) | | First name |
| last_name | VARCHAR(150) | | Last name |
| phone | VARCHAR(20) | | Contact number |
| role | VARCHAR(20) | NOT NULL | User role enum |
| is_active | Boolean | DEFAULT TRUE | Account status |
| is_staff | Boolean | DEFAULT FALSE | Admin access |
| is_superuser | Boolean | DEFAULT FALSE | Super admin |
| last_login | DateTime | NULL | Last login time |
| created_at | DateTime | NOT NULL | Creation timestamp |
| updated_at | DateTime | NOT NULL | Update timestamp |

**Indexes:**
- `username` (UNIQUE)
- `email` (UNIQUE)
- `role`

**Role Enum:**
- `SUPER_ADMIN`
- `CONTRACTOR`
- `SITE_MANAGER`
- `QS`
- `ARCHITECT`
- `CLIENT`

---

### 2. Projects Module

#### projects
Main project table

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | Primary key |
| name | VARCHAR(200) | NOT NULL | Project name |
| code | VARCHAR(50) | UNIQUE, NOT NULL | Project code |
| description | TEXT | | Project details |
| client_name | VARCHAR(200) | NOT NULL | Client name |
| location | VARCHAR(500) | | Project location |
| start_date | Date | NOT NULL | Start date |
| end_date | Date | | Expected completion |
| total_budget | Decimal(15,2) | NOT NULL | Total budget |
| status | VARCHAR(20) | NOT NULL | Project status |
| health_status | VARCHAR(20) | NOT NULL | Green/Yellow/Red |
| progress_percentage | Decimal(5,2) | DEFAULT 0 | 0-100% |
| contractor_id | BigInt | FK → users | Project owner |
| created_by_id | BigInt | FK → users | Creator |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |
| deleted_at | DateTime | NULL | Soft delete |

**Indexes:**
- `code` (UNIQUE)
- `contractor_id`
- `status`
- `health_status`

**Status Enum:**
- `PLANNING`
- `IN_PROGRESS`
- `ON_HOLD`
- `COMPLETED`
- `CANCELLED`

**Health Status Enum:**
- `GREEN` - On track
- `YELLOW` - Minor issues
- `RED` - Critical issues

#### project_members
Team members assigned to projects

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| user_id | BigInt | FK → users | |
| role | VARCHAR(50) | NOT NULL | Role in project |
| assigned_at | DateTime | NOT NULL | |
| removed_at | DateTime | NULL | If removed |

**Indexes:**
- `(project_id, user_id)` (UNIQUE)

#### milestones
Project milestones

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| name | VARCHAR(200) | NOT NULL | Milestone name |
| description | TEXT | | Details |
| due_date | Date | NOT NULL | Target date |
| completion_date | Date | NULL | Actual completion |
| is_completed | Boolean | DEFAULT FALSE | Status |
| budget_allocation | Decimal(15,2) | DEFAULT 0 | Budget for this milestone |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`
- `is_completed`

---

### 3. Ledger Module

#### project_budgets
Budget allocations by stage

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| stage_name | VARCHAR(100) | NOT NULL | e.g., "Foundation" |
| allocated_amount | Decimal(15,2) | NOT NULL | Budget allocation |
| spent_amount | Decimal(15,2) | DEFAULT 0 | Amount spent |
| notes | TEXT | | |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`

#### suppliers
Supplier master data

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| name | VARCHAR(200) | NOT NULL | Supplier name |
| contact_person | VARCHAR(200) | | Contact name |
| phone | VARCHAR(20) | | Phone |
| email | VARCHAR(254) | | Email |
| address | TEXT | | Address |
| tax_id | VARCHAR(50) | | Tax/VAT ID |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

#### expenses
All project expenses

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| budget_stage_id | BigInt | FK → project_budgets | |
| supplier_id | BigInt | FK → suppliers | NULL if cash |
| category | VARCHAR(50) | NOT NULL | Expense category |
| description | TEXT | NOT NULL | What was purchased |
| amount | Decimal(15,2) | NOT NULL | Expense amount |
| expense_date | Date | NOT NULL | When expense occurred |
| receipt_number | VARCHAR(100) | | Receipt/invoice number |
| payment_method | VARCHAR(20) | NOT NULL | Cash/Bank/etc |
| created_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`
- `expense_date`
- `category`

#### client_payments
Payments received from clients

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| amount | Decimal(15,2) | NOT NULL | Payment amount |
| payment_date | Date | NOT NULL | When received |
| payment_method | VARCHAR(20) | NOT NULL | Bank/Cash/Cheque |
| reference_number | VARCHAR(100) | | Transaction reference |
| notes | TEXT | | |
| created_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`
- `payment_date`

---

### 4. Workers Module

#### workers
Worker registry

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | NULL if shared |
| first_name | VARCHAR(100) | NOT NULL | |
| last_name | VARCHAR(100) | NOT NULL | |
| phone | VARCHAR(20) | | |
| id_number | VARCHAR(50) | | National ID |
| role | VARCHAR(50) | NOT NULL | Mason/Laborer/etc |
| daily_rate | Decimal(10,2) | NOT NULL | Daily wage |
| hire_date | Date | NOT NULL | |
| termination_date | Date | NULL | If terminated |
| is_active | Boolean | DEFAULT TRUE | |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`
- `is_active`

#### attendance
Daily worker attendance

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| worker_id | BigInt | FK → workers | |
| project_id | BigInt | FK → projects | |
| attendance_date | Date | NOT NULL | |
| status | VARCHAR(20) | NOT NULL | Present/Absent/Half |
| hours_worked | Decimal(4,2) | DEFAULT 8 | Hours |
| overtime_hours | Decimal(4,2) | DEFAULT 0 | OT hours |
| notes | TEXT | | |
| marked_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |

**Indexes:**
- `(worker_id, attendance_date)` (UNIQUE)
- `project_id`
- `attendance_date`

#### machines
Machine/equipment inventory

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| name | VARCHAR(200) | NOT NULL | Machine name |
| machine_type | VARCHAR(100) | NOT NULL | Type |
| registration_number | VARCHAR(50) | | Reg/Serial |
| hourly_rate | Decimal(10,2) | NOT NULL | Rental rate |
| is_owned | Boolean | DEFAULT TRUE | Owned vs rented |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

#### machine_usage
Machine usage logs

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| machine_id | BigInt | FK → machines | |
| project_id | BigInt | FK → projects | |
| usage_date | Date | NOT NULL | |
| hours_used | Decimal(6,2) | NOT NULL | Hours |
| operator_name | VARCHAR(200) | | Operator |
| notes | TEXT | | |
| logged_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |

**Indexes:**
- `(machine_id, usage_date)`
- `project_id`

---

### 5. Consultants Module

#### documents
Document repository

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| title | VARCHAR(300) | NOT NULL | Document title |
| document_type | VARCHAR(50) | NOT NULL | Drawing/BOQ/etc |
| file_path | VARCHAR(500) | NOT NULL | S3/local path |
| file_size | BigInt | | Bytes |
| mime_type | VARCHAR(100) | | File MIME type |
| version | VARCHAR(20) | DEFAULT '1.0' | Version number |
| is_latest | Boolean | DEFAULT TRUE | Latest version flag |
| uploaded_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |
| updated_at | DateTime | NOT NULL | |

**Indexes:**
- `project_id`
- `document_type`
- `is_latest`

#### document_revisions
Document version history

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| document_id | BigInt | FK → documents | |
| version | VARCHAR(20) | NOT NULL | Version |
| file_path | VARCHAR(500) | NOT NULL | Path |
| changes_description | TEXT | | What changed |
| uploaded_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |

#### approvals
Document approvals

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| document_id | BigInt | FK → documents | |
| approver_id | BigInt | FK → users | |
| status | VARCHAR(20) | NOT NULL | Pending/Approved/Rejected |
| comments | TEXT | | Approval comments |
| approved_at | DateTime | NULL | When approved |
| created_at | DateTime | NOT NULL | |

---

### 6. Clients Module

#### client_messages
Client communications

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| sender_id | BigInt | FK → users | |
| message | TEXT | NOT NULL | Message content |
| is_read | Boolean | DEFAULT FALSE | Read status |
| created_at | DateTime | NOT NULL | |

#### project_updates
Updates for clients

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| title | VARCHAR(200) | NOT NULL | Update title |
| description | TEXT | NOT NULL | Details |
| posted_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |

#### photo_gallery
Project photos

| Column | Type | Constraints | Notes |
|--------|------|-------------|-------|
| id | BigInt | PK, Auto | |
| project_id | BigInt | FK → projects | |
| title | VARCHAR(200) | | Photo title |
| description | TEXT | | Description |
| photo_path | VARCHAR(500) | NOT NULL | S3/local path |
| taken_date | Date | | When photo taken |
| uploaded_by_id | BigInt | FK → users | |
| created_at | DateTime | NOT NULL | |

---

## Relationships Diagram

```
users (1) ----< (M) projects [contractor_id]
users (1) ----< (M) project_members
projects (1) ----< (M) project_members
projects (1) ----< (M) milestones
projects (1) ----< (M) project_budgets
projects (1) ----< (M) expenses
projects (1) ----< (M) client_payments
projects (1) ----< (M) workers
projects (1) ----< (M) attendance
projects (1) ----< (M) machine_usage
projects (1) ----< (M) documents
projects (1) ----< (M) client_messages
workers (1) ----< (M) attendance
machines (1) ----< (M) machine_usage
documents (1) ----< (M) document_revisions
documents (1) ----< (M) approvals
suppliers (1) ----< (M) expenses
```

---

## Views (To be created)

### project_financial_summary
Real-time P&L view

```sql
CREATE VIEW project_financial_summary AS
SELECT 
    p.id as project_id,
    p.name as project_name,
    p.total_budget,
    COALESCE(SUM(e.amount), 0) as total_expenses,
    COALESCE(SUM(cp.amount), 0) as total_payments,
    p.total_budget - COALESCE(SUM(e.amount), 0) as remaining_budget,
    COALESCE(SUM(cp.amount), 0) - COALESCE(SUM(e.amount), 0) as profit_loss
FROM projects p
LEFT JOIN expenses e ON p.id = e.project_id
LEFT JOIN client_payments cp ON p.id = cp.project_id
GROUP BY p.id;
```

---

## Indexes Strategy

- **Primary Keys**: Auto-indexed
- **Foreign Keys**: Always indexed
- **Frequent WHERE clauses**: Indexed
- **Date ranges**: Indexed
- **Status fields**: Indexed

---

**Version**: 1.0
**Last Updated**: March 2026
**Database**: PostgreSQL 15
