"""
URL Configuration for Role-Based Access Control API

This module defines URL patterns for RBAC REST API endpoints.
"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from apps.roles.views import RoleViewSet, PermissionViewSet, UserRoleViewSet

# Create router
router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'permissions', PermissionViewSet, basename='permission')
router.register(r'user-roles', UserRoleViewSet, basename='user-role')

app_name = 'roles'

urlpatterns = [
    path('', include(router.urls)),
]
