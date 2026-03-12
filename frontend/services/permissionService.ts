// ============================================================================
// PERMISSION SERVICE
// Handles RBAC permission checking and management
// ============================================================================

import { api } from './apiClient';
import type { Permission, PermissionCheck, Role, User } from '@/types';

export const permissionService = {
  /**
   * Get user permissions
   */
  async getUserPermissions(userId: number, context?: {
    organizationId?: string;
    projectId?: string;
  }): Promise<string[]> {
    try {
      const params: any = { user_id: userId };
      
      if (context?.organizationId) {
        params.organization_id = context.organizationId;
      }
      
      if (context?.projectId) {
        params.project_id = context.projectId;
      }

      const response = await api.get<{
        permission_codes: string[];
        count: number;
      }>('/user-roles/user_permissions/', { params });
      
      return response.permission_codes;
    } catch (error) {
      console.error('Failed to fetch user permissions:', error);
      return [];
    }
  },

  /**
   * Check if user has specific permission
   */
  async checkPermission(data: {
    userId: number;
    permissionCode: string;
    organizationId?: string;
    projectId?: string;
  }): Promise<boolean> {
    try {
      const response = await api.post<PermissionCheck>('/user-roles/check_permission/', {
        user_id: data.userId,
        permission_code: data.permissionCode,
        organization_id: data.organizationId,
        project_id: data.projectId,
      });
      
      return response.has_permission;
    } catch (error) {
      console.error('Permission check failed:', error);
      return false;
    }
  },

  /**
   * Get user roles
   */
  async getUserRoles(userId: number, context?: {
    organizationId?: string;
    projectId?: string;
  }): Promise<any[]> {
    try {
      const params: any = { user_id: userId };
      
      if (context?.organizationId) {
        params.organization_id = context.organizationId;
      }
      
      if (context?.projectId) {
        params.project_id = context.projectId;
      }

      const response = await api.get<{
        roles: any[];
        count: number;
      }>('/user-roles/user_roles/', { params });
      
      return response.roles;
    } catch (error) {
      console.error('Failed to fetch user roles:', error);
      return [];
    }
  },

  /**
   * Assign role to user
   */
  async assignRole(data: {
    userId: number;
    roleCode: string;
    organizationId?: string;
    projectId?: string;
    expiresAt?: string;
    notes?: string;
  }): Promise<any> {
    try {
      const response = await api.post('/user-roles/assign/', {
        user_id: data.userId,
        role_code: data.roleCode,
        organization_id: data.organizationId,
        project_id: data.projectId,
        expires_at: data.expiresAt,
        notes: data.notes,
      });
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Remove role from user
   */
  async removeRole(data: {
    userId: number;
    roleCode: string;
    organizationId?: string;
    projectId?: string;
  }): Promise<void> {
    try {
      await api.post('/user-roles/remove/', {
        user_id: data.userId,
        role_code: data.roleCode,
        organization_id: data.organizationId,
        project_id: data.projectId,
      });
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get all roles
   */
  async getAllRoles(): Promise<Role[]> {
    try {
      const response = await api.get<Role[]>('/roles/');
      return response;
    } catch (error) {
      console.error('Failed to fetch roles:', error);
      return [];
    }
  },

  /**
   * Get all permissions
   */
  async getAllPermissions(): Promise<Permission[]> {
    try {
      const response = await api.get<Permission[]>('/permissions/');
      return response;
    } catch (error) {
      console.error('Failed to fetch permissions:', error);
      return [];
    }
  },

  /**
   * Get permissions by category
   */
  async getPermissionsByCategory(): Promise<Record<string, any>> {
    try {
      const response = await api.get('/permissions/by_category/');
      return response;
    } catch (error) {
      console.error('Failed to fetch permissions by category:', error);
      return {};
    }
  },
};
