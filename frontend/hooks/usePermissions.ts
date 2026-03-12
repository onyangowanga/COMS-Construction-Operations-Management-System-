// ============================================================================
// USE PERMISSIONS HOOK
// Custom hook for permission checking
// ============================================================================

'use client';

import { useCallback } from 'react';
import { useAuthStore } from '@/store';
import { permissionService } from '@/services';

interface PermissionContext {
  organizationId?: number;
  projectId?: number;
}

export function usePermissions() {
  const { user, hasPermission, hasRole, hasAnyPermission, hasAllPermissions } = useAuthStore();

  // Check permission with backend (for context-aware checks)
  const checkPermission = useCallback(
    async (permissionCode: string, context?: PermissionContext): Promise<boolean> => {
      if (!user) return false;

      try {
        const result = await permissionService.checkPermission(
          user.id,
          permissionCode,
          context
        );
        return result;
      } catch (error) {
        console.error('Permission check error:', error);
        return false;
      }
    },
    [user]
  );

  // Get user permissions with context
  const getUserPermissions = useCallback(
    async (context?: PermissionContext): Promise<string[]> => {
      if (!user) return [];

      try {
        const permissions = await permissionService.getUserPermissions(user.id, context);
        return permissions;
      } catch (error) {
        console.error('Failed to get user permissions:', error);
        return [];
      }
    },
    [user]
  );

  // Get user roles with context
  const getUserRoles = useCallback(
    async (context?: PermissionContext) => {
      if (!user) return [];

      try {
        const roles = await permissionService.getUserRoles(user.id, context);
        return roles;
      } catch (error) {
        console.error('Failed to get user roles:', error);
        return [];
      }
    },
    [user]
  );

  return {
    user,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions,
    checkPermission,
    getUserPermissions,
    getUserRoles,
  };
}
