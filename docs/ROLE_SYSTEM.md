# Role-Based Access Control (RBAC) System Documentation

## Overview

The RBAC (Role-Based Access Control) module provides a comprehensive permission management system for COMS. It allows fine-grained control over what users can do within the system based on their assigned roles and permissions.

## Table of Contents

1. [Architecture](#architecture)
2. [Core Concepts](#core-concepts)
3. [System Roles](#system-roles)
4. [Permission Categories](#permission-categories)
5. [Models](#models)
6. [Services](#services)
7. [API Endpoints](#api-endpoints)
8. [Middleware](#middleware)
9. [Usage Examples](#usage-examples)
10. [Admin Interface](#admin-interface)
11. [Best Practices](#best-practices)

---

## Architecture

The RBAC module follows the COMS 3-layer architecture:

```
┌─────────────────┐
│   API Views     │  (REST endpoints for role management)
├─────────────────┤
│   Services      │  (Business logic for role operations)
├─────────────────┤
│   Selectors     │  (Optimized database queries)
├─────────────────┤
│   Models        │  (Role, Permission, UserRole)
└─────────────────┘
```

**Key Features:**
- Context-aware permissions (system-wide, organization-level, project-level)
- Role expiration support
- Superuser bypass
- Many-to-many role-permission relationships
- Middleware-based automatic enforcement

---

## Core Concepts

### Roles
Roles are collections of permissions that can be assigned to users. COMS has 8 predefined system roles.

### Permissions
Permissions are fine-grained capabilities that allow specific actions (e.g., "approve_variations", "view_financials").

### User Roles
User role assignments link users to roles with optional context (organization or project).

### Context
Permissions can be scoped to different contexts:
- **System-wide**: User has the permission everywhere
- **Organization-level**: User has the permission within a specific organization
- **Project-level**: User has the permission within a specific project

---

## System Roles

The system includes 8 predefined roles:

| Code | Name | Description |
|------|------|-------------|
| `admin` | Administrator | Full system access and control |
| `finance_manager` | Finance Manager | Manages budgets, payments, and financial reports |
| `project_manager` | Project Manager | Oversees project execution and team management |
| `site_engineer` | Site Engineer | Manages on-site operations and daily reports |
| `consultant` | Consultant | Reviews and approves technical documents |
| `client` | Client | Views project progress and approves milestones |
| `supplier` | Supplier | Manages supply orders and deliveries |
| `subcontractor` | Subcontractor | Manages subcontract work and claims |

---

## Permission Categories

Permissions are organized into 12 categories:

| Category | Description | Examples |
|----------|-------------|----------|
| **project** | Project management | create_project, edit_project, delete_project |
| **financial** | Financial operations | view_financials, manage_budget, approve_budget |
| **document** | Document management | upload_document, delete_document, approve_document |
| **variation** | Variation orders | create_variation, approve_variation, reject_variation |
| **claim** | Payment claims | create_claim, certify_claim, approve_claim |
| **payment** | Payments | create_payment, approve_payment, process_payment |
| **approval** | General approvals | approve_workflow, reject_workflow |
| **report** | Reporting | view_report, generate_report, export_report |
| **procurement** | Procurement | create_lpo, approve_lpo, receive_goods |
| **subcontract** | Subcontracting | manage_subcontract, approve_subcontract_claim |
| **site_operations** | Site operations | record_site_activity, update_progress |
| **system** | System administration | manage_users, manage_roles, system_settings |

---

## Models

### Role Model

```python
class Role(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=50, unique=True, choices=ROLE_CHOICES)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    is_system_role = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    permissions = models.ManyToManyField('Permission', related_name='roles')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def permission_count(self):
        return self.permissions.count()
    
    @property
    def user_count(self):
        return self.user_roles.filter(is_active=True).count()
```

**Key Points:**
- System roles cannot be deleted (`is_system_role=True`)
- Roles can be deactivated without deleting

### Permission Model

```python
class Permission(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    code = models.CharField(max_length=100, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, db_index=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    @property
    def role_count(self):
        return self.roles.filter(is_active=True).count()
```

**Database Indexes:**
- `perm_code_idx`: On `code` for fast lookups
- `perm_category_idx`: On `category` for filtering

### UserRole Model

```python
class UserRole(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_roles')
    role = models.ForeignKey(Role, on_delete=models.CASCADE, related_name='user_roles')
    organization = models.ForeignKey('authentication.Organization', null=True, blank=True, ...)
    project = models.ForeignKey('projects.Project', null=True, blank=True, ...)
    is_active = models.BooleanField(default=True, db_index=True)
    assigned_by = models.ForeignKey(User, null=True, blank=True, ...)
    assigned_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    notes = models.TextField(blank=True)
    
    @property
    def is_expired(self):
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    @property
    def is_valid(self):
        return self.is_active and not self.is_expired
```

**Database Indexes:**
- `ur_user_active_idx`: On `user + is_active`
- `ur_role_active_idx`: On `role + is_active`
- `ur_org_active_idx`: On `organization + is_active`
- `ur_project_active_idx`: On `project + is_active`

**Unique Constraint:**
- `user + role + organization + project` (prevents duplicate assignments)

---

## Services

### RoleService

```python
from apps.roles.services import RoleService

# Create a custom role
role = RoleService.create_role(
    code='custom_manager',
    name='Custom Manager',
    description='Custom role for special managers',
    permission_codes=['view_project', 'edit_project'],
    is_system_role=False
)

# Update a role
RoleService.update_role(
    role=role,
    name='Updated Manager',
    permission_codes=['view_project', 'edit_project', 'approve_variation']
)

# Delete a custom role
RoleService.delete_role(role)  # Raises ValueError if system role
```

### UserRoleService

```python
from apps.roles.services import UserRoleService

# Assign a role to a user
user_role = UserRoleService.assign_role(
    user=user,
    role_code='project_manager',
    organization=org,
    project=project,
    assigned_by=request.user,
    expires_at=datetime(2025, 12, 31),
    notes='Temporary PM for this project'
)

# Remove a role from a user
UserRoleService.remove_role(
    user=user,
    role_code='project_manager',
    organization=org,
    project=project
)

# Check if user has a permission
has_perm = UserRoleService.check_permission(
    user=user,
    permission_code='approve_variations',
    organization=org,
    project=project
)

# Get all user permissions
permissions = UserRoleService.get_user_permissions(
    user=user,
    organization=org,
    project=project
)
# Returns: ['view_project', 'edit_project', 'approve_variation', ...]

# Get all user roles with details
roles = UserRoleService.get_user_roles(
    user=user,
    organization=org,
    project=project
)
# Returns list of dicts with role details
```

---

## API Endpoints

### Roles API

#### List Roles
```http
GET /api/roles/
GET /api/roles/?is_active=true
GET /api/roles/?is_system_role=true
```

#### Get System Roles
```http
GET /api/roles/system/
```

#### Create Role
```http
POST /api/roles/
Content-Type: application/json

{
    "code": "custom_role",
    "name": "Custom Role",
    "description": "A custom role",
    "permission_ids": ["uuid1", "uuid2"],
    "is_system_role": false
}
```

#### Update Role
```http
PUT /api/roles/{id}/
Content-Type: application/json

{
    "name": "Updated Role Name",
    "description": "Updated description",
    "permission_ids": ["uuid1", "uuid2", "uuid3"]
}
```

#### Delete Role
```http
DELETE /api/roles/{id}/
```

#### Add Permission to Role
```http
POST /api/roles/{id}/add_permission/
Content-Type: application/json

{
    "permission_code": "approve_variations"
}
```

#### Remove Permission from Role
```http
POST /api/roles/{id}/remove_permission/
Content-Type: application/json

{
    "permission_code": "approve_variations"
}
```

### Permissions API

#### List Permissions
```http
GET /api/permissions/
GET /api/permissions/?category=financial
GET /api/permissions/?is_active=true
```

#### Get Permissions by Category
```http
GET /api/permissions/by_category/
```

Returns:
```json
{
    "project": {
        "name": "Project Management",
        "permissions": [...]
    },
    "financial": {
        "name": "Financial Operations",
        "permissions": [...]
    }
}
```

### User Roles API

#### List User Role Assignments
```http
GET /api/user-roles/
GET /api/user-roles/?user_id=1
GET /api/user-roles/?role_code=project_manager
GET /api/user-roles/?organization_id=uuid
GET /api/user-roles/?project_id=uuid
GET /api/user-roles/?is_active=true
```

#### Assign Role to User
```http
POST /api/user-roles/assign/
Content-Type: application/json

{
    "user_id": 1,
    "role_code": "project_manager",
    "organization_id": "uuid",  // optional
    "project_id": "uuid",  // optional
    "expires_at": "2025-12-31T23:59:59Z",  // optional
    "notes": "Temporary assignment"  // optional
}
```

#### Remove Role from User
```http
POST /api/user-roles/remove/
Content-Type: application/json

{
    "user_id": 1,
    "role_code": "project_manager",
    "organization_id": "uuid",  // optional
    "project_id": "uuid"  // optional
}
```

#### Check User Permission
```http
POST /api/user-roles/check_permission/
Content-Type: application/json

{
    "user_id": 1,
    "permission_code": "approve_variations",
    "organization_id": "uuid",  // optional
    "project_id": "uuid"  // optional
}
```

Response:
```json
{
    "has_permission": true,
    "user_id": 1,
    "permission_code": "approve_variations"
}
```

#### Get User Permissions
```http
GET /api/user-roles/user_permissions/?user_id=1
GET /api/user-roles/user_permissions/?user_id=1&organization_id=uuid
GET /api/user-roles/user_permissions/?user_id=1&project_id=uuid
```

Response:
```json
{
    "user_id": 1,
    "permission_codes": ["view_project", "edit_project", "approve_variation"],
    "count": 3
}
```

#### Get User Roles
```http
GET /api/user-roles/user_roles/?user_id=1
GET /api/user-roles/user_roles/?user_id=1&organization_id=uuid
GET /api/user-roles/user_roles/?user_id=1&project_id=uuid
```

Response:
```json
{
    "user_id": 1,
    "roles": [
        {
            "role_code": "project_manager",
            "role_name": "Project Manager",
            "organization": "ABC Construction",
            "project": "Highway Project",
            "assigned_at": "2024-01-15T10:30:00Z",
            "expires_at": null
        }
    ],
    "count": 1
}
```

---

## Middleware

The `RBACMiddleware` automatically enforces permissions on API endpoints.

### Configuration

Add to `settings.py`:

```python
MIDDLEWARE = [
    # ... other middleware
    'apps.roles.middleware.RBACMiddleware',
]
```

### How It Works

1. **Public endpoints**: Bypass permission checks (login, register, etc.)
2. **Authenticated check**: Ensures user is logged in
3. **Superuser bypass**: Superusers have all permissions
4. **Permission mapping**: Matches URL pattern and HTTP method to required permission
5. **Context extraction**: Gets organization/project from request
6. **Permission check**: Verifies user has the required permission
7. **Response**: Allows request or returns 403 Forbidden

### Example Permission Mappings

```python
PERMISSION_MAPPINGS = [
    (r'^/api/projects/$', ['POST'], 'create_project'),
    (r'^/api/projects/\d+/$', ['PUT', 'PATCH'], 'edit_project'),
    (r'^/api/variations/\d+/approve/$', ['POST'], 'approve_variation'),
    (r'^/api/claims/\d+/certify/$', ['POST'], 'certify_claim'),
]
```

### Customization

To add new permission mappings, update `PERMISSION_MAPPINGS` in `middleware.py`:

```python
PERMISSION_MAPPINGS.append(
    (r'^/api/custom-endpoint/$', ['POST'], 'custom_permission')
)
```

---

## Usage Examples

### Example 1: Assign Project Manager Role

```python
from apps.roles.services import UserRoleService
from apps.authentication.models import User
from apps.projects.models import Project

user = User.objects.get(username='john.doe')
project = Project.objects.get(id='project-uuid')

# Assign project manager role for specific project
UserRoleService.assign_role(
    user=user,
    role_code='project_manager',
    project=project,
    assigned_by=request.user,
    notes='Assigned as PM for highway project'
)
```

### Example 2: Check Permission Before Action

```python
from apps.roles.services import UserRoleService

# Check if user can approve variations for this project
can_approve = UserRoleService.check_permission(
    user=request.user,
    permission_code='approve_variation',
    project=project
)

if can_approve:
    # Approve the variation
    variation.approve(approved_by=request.user)
else:
    raise PermissionDenied("You don't have permission to approve variations")
```

### Example 3: Use Permission Decorator

```python
from apps.roles.services import require_permission

@require_permission('approve_variation', project_field='project')
def approve_variation(request, variation_id):
    variation = get_object_or_404(Variation, id=variation_id)
    variation.approve(approved_by=request.user)
    return JsonResponse({'message': 'Variation approved'})
```

### Example 4: Temporary Role Assignment

```python
from datetime import datetime, timedelta
from apps.roles.services import UserRoleService

# Assign consultant role for 30 days
UserRoleService.assign_role(
    user=consultant_user,
    role_code='consultant',
    project=project,
    assigned_by=request.user,
    expires_at=datetime.now() + timedelta(days=30),
    notes='Temporary consultant for design review'
)
```

### Example 5: Bulk Permission Check

```python
from apps.roles.services import UserRoleService

# Check if user has ALL these permissions
required_perms = ['view_project', 'edit_project', 'approve_budget']

has_all = UserRoleService.check_all_permissions(
    user=request.user,
    permission_codes=required_perms,
    project=project
)

# Check if user has ANY of these permissions
optional_perms = ['approve_variation', 'certify_claim']

has_any = UserRoleService.check_any_permission(
    user=request.user,
    permission_codes=optional_perms,
    project=project
)
```

---

## Admin Interface

The Django admin interface provides powerful tools for managing RBAC:

### Role Admin Features
- Color-coded system/custom roles
- Active/inactive status indicators
- Permission count with drill-down links
- User count with drill-down links
- Protection against deleting system roles
- Horizontal filter for permissions

### Permission Admin Features
- Color-coded categories
- Category filtering
- Search by code/name
- Role count with drill-down links

### UserRole Admin Features
- User and role as clickable links
- Context display (organization/project)
- Color-coded status (active/expired/inactive)
- Expiry date display
- Bulk activate/deactivate actions
- Assignment history tracking

---

## Best Practices

### 1. Use Context Appropriately
```python
# ✅ Good: Assign role with appropriate context
UserRoleService.assign_role(
    user=user,
    role_code='project_manager',
    project=project  # Scoped to specific project
)

# ❌ Bad: System-wide when project-specific is more appropriate
UserRoleService.assign_role(
    user=user,
    role_code='project_manager'  # User is PM for ALL projects
)
```

### 2. Check Permissions, Not Roles
```python
# ✅ Good: Check specific permission
if UserRoleService.check_permission(user, 'approve_variation', project=project):
    approve_variation()

# ❌ Bad: Check role (less flexible)
if UserRoleSelector.has_role(user, 'project_manager', project=project):
    approve_variation()  # What if consultant also can approve?
```

### 3. Use Permission Decorators
```python
# ✅ Good: Declarative permission requirement
@require_permission('approve_variation', project_field='project')
def approve_variation_view(request, variation_id):
    # Permission already checked by decorator
    ...

# ❌ Bad: Manual check in every view
def approve_variation_view(request, variation_id):
    if not UserRoleService.check_permission(request.user, 'approve_variation'):
        raise PermissionDenied()
    ...
```

### 4. Set Expiry for Temporary Roles
```python
# ✅ Good: Temporary consultant with expiry
UserRoleService.assign_role(
    user=consultant,
    role_code='consultant',
    project=project,
    expires_at=contract_end_date
)

# ❌ Bad: No expiry for temporary role
UserRoleService.assign_role(
    user=consultant,
    role_code='consultant',
    project=project
    # Forgotten, stays active forever
)
```

### 5. Clean Up Expired Roles Periodically
```python
# Run as a scheduled task (e.g., daily)
from apps.roles.services import UserRoleService

deactivated_count = UserRoleService.cleanup_expired_roles()
print(f"Deactivated {deactivated_count} expired roles")
```

### 6. Don't Modify System Roles
```python
# ✅ Good: Create custom role for special needs
custom_role = RoleService.create_role(
    code='special_manager',
    name='Special Manager',
    permission_codes=[...],
    is_system_role=False
)

# ❌ Bad: Modifying system role
admin_role = RoleSelector.get_role_by_code('admin')
RoleService.update_role(admin_role, permission_codes=[...])  # Don't do this
```

### 7. Use Middleware for Consistent Enforcement
```python
# ✅ Good: Let middleware handle common cases
# Just configure PERMISSION_MAPPINGS in middleware.py

# ⚠️ Manual checks: Only for complex custom logic
def complex_approval_view(request):
    # Custom permission logic
    if request.user.organization.is_premium:
        required_perm = 'approve_premium'
    else:
        required_perm = 'approve_standard'
    
    if not UserRoleService.check_permission(request.user, required_perm):
        raise PermissionDenied()
```

---

## Integration Checklist

- [ ] Add `'apps.roles'` to `INSTALLED_APPS`
- [ ] Add `'apps.roles.middleware.RBACMiddleware'` to `MIDDLEWARE`
- [ ] Include RBAC URLs in main `urls.py`: `path('api/', include('apps.roles.urls'))`
- [ ] Run migrations: `python manage.py makemigrations roles && python manage.py migrate`
- [ ] Create default roles and permissions (management command recommended)
- [ ] Update existing API views with permission checks
- [ ] Configure middleware permission mappings
- [ ] Train users on the permission system

---

## Troubleshooting

### User Has Role But Permission Check Fails
1. Check if role assignment is active: `user_role.is_active == True`
2. Check if role assignment is expired: `user_role.is_expired == False`
3. Verify role has the permission: `permission in role.permissions.all()`
4. Check context matches: If assigned at project level, check at project level

### Middleware Returns 403 But User Should Have Access
1. Check `PUBLIC_ENDPOINTS` in middleware
2. Verify `PERMISSION_MAPPINGS` includes the endpoint
3. Ensure permission code matches exactly
4. Check if context extraction is working correctly

### Role Assignment Fails
1. Check unique constraint: User may already have that role in that context
2. Verify role code exists
3. Ensure organization/project exists if providing IDs

---

## Future Enhancements

- [ ] Permission inheritance (parent-child relationships)
- [ ] Role templates for quick setup
- [ ] Permission groups for easier management
- [ ] Audit trail for role changes (integrate with events module)
- [ ] API rate limiting per role
- [ ] Conditional permissions (e.g., "approve if < $10,000")
- [ ] Role delegation (temporary transfer of permissions)

---

For questions or issues, contact the COMS development team.
