"""
API Views for Role-Based Access Control

This module provides REST API endpoints for managing roles, permissions, and user roles.
"""

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from apps.roles.models import Role, Permission, UserRole
from apps.roles.serializers import (
    RoleSerializer,
    PermissionSerializer,
    UserRoleSerializer,
    AssignRoleSerializer,
    RemoveRoleSerializer,
    CheckPermissionSerializer,
    UserPermissionsSerializer
)
from apps.roles.services import RoleService, PermissionService, UserRoleService
from apps.roles.selectors import RoleSelector, PermissionSelector, UserRoleSelector

User = get_user_model()


class RoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing roles.
    
    Endpoints:
    - GET /api/roles/ - List all roles
    - POST /api/roles/ - Create a new role
    - GET /api/roles/{id}/ - Get role details
    - PUT /api/roles/{id}/ - Update a role
    - DELETE /api/roles/{id}/ - Delete a role (custom roles only)
    - GET /api/roles/system/ - List system roles
    - POST /api/roles/{id}/add_permission/ - Add permission to role
    - POST /api/roles/{id}/remove_permission/ - Remove permission from role
    """
    
    queryset = Role.objects.all()
    serializer_class = RoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = RoleSelector.get_all_roles()
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter system roles
        is_system = self.request.query_params.get('is_system_role')
        if is_system is not None:
            queryset = queryset.filter(is_system_role=is_system.lower() == 'true')
        
        return queryset
    
    def destroy(self, request, *args, **kwargs):
        """Delete a role (prevent deletion of system roles)."""
        instance = self.get_object()
        
        try:
            RoleService.delete_role(instance)
            return Response(status=status.HTTP_204_NO_CONTENT)
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['get'])
    def system(self, request):
        """Get all system roles."""
        roles = RoleSelector.get_system_roles()
        serializer = self.get_serializer(roles, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def add_permission(self, request, pk=None):
        """Add a permission to a role."""
        role = self.get_object()
        permission_code = request.data.get('permission_code')
        
        if not permission_code:
            return Response(
                {'error': 'permission_code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            RoleService.add_permission_to_role(role, permission_code)
            serializer = self.get_serializer(role)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=True, methods=['post'])
    def remove_permission(self, request, pk=None):
        """Remove a permission from a role."""
        role = self.get_object()
        permission_code = request.data.get('permission_code')
        
        if not permission_code:
            return Response(
                {'error': 'permission_code is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            RoleService.remove_permission_from_role(role, permission_code)
            serializer = self.get_serializer(role)
            return Response(serializer.data)
        except Exception as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PermissionViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing permissions.
    
    Endpoints:
    - GET /api/permissions/ - List all permissions
    - GET /api/permissions/{id}/ - Get permission details
    - GET /api/permissions/by_category/ - List permissions grouped by category
    """
    
    queryset = Permission.objects.all()
    serializer_class = PermissionSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = PermissionSelector.get_all_permissions()
        
        # Filter by category
        category = self.request.query_params.get('category')
        if category:
            queryset = queryset.filter(category=category)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def by_category(self, request):
        """Get permissions grouped by category."""
        categories = {}
        
        for category_code, category_name in Permission.CATEGORY_CHOICES:
            permissions = PermissionSelector.get_permissions_by_category(category_code)
            serializer = self.get_serializer(permissions, many=True)
            categories[category_code] = {
                'name': category_name,
                'permissions': serializer.data
            }
        
        return Response(categories)


class UserRoleViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing user role assignments.
    
    Endpoints:
    - GET /api/user-roles/ - List all user role assignments
    - POST /api/user-roles/ - Create a role assignment
    - GET /api/user-roles/{id}/ - Get assignment details
    - PUT /api/user-roles/{id}/ - Update an assignment
    - DELETE /api/user-roles/{id}/ - Delete an assignment
    - POST /api/user-roles/assign/ - Assign role to user
    - POST /api/user-roles/remove/ - Remove role from user
    - POST /api/user-roles/check_permission/ - Check user permission
    - GET /api/user-roles/user_permissions/ - Get user's permissions
    - GET /api/user-roles/user_roles/ - Get user's roles
    """
    
    queryset = UserRole.objects.all()
    serializer_class = UserRoleSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get filtered queryset based on query parameters."""
        queryset = UserRole.objects.select_related(
            'user', 'role', 'organization', 'project', 'assigned_by'
        ).prefetch_related('role__permissions')
        
        # Filter by user
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(user_id=user_id)
        
        # Filter by role
        role_code = self.request.query_params.get('role_code')
        if role_code:
            queryset = queryset.filter(role__code=role_code)
        
        # Filter by organization
        org_id = self.request.query_params.get('organization_id')
        if org_id:
            queryset = queryset.filter(organization_id=org_id)
        
        # Filter by project
        project_id = self.request.query_params.get('project_id')
        if project_id:
            queryset = queryset.filter(project_id=project_id)
        
        # Filter by active status
        is_active = self.request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')
        
        # Filter expired
        include_expired = self.request.query_params.get('include_expired', 'false')
        if include_expired.lower() == 'false':
            from django.utils import timezone
            from django.db.models import Q
            queryset = queryset.filter(
                Q(expires_at__isnull=True) | Q(expires_at__gt=timezone.now())
            )
        
        return queryset.order_by('-assigned_at')
    
    @action(detail=False, methods=['post'])
    def assign(self, request):
        """
        Assign a role to a user.
        
        Request body:
        {
            "user_id": 1,
            "role_code": "project_manager",
            "organization_id": "uuid",  # optional
            "project_id": "uuid",  # optional
            "expires_at": "2025-01-01T00:00:00Z",  # optional
            "notes": "Temporary assignment"  # optional
        }
        """
        serializer = AssignRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        role_code = serializer.validated_data['role_code']
        
        # Get context objects
        organization = None
        project = None
        
        org_id = serializer.validated_data.get('organization_id')
        if org_id:
            from apps.authentication.models import Organization
            organization = get_object_or_404(Organization, id=org_id)
        
        proj_id = serializer.validated_data.get('project_id')
        if proj_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, id=proj_id)
        
        try:
            user_role = UserRoleService.assign_role(
                user=user,
                role_code=role_code,
                organization=organization,
                project=project,
                assigned_by=request.user,
                expires_at=serializer.validated_data.get('expires_at'),
                notes=serializer.validated_data.get('notes', '')
            )
            
            result_serializer = UserRoleSerializer(user_role)
            return Response(result_serializer.data, status=status.HTTP_201_CREATED)
        
        except ValueError as e:
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    @action(detail=False, methods=['post'])
    def remove(self, request):
        """
        Remove a role from a user.
        
        Request body:
        {
            "user_id": 1,
            "role_code": "project_manager",
            "organization_id": "uuid",  # optional
            "project_id": "uuid"  # optional
        }
        """
        serializer = RemoveRoleSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        role_code = serializer.validated_data['role_code']
        
        # Get context objects
        organization = None
        project = None
        
        org_id = serializer.validated_data.get('organization_id')
        if org_id:
            from apps.authentication.models import Organization
            organization = get_object_or_404(Organization, id=org_id)
        
        proj_id = serializer.validated_data.get('project_id')
        if proj_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, id=proj_id)
        
        success = UserRoleService.remove_role(
            user=user,
            role_code=role_code,
            organization=organization,
            project=project
        )
        
        if success:
            return Response({'message': 'Role removed successfully'})
        else:
            return Response(
                {'error': 'Role assignment not found'},
                status=status.HTTP_404_NOT_FOUND
            )
    
    @action(detail=False, methods=['post'])
    def check_permission(self, request):
        """
        Check if a user has a specific permission.
        
        Request body:
        {
            "user_id": 1,
            "permission_code": "approve_variations",
            "organization_id": "uuid",  # optional
            "project_id": "uuid"  # optional
        }
        """
        serializer = CheckPermissionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = get_object_or_404(User, id=serializer.validated_data['user_id'])
        permission_code = serializer.validated_data['permission_code']
        
        # Get context objects
        organization = None
        project = None
        
        org_id = serializer.validated_data.get('organization_id')
        if org_id:
            from apps.authentication.models import Organization
            organization = get_object_or_404(Organization, id=org_id)
        
        proj_id = serializer.validated_data.get('project_id')
        if proj_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, id=proj_id)
        
        has_permission = UserRoleService.check_permission(
            user=user,
            permission_code=permission_code,
            organization=organization,
            project=project
        )
        
        return Response({
            'has_permission': has_permission,
            'user_id': user.id,
            'permission_code': permission_code
        })
    
    @action(detail=False, methods=['get'])
    def user_permissions(self, request):
        """
        Get all permissions for a user.
        
        Query params:
        - user_id: ID of the user (required)
        - organization_id: Organization context (optional)
        - project_id: Project context (optional)
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        
        # Get context objects
        organization = None
        project = None
        
        org_id = request.query_params.get('organization_id')
        if org_id:
            from apps.authentication.models import Organization
            organization = get_object_or_404(Organization, id=org_id)
        
        proj_id = request.query_params.get('project_id')
        if proj_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, id=proj_id)
        
        permissions = UserRoleService.get_user_permissions(
            user=user,
            organization=organization,
            project=project
        )
        
        return Response({
            'user_id': user.id,
            'permission_codes': permissions,
            'count': len(permissions)
        })
    
    @action(detail=False, methods=['get'])
    def user_roles(self, request):
        """
        Get all roles for a user with details.
        
        Query params:
        - user_id: ID of the user (required)
        - organization_id: Organization context (optional)
        - project_id: Project context (optional)
        """
        user_id = request.query_params.get('user_id')
        if not user_id:
            return Response(
                {'error': 'user_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        user = get_object_or_404(User, id=user_id)
        
        # Get context objects
        organization = None
        project = None
        
        org_id = request.query_params.get('organization_id')
        if org_id:
            from apps.authentication.models import Organization
            organization = get_object_or_404(Organization, id=org_id)
        
        proj_id = request.query_params.get('project_id')
        if proj_id:
            from apps.projects.models import Project
            project = get_object_or_404(Project, id=proj_id)
        
        roles = UserRoleService.get_user_roles(
            user=user,
            organization=organization,
            project=project
        )
        
        return Response({
            'user_id': user.id,
            'roles': roles,
            'count': len(roles)
        })
