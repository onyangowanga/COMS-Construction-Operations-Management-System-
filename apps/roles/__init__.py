"""
COMS Role-Based Access Control (RBAC) Module

This module provides comprehensive role and permission management for the COMS platform.
It implements fine-grained access control for all features and modules.

Key Features:
- 8 predefined roles (Admin, Finance Manager, Project Manager, etc.)
- 50+ granular permissions
- Role-based permission assignment
- User-role associations
- Permission checking utilities
- Middleware for automatic permission enforcement
- API endpoints for role management
"""

default_app_config = 'apps.roles.apps.RolesConfig'
