"""
Role-Based Access Control Middleware

This module provides middleware for enforcing permissions on API endpoints.
"""

from django.http import JsonResponse
from django.utils.deprecation import MiddlewareMixin
from apps.roles.roles_selectors import UserRoleSelector
import re


class RBACMiddleware(MiddlewareMixin):
    """
    Middleware to enforce role-based permissions on API endpoints.
    
    This middleware checks if the request user has the required permission
    to access specific API endpoints based on predefined permission mappings.
    """
    
    # Permission mappings for different endpoint patterns
    # Format: (pattern, http_methods, permission_code)
    PERMISSION_MAPPINGS = [
        # Project endpoints
        (r'^/api/projects/$', ['POST'], 'create_project'),
        (r'^/api/projects/\d+/$', ['PUT', 'PATCH'], 'edit_project'),
        (r'^/api/projects/\d+/$', ['DELETE'], 'delete_project'),
        (r'^/api/projects/\d+/$', ['GET'], 'view_project'),
        
        # Financial endpoints
        (r'^/api/financials/', ['GET'], 'view_financials'),
        (r'^/api/budgets/', ['POST', 'PUT', 'PATCH'], 'manage_budget'),
        
        # Variation endpoints
        (r'^/api/variations/$', ['POST'], 'create_variation'),
        (r'^/api/variations/\d+/approve/$', ['POST'], 'approve_variation'),
        (r'^/api/variations/\d+/reject/$', ['POST'], 'reject_variation'),
        
        # Claim endpoints
        (r'^/api/claims/$', ['POST'], 'create_claim'),
        (r'^/api/claims/\d+/certify/$', ['POST'], 'certify_claim'),
        (r'^/api/claims/\d+/approve/$', ['POST'], 'approve_claim'),
        
        # Payment endpoints
        (r'^/api/payments/$', ['POST'], 'create_payment'),
        (r'^/api/payments/\d+/approve/$', ['POST'], 'approve_payment'),
        
        # Document endpoints
        (r'^/api/documents/$', ['POST'], 'upload_document'),
        (r'^/api/documents/\d+/$', ['DELETE'], 'delete_document'),
        (r'^/api/documents/\d+/$', ['GET'], 'view_document'),
        
        # Report endpoints
        (r'^/api/reports/', ['GET'], 'view_report'),
        (r'^/api/reports/generate/', ['POST'], 'generate_report'),
        
        # Procurement endpoints
        (r'^/api/lpos/$', ['POST'], 'create_lpo'),
        (r'^/api/lpos/\d+/approve/$', ['POST'], 'approve_lpo'),
        
        # User management
        (r'^/api/users/', ['GET'], 'view_users'),
        (r'^/api/users/', ['POST', 'PUT', 'PATCH'], 'manage_users'),
        
        # Role management
        (r'^/api/roles/', ['GET'], 'view_roles'),
        (r'^/api/roles/', ['POST', 'PUT', 'PATCH', 'DELETE'], 'manage_roles'),
    ]
    
    # Public endpoints that don't require authentication or permissions
    PUBLIC_ENDPOINTS = [
        r'^/api/auth/login/$',
        r'^/api/auth/register/$',
        r'^/api/auth/password-reset/$',
        r'^/api/health/$',
        r'^/api/status/$',
    ]
    
    def process_request(self, request):
        """
        Process each request to check permissions.
        
        Args:
            request: Django request object
            
        Returns:
            None if permission granted, JsonResponse with 403 if denied
        """
        # Skip non-API requests
        if not request.path.startswith('/api/'):
            return None
        
        # Check if endpoint is public
        if self._is_public_endpoint(request.path):
            return None
        
        # Check if user is authenticated
        if not hasattr(request, 'user') or not request.user.is_authenticated:
            return JsonResponse(
                {'error': 'Authentication required'},
                status=401
            )
        
        # Superusers have all permissions
        if request.user.is_superuser:
            return None
        
        # Find matching permission requirement
        required_permission = self._get_required_permission(request.path, request.method)
        
        # If no permission mapping exists, allow the request
        # (This allows for endpoints that don't need specific permissions)
        if not required_permission:
            return None
        
        # Get context from request
        organization = self._get_organization_from_request(request)
        project = self._get_project_from_request(request)
        
        # Check if user has the required permission
        has_permission = UserRoleSelector.has_permission(
            user=request.user,
            permission_code=required_permission,
            organization=organization,
            project=project
        )
        
        if not has_permission:
            return JsonResponse(
                {
                    'error': 'Permission denied',
                    'required_permission': required_permission,
                    'message': f'You do not have the required permission: {required_permission}'
                },
                status=403
            )
        
        # Permission granted
        return None
    
    def _is_public_endpoint(self, path: str) -> bool:
        """
        Check if the endpoint is public.
        
        Args:
            path: Request path
            
        Returns:
            Boolean indicating if endpoint is public
        """
        for pattern in self.PUBLIC_ENDPOINTS:
            if re.match(pattern, path):
                return True
        return False
    
    def _get_required_permission(self, path: str, method: str) -> str:
        """
        Get the required permission for a path and method.
        
        Args:
            path: Request path
            method: HTTP method
            
        Returns:
            Permission code or None
        """
        for pattern, methods, permission in self.PERMISSION_MAPPINGS:
            if re.match(pattern, path) and method.upper() in methods:
                return permission
        return None
    
    def _get_organization_from_request(self, request):
        """
        Extract organization from request data or query parameters.
        
        Args:
            request: Django request object
            
        Returns:
            Organization instance or None
        """
        org_id = None
        
        # Try to get from query parameters
        if hasattr(request, 'GET'):
            org_id = request.GET.get('organization_id') or request.GET.get('organization')
        
        # Try to get from request body
        if not org_id and hasattr(request, 'data'):
            org_id = request.data.get('organization_id') or request.data.get('organization')
        
        if org_id:
            try:
                from apps.authentication.models import Organization
                return Organization.objects.get(id=org_id)
            except Organization.DoesNotExist:
                pass
        
        return None
    
    def _get_project_from_request(self, request):
        """
        Extract project from request data, query parameters, or URL.
        
        Args:
            request: Django request object
            
        Returns:
            Project instance or None
        """
        project_id = None
        
        # Try to get from query parameters
        if hasattr(request, 'GET'):
            project_id = request.GET.get('project_id') or request.GET.get('project')
        
        # Try to get from request body
        if not project_id and hasattr(request, 'data'):
            project_id = request.data.get('project_id') or request.data.get('project')
        
        # Try to extract from URL path (e.g., /api/projects/123/)
        if not project_id:
            match = re.search(r'/api/projects/(\d+)/', request.path)
            if match:
                project_id = match.group(1)
        
        if project_id:
            try:
                from apps.projects.models import Project
                return Project.objects.get(id=project_id)
            except Project.DoesNotExist:
                pass
        
        return None
