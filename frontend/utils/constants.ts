// ============================================================================
// APPLICATION CONSTANTS
// ============================================================================

export const APP_NAME = 'COMS';
export const APP_VERSION = '1.0.0';

// API Configuration
export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
export const WS_URL = process.env.NEXT_PUBLIC_WS_URL || 'ws://localhost:8000/ws';

// Token Configuration
export const TOKEN_KEY = 'coms_access_token';
export const REFRESH_TOKEN_KEY = 'coms_refresh_token';
export const USER_KEY = 'coms_user';
export const TOKEN_EXPIRY = parseInt(process.env.NEXT_PUBLIC_TOKEN_EXPIRY || '3600');

// Pagination
export const DEFAULT_PAGE_SIZE = 20;
export const PAGE_SIZE_OPTIONS = [10, 20, 50, 100];

// Date Formats
export const DATE_FORMAT = 'MMM dd, yyyy';
export const DATETIME_FORMAT = 'MMM dd, yyyy HH:mm';
export const TIME_FORMAT = 'HH:mm';
export const API_DATE_FORMAT = 'yyyy-MM-dd';
export const API_DATETIME_FORMAT = "yyyy-MM-dd'T'HH:mm:ss";

// Project Status Options
export const PROJECT_STATUS_OPTIONS = [
  { value: 'planning', label: 'Planning', color: 'bg-blue-100 text-blue-800' },
  { value: 'active', label: 'Active', color: 'bg-green-100 text-green-800' },
  { value: 'on_hold', label: 'On Hold', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'completed', label: 'Completed', color: 'bg-gray-100 text-gray-800' },
  { value: 'cancelled', label: 'Cancelled', color: 'bg-red-100 text-red-800' },
];

// Variation Status Options
export const VARIATION_STATUS_OPTIONS = [
  { value: 'draft', label: 'Draft', color: 'bg-gray-100 text-gray-800' },
  { value: 'submitted', label: 'Submitted', color: 'bg-blue-100 text-blue-800' },
  { value: 'under_review', label: 'Under Review', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'approved', label: 'Approved', color: 'bg-green-100 text-green-800' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' },
  { value: 'implemented', label: 'Implemented', color: 'bg-purple-100 text-purple-800' },
];

// Claim Status Options
export const CLAIM_STATUS_OPTIONS = [
  { value: 'draft', label: 'Draft', color: 'bg-gray-100 text-gray-800' },
  { value: 'submitted', label: 'Submitted', color: 'bg-blue-100 text-blue-800' },
  { value: 'under_review', label: 'Under Review', color: 'bg-yellow-100 text-yellow-800' },
  { value: 'certified', label: 'Certified', color: 'bg-indigo-100 text-indigo-800' },
  { value: 'approved', label: 'Approved', color: 'bg-green-100 text-green-800' },
  { value: 'paid', label: 'Paid', color: 'bg-emerald-100 text-emerald-800' },
  { value: 'rejected', label: 'Rejected', color: 'bg-red-100 text-red-800' },
];

// Priority Options
export const PRIORITY_OPTIONS = [
  { value: 'low', label: 'Low', color: 'bg-gray-100 text-gray-800' },
  { value: 'medium', label: 'Medium', color: 'bg-blue-100 text-blue-800' },
  { value: 'high', label: 'High', color: 'bg-orange-100 text-orange-800' },
  { value: 'critical', label: 'Critical', color: 'bg-red-100 text-red-800' },
];

// Sidebar Navigation Items
export const SIDEBAR_NAVIGATION = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: 'LayoutDashboard',
    permission: null,
  },
  {
    name: 'Projects',
    href: '/projects',
    icon: 'FolderKanban',
    permission: 'view_project',
  },
  {
    name: 'Contracts',
    href: '/contracts',
    icon: 'FileText',
    permission: ['contract.view', 'view_contract', 'contract.create'],
  },
  {
    name: 'Activity',
    href: '/activity',
    icon: 'Activity',
    permission: ['activity.view', 'view_activity'],
  },
  {
    name: 'Notifications',
    href: '/notifications',
    icon: 'Bell',
    permission: ['notification.view', 'view_notification'],
  },
  {
    name: 'Documents',
    href: '/documents',
    icon: 'FileStack',
    permission: null,
  },
  {
    name: 'Variations',
    href: '/variations',
    icon: 'GitBranch',
    permission: null,
  },
  {
    name: 'Claims',
    href: '/claims',
    icon: 'Receipt',
    permission: null,
  },
  {
    name: 'Procurement',
    href: '/procurement',
    icon: 'ShoppingCart',
    permission: ['procurement.view', 'view_procurement', 'view_procurement_order', 'procurement.create', 'view_lpo'],
  },
  {
    name: 'Subcontractors',
    href: '/subcontractors',
    icon: 'Users',
    permission: ['subcontractor.view', 'view_subcontractor', 'view_subcontract', 'subcontractor.create'],
  },
  {
    name: 'Suppliers',
    href: '/suppliers',
    icon: 'Users',
    permission: ['supplier.view', 'view_supplier', 'supplier.create'],
  },
  {
    name: 'Reports',
    href: '/reports',
    icon: 'BarChart3',
    permission: 'view_report',
  },
  {
    name: 'Administration',
    href: '/system-admin',
    icon: 'Settings',
    permission: 'manage_users',
    subsections: [
      { name: 'Users', href: '/system-admin/users', permission: 'manage_users' },
      { name: 'Roles', href: '/system-admin/roles', permission: 'manage_roles' },
      { name: 'Permissions', href: '/system-admin/permissions', permission: 'manage_roles' },
      { name: 'Workflows', href: '/system-admin/workflows', permission: 'manage_roles' },
      { name: 'Organizations', href: '/system-admin/organizations', permission: 'manage_organizations' },
      { name: 'Notifications', href: '/system-admin/notifications', permission: 'manage_users' },
    ],
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: 'Settings2',
    permission: null,
    subsections: [
      { name: 'Profile', href: '/settings/profile' },
      { name: 'Notifications', href: '/settings/notifications' },
      { name: 'Preferences', href: '/settings/preferences' },
      { name: 'Organization', href: '/settings/organization' },
      { name: 'Security', href: '/settings/security' },
    ],
  },
];

// Chart Colors
export const CHART_COLORS= {
  primary: '#0ea5e9',
  secondary: '#8b5cf6',
  success: '#10b981',
  warning: '#f59e0b',
  danger: '#ef4444',
  info: '#3b82f6',
  gray: '#6b7280',
};

// Notification Types Configuration
export const NOTIFICATION_TYPE_CONFIG = {
  info: { icon: 'Info', color: 'text-blue-600' },
  success: { icon: 'CheckCircle2', color: 'text-green-600' },
  warning: { icon: 'AlertTriangle', color: 'text-yellow-600' },
  error: { icon: 'XCircle', color: 'text-red-600' },
  approval_required: { icon: 'Clock', color: 'text-orange-600' },
  document_uploaded: { icon: 'FileUp', color: 'text-blue-600' },
  variation_created: { icon: 'GitBranch', color: 'text-purple-600' },
  claim_submitted: { icon: 'Receipt', color: 'text-green-600' },
  payment_approved: { icon: 'DollarSign', color: 'text-emerald-600' },
};
