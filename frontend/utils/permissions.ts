// ============================================================================
// PERMISSION UTILITIES
// ============================================================================

/**
 * Permission mapping for common actions
 */
export const PERMISSIONS = {
  // Project permissions
  PROJECT_VIEW: 'view_project',
  PROJECT_CREATE: 'create_project',
  PROJECT_EDIT: 'edit_project',
  PROJECT_DELETE: 'delete_project',
  
  // Variation permissions
  VARIATION_VIEW: 'view_variation',
  VARIATION_CREATE: 'create_variation',
  VARIATION_APPROVE: 'approve_variation',
  VARIATION_REJECT: 'reject_variation',
  
  // Claim permissions
  CLAIM_VIEW: 'view_claim',
  CLAIM_CREATE: 'create_claim',
  CLAIM_CERTIFY: 'certify_claim',
  CLAIM_APPROVE: 'approve_claim',
  
  // Payment permissions
  PAYMENT_VIEW: 'view_payment',
  PAYMENT_CREATE: 'create_payment',
  PAYMENT_APPROVE: 'approve_payment',
  
  // Document permissions
  DOCUMENT_VIEW: 'view_document',
  DOCUMENT_UPLOAD: 'upload_document',
  DOCUMENT_DELETE: 'delete_document',
  DOCUMENT_APPROVE: 'approve_document',
  
  // Financial permissions
  FINANCIAL_VIEW: 'view_financials',
  BUDGET_MANAGE: 'manage_budget',
  
  // Procurement permissions
  LPO_CREATE: 'create_lpo',
  LPO_APPROVE: 'approve_lpo',
  
  // Report permissions
  REPORT_VIEW: 'view_report',
  REPORT_GENERATE: 'generate_report',
  
  // System permissions
  USER_MANAGE: 'manage_users',
  ROLE_MANAGE: 'manage_roles',
  SYSTEM_SETTINGS: 'system_settings',
} as const;

/**
 * Role codes
 */
export const ROLES = {
  ADMIN: 'admin',
  FINANCE_MANAGER: 'finance_manager',
  PROJECT_MANAGER: 'project_manager',
  SITE_ENGINEER: 'site_engineer',
  CONSULTANT: 'consultant',
  CLIENT: 'client',
  SUPPLIER: 'supplier',
  SUBCONTRACTOR: 'subcontractor',
} as const;

/**
 * Check if user has a specific permission
 */
export function hasPermission(
  userPermissions: string[] | undefined,
  requiredPermission: string
): boolean {
  if (!userPermissions) return false;
  return userPermissions.includes(requiredPermission);
}

/**
 * Check if user has any of the specified permissions
 */
export function hasAnyPermission(
  userPermissions: string[] | undefined,
  requiredPermissions: string[]
): boolean {
  if (!userPermissions) return false;
  return requiredPermissions.some(permission => 
    userPermissions.includes(permission)
  );
}

/**
 * Check if user has all of the specified permissions
 */
export function hasAllPermissions(
  userPermissions: string[] | undefined,
  requiredPermissions: string[]
): boolean {
  if (!userPermissions) return false;
  return requiredPermissions.every(permission => 
    userPermissions.includes(permission)
  );
}

/**
 * Check if user has a specific role
 */
export function hasRole(
  userRoles: string[] | undefined,
  requiredRole: string
): boolean {
  if (!userRoles) return false;
  return userRoles.includes(requiredRole);
}

/**
 * Get permission label
 */
export function getPermissionLabel(permissionCode: string): string {
  return permissionCode
    .split('_')
    .map(word => word.charAt(0).toUpperCase() + word.slice(1))
    .join(' ');
}
