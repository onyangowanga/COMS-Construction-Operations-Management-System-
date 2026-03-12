// ============================================================================
// USER & AUTHENTICATION TYPES
// ============================================================================

export interface User {
  id: number;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  is_active: boolean;
  is_staff: boolean;
  is_superuser: boolean;
  date_joined: string;
  last_login: string | null;
  organization?: Organization;
  roles?: UserRole[];
  permissions?: string[];
}

export interface Organization {
  id: string;
  name: string;
  logo?: string;
  address?: string;
  phone?: string;
  email?: string;
  created_at: string;
}

export interface UserRole {
  id: string;
  role_code: string;
  role_name: string;
  organization?: string;
  organization_name?: string;
  project?: string;
  project_name?: string;
  assigned_at: string;
  expires_at?: string;
  is_active: boolean;
}

export interface AuthTokens {
  access: string;
  refresh: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface LoginResponse {
  user: User;
  message: string;
}
