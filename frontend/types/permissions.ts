// ============================================================================
// PERMISSION & ROLE TYPES
// ============================================================================

export interface Role {
  id: string;
  code: string;
  name: string;
  description: string;
  is_system_role: boolean;
  is_active: boolean;
  permissions: Permission[];
  permission_count: number;
  user_count: number;
}

export interface Permission {
  id: string;
  code: string;
  name: string;
  description: string;
  category: PermissionCategory;
  is_active: boolean;
}

export enum PermissionCategory {
  PROJECT = 'project',
  FINANCIAL = 'financial',
  DOCUMENT = 'document',
  VARIATION = 'variation',
  CLAIM = 'claim',
  PAYMENT = 'payment',
  APPROVAL = 'approval',
  REPORT = 'report',
  PROCUREMENT = 'procurement',
  SUBCONTRACT = 'subcontract',
  SITE_OPERATIONS = 'site_operations',
  SYSTEM = 'system',
}

export interface PermissionCheck {
  has_permission: boolean;
  user_id: number;
  permission_code: string;
}
