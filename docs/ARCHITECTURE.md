# COMS System Architecture

## Overview
COMS (Construction Operations Management System) is a web-based platform designed to manage all aspects of construction projects from finances to workforce management.

## System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        COMS System                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│  │   Browser    │    │    Mobile    │    │   Desktop    │ │
│  │   Client     │    │    Client    │    │   Client     │ │
│  └──────┬───────┘    └──────┬───────┘    └──────┬───────┘ │
│         │                   │                   │          │
│         └───────────────────┼───────────────────┘          │
│                             │                               │
│                   ┌─────────▼─────────┐                    │
│                   │   Nginx (Reverse  │                    │
│                   │      Proxy)       │                    │
│                   └─────────┬─────────┘                    │
│                             │                               │
│         ┌───────────────────┼───────────────────┐          │
│         │                   │                   │          │
│    ┌────▼────┐         ┌────▼────┐        ┌────▼────┐    │
│    │ Django  │         │ Django  │        │  Static │    │
│    │ +HTMX   │◄───────►│   DRF   │        │  Files  │    │
│    │Templates│         │   API   │        │         │    │
│    └────┬────┘         └────┬────┘        └─────────┘    │
│         │                   │                              │
│         └────────┬──────────┘                              │
│                  │                                         │
│         ┌────────▼────────┐                                │
│         │   Django ORM    │                                │
│         └────────┬────────┘                                │
│                  │                                         │
│      ┌───────────┼───────────┐                             │
│      │           │           │                             │
│  ┌───▼───┐   ┌───▼───┐  ┌───▼────┐                       │
│  │ PostgreSQL│  │ Redis │  │  S3   │                       │
│  │ Database  │  │ Cache │  │Storage│                       │
│  └───────────┘  └───────┘  └────────┘                       │
└─────────────────────────────────────────────────────────────┘
```

## Technology Stack

### Frontend Layer
- **Templates**: Django Template Engine
- **Interactivity**: HTMX for dynamic updates
- **Styling**: Bootstrap 5
- **Icons**: Bootstrap Icons

### Backend Layer
- **Framework**: Django 4.2+
- **API**: Django REST Framework
- **Authentication**: JWT (djangorestframework-simplejwt)
- **Task Queue**: Celery (for async tasks)

### Data Layer
- **Database**: PostgreSQL 15
- **Cache**: Redis
- **File Storage**: S3-compatible object storage

### Infrastructure
- **Web Server**: Nginx
- **Application Server**: Gunicorn
- **Containerization**: Docker
- **Orchestration**: Docker Compose

## Module Architecture

### 1. Authentication Module (`apps.authentication`)
**Purpose**: User management and role-based access control

**Components**:
- Custom User model extending AbstractUser
- JWT token generation and validation
- Role-based permissions
- Multi-project access control

**Database Tables**:
- `users` - User accounts
- `roles` - System roles
- `user_roles` - User-role assignments
- `project_access` - Project-level permissions

### 2. Projects Module (`apps.projects`)
**Purpose**: Core project management functionality

**Components**:
- Project CRUD operations
- Budget allocation
- Milestone tracking
- Health status calculation

**Database Tables**:
- `projects` - Project master data
- `milestones` - Project milestones
- `project_stages` - Project phases
- `project_health` - Status tracking

### 3. Ledger Module (`apps.ledger`)
**Purpose**: Financial tracking and reporting

**Components**:
- Expense management
- Payment tracking
- P&L calculations
- Budget variance analysis

**Database Tables**:
- `project_budgets` - Budget allocations
- `expenses` - Expense entries
- `suppliers` - Supplier master
- `client_payments` - Payment records
- `stage_costs` - Stage-wise costs
- `ledger_entries` - Financial journal

### 4. Workers Module (`apps.workers`)
**Purpose**: Workforce and machinery management

**Components**:
- Worker registration
- Daily attendance
- Machine tracking
- Payroll calculations

**Database Tables**:
- `workers` - Worker master
- `attendance` - Daily attendance
- `machines` - Machine inventory
- `machine_usage` - Usage logs

### 5. Consultants Module (`apps.consultants`)
**Purpose**: Document and approval management

**Components**:
- Document upload/download
- Version control
- Approval workflows
- Activity logging

**Database Tables**:
- `documents` - Document metadata
- `document_revisions` - Version history
- `valuations` - QS valuations
- `approvals` - Approval tracking

### 6. Clients Module (`apps.clients`)
**Purpose**: Client portal and communication

**Components**:
- Read-only project view
- Progress visualization
- Photo gallery
- Messaging

**Database Tables**:
- `client_messages` - Client communications
- `project_updates` - Progress updates
- `photo_gallery` - Project photos

## Security Architecture

### Authentication Flow
```
1. User Login → JWT Token Generation
2. Token Storage (HTTP-only cookie)
3. Token Validation on each request
4. Role-based route access
5. Project-level permission check
```

### Security Measures
- JWT-based stateless authentication
- CSRF protection for forms
- SQL injection prevention (ORM)
- XSS protection (template escaping)
- HTTPS enforcement (production)
- Secure password hashing (PBKDF2)
- Rate limiting on API endpoints
- File upload validation
- Role-based access control (RBAC)

## Data Flow

### Typical Request Flow
```
1. User Request → Nginx
2. Nginx → Gunicorn
3. Gunicorn → Django
4. Django → ORM
5. ORM → PostgreSQL
6. Response ← Database
7. Template Rendering / JSON Response
8. User ← Response
```

### File Upload Flow
```
1. User uploads file → Django
2. File validation
3. Save to local/S3 storage
4. Metadata to PostgreSQL
5. Return file URL
```

## Deployment Architecture

### Development Environment
```
Developer Machine
  └── Docker Compose
      ├── Web Container (Django)
      ├── DB Container (PostgreSQL)
      └── Redis Container
```

### Production Environment
```
Cloud VPS
  ├── Nginx (Port 80/443)
  ├── Gunicorn (Multiple workers)
  ├── Django Application
  ├── Managed PostgreSQL
  ├── Redis
  └── S3 Storage
```

## Scalability Considerations

### Current Architecture
- Single server deployment
- Suitable for 1-50 concurrent users
- Perfect for solo contractor

### Future Scaling Options
1. **Horizontal Scaling**: Multiple web servers + load balancer
2. **Database**: Read replicas for reporting
3. **Caching**: Redis for frequently accessed data
4. **CDN**: For static files and media
5. **Background Jobs**: Celery for async tasks

## Monitoring & Logging

### Logging Levels
- **DEBUG**: Development only
- **INFO**: General application flow
- **WARNING**: Unusual but handled situations
- **ERROR**: Errors that need attention
- **CRITICAL**: System failures

### Monitoring Points
- Application logs → File system
- Error tracking → Sentry (optional)
- Uptime monitoring → UptimeRobot
- Performance → Django Debug Toolbar (dev)

## Backup Strategy

### Database
- Daily automated backups
- Retention: 30 days
- Storage: Off-site location

### Files
- S3 versioning enabled
- Weekly full backups

### Recovery
- Point-in-time recovery capability
- RTO: 4 hours
- RPO: 24 hours

---

**Version**: 1.0  
**Last Updated**: March 2026  
**Status**: Development Phase
