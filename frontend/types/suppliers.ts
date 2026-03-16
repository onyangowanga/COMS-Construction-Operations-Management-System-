// ============================================================================
// SUPPLIER TYPES
// ============================================================================

export enum SupplierStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
}

export interface SupplierQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
}

export interface SupplierCreatePayload {
  company_name: string;
  contact_person?: string;
  email: string;
  phone: string;
  address?: string;
  registration_number?: string;
  tax_number?: string;
  notes?: string;
  status?: SupplierStatus | string;
}

export interface SupplierUpdatePayload extends Partial<SupplierCreatePayload> {}

export interface Supplier {
  id: string;
  company_name: string;
  contact_person?: string;
  email: string;
  phone: string;
  address?: string;
  registration_number?: string;
  tax_number?: string;
  notes?: string;
  status: SupplierStatus | string;
  created_at: string;
  updated_at: string;

  // Backend compatibility fields
  name?: string;
  tax_pin?: string;
  is_active?: boolean;
}
