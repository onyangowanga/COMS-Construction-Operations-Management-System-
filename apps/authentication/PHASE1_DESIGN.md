# Phase 1: Authentication Models - Design Documentation

## Overview
The authentication system for COMS implements a robust, scalable role-based access control (RBAC) with multi-project support and comprehensive audit logging.

## Models Design

### 1. **User Model** (Custom User)
**Purpose**: Extends Django's AbstractUser to add construction-specific fields and role management.

**Key Features**:
- **Role-based system**: Primary role (Super Admin, Contractor, Site Manager, QS, Architect, Client)
- **Phone validation**: Using regex validator for international numbers
- **Profile management**: Company info, profile picture
- **Security tracking**: Email verification, last login IP
- **Timestamps**: Created/updated tracking

**Why Custom User?**:
- Cannot change User model after migrations
- Allows flexibility for future enhancements
- Construction-specific fields (company, phone)
- Better control over authentication flow

**Important Methods**:
- `has_project_access(project_id)`: Check if user can access a project
- `get_project_role(project_id)`: Get user's role within a specific project

### 2. **ProjectAccess Model** (Multi-Project Support)
**Purpose**: Links users to projects with granular permissions.

**Key Features**:
- **Project-specific roles**: Users can have different roles in different projects
- **Fine-grained permissions**: 5 boolean permission fields
- **Audit trail**: Who assigned it, when, and why (notes)
- **Soft delete**: Deactivate instead of deleting for history preservation
- **Auto-permissions**: Automatically sets permissions based on role

**Permission Structure**:
```python
OWNER/MANAGER:      All permissions ✓
SITE_MANAGER:       Edit, Workers, View Financials
QS:                 Budget, Approvals, View Financials
ARCHITECT:          Approvals only
FOREMAN:            Workers only
VIEWER:             Read-only access
```

**Why This Design?**:
- **Flexibility**: User can be Site Manager on Project A, Architect on Project B
- **Security**: Explicit permission checks prevent unauthorized access
- **Scalability**: Easy to add new permission types
- **History**: Soft deletes preserve audit trail

### 3. **AuditLog Model** (Security Compliance)
**Purpose**: Track all authentication-related actions for security and compliance.

**Tracked Actions**:
- Logins (successful and failed)
- Logouts
- Password changes/resets
- Role changes
- Access grants/revocations
- Account creation/deactivation

**Why Audit Logging?**:
- **Security**: Detect suspicious activity (multiple failed logins)
- **Compliance**: Required for many construction contracts
- **Debugging**: Trace issues to specific events
- **Accountability**: Know who did what and when

**Features**:
- **Immutable**: No add/delete in admin (read-only)
- **JSON details**: Flexible additional data storage
- **IP tracking**: Geo-location and security analysis
- **User agent**: Device/browser information

## Database Design Considerations

### Indexes
Strategic indexes for common query patterns:
- `User`: `email`, `role`, `(is_active, role)`
- `ProjectAccess`: `(user, project)`, `(project, is_active)`, `project_role`
- `AuditLog`: `(user, action)`, `(action, timestamp)`, `timestamp`

**Why These Indexes?**:
- Frequent filtering by role and active status
- Project access checks are performance-critical
- Audit log queries by time range and action type

### Relationships
```
User (1) ←──→ (M) ProjectAccess ←──→ (M) Project
User (1) ←──→ (M) AuditLog
User (1) ←──→ (M) ProjectAccess [as assigned_by]
```

### Unique Constraints
- `User.username`: Inherited from AbstractUser
- `User.email`: Inherited from AbstractUser
- `ProjectAccess(user, project)`: One access record per user per project
- `Project.code`: Unique project identifier

## Security Features

### 1. **Password Security**
- Django's PBKDF2 hashing (default)
- Password validators (length, similarity, common, numeric)
- Password reset with audit logging

### 2. **Access Control**
- Super Admin: Bypass all project checks
- Role-based routing in views
- Permission checks at model level
- Project-scoped data isolation

### 3. **Audit Trail**
- All authentication events logged
- Failed login attempts tracked
- IP address and device tracking
- Immutable audit records

### 4. **Email Verification**
- `is_verified` flag
- Can require verification before access
- Tracked in audit log

## Django Signals Integration

**signals.py** automatically:
- Logs all login/logout events
- Tracks failed login attempts
- Records account creation
- Logs access grants/revocations
- Updates last login IP

## Usage Examples

### Check Project Access
```python
# In a view or permission class
if not request.user.has_project_access(project_id):
    return HttpResponseForbidden()

# Get role for specific project
role = request.user.get_project_role(project_id)
if role == ProjectAccess.ProjectRole.OWNER:
    # Allow editing
    pass
```

### Grant Project Access
```python
access = ProjectAccess.objects.create(
    user=user,
    project=project,
    project_role=ProjectAccess.ProjectRole.SITE_MANAGER,
    assigned_by=request.user
)
# Permissions are auto-set based on role
```

### Deactivate Access (Soft Delete)
```python
access = ProjectAccess.objects.get(user=user, project=project)
access.deactivate()  # Sets is_active=False, removed_at=now()
```

### Query Audit Logs
```python
# Recent logins
recent_logins = AuditLog.objects.filter(
    action=AuditLog.Action.LOGIN,
    timestamp__gte=timezone.now() - timedelta(days=7)
)

# Failed login attempts for a user
failed_attempts = AuditLog.objects.filter(
    details__username=username,
    action=AuditLog.Action.FAILED_LOGIN
).count()
```

## Future Enhancements (Post-Phase 1)

1. **Two-Factor Authentication (2FA)**
   - Add `two_factor_enabled` field to User
   - TOTP or SMS-based verification

2. **Session Management**
   - Track active sessions
   - Force logout from all devices

3. **IP Whitelisting**
   - Restrict access by IP range
   - Per-user or per-project settings

4. **Advanced Permissions**
   - Row-level permissions
   - Time-based access (temporary access)
   - Department-level grouping

5. **OAuth Integration**
   - Google/Microsoft SSO
   - SAML for enterprise clients

## Testing Checklist

- [ ] User creation with all roles
- [ ] Login/logout audit logging
- [ ] Failed login tracking
- [ ] Project access grant/revoke
- [ ] Permission auto-assignment
- [ ] Soft delete functionality
- [ ] Super Admin bypass
- [ ] Multi-project access
- [ ] Email uniqueness
- [ ] Username uniqueness

## Migration Notes

**Important**: This is Phase 1. Run migrations BEFORE adding data:
```bash
python manage.py makemigrations authentication projects
python manage.py migrate
```

**Why projects migration?**: ProjectAccess has a foreign key to Project model.

## Admin Interface

All models are registered in admin with:
- Optimized list displays
- Useful filters
- Search functionality
- Read-only audit logs
- Bulk actions for access management

Access at: `http://localhost:8000/admin/`

---

**Status**: ✅ Ready for Migration
**Phase**: 1 - Foundation
**Next**: Create migrations and test in Django admin
