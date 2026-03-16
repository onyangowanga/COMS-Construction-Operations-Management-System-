// ============================================================================
// PROCUREMENT TYPES
// ============================================================================

export enum ProcurementOrderStatus {
  DRAFT = 'DRAFT',
  APPROVED = 'APPROVED',
  ISSUED = 'ISSUED',
  PARTIALLY_DELIVERED = 'PARTIALLY_DELIVERED',
  DELIVERED = 'DELIVERED',
  INVOICED = 'INVOICED',
  PAID = 'PAID',
  CANCELLED = 'CANCELLED',
}

export interface ProcurementQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
  project?: string;
  supplier?: string;
}

export interface ProcurementOrderFormInput {
  reference_number: string;
  project: string;
  supplier: string;
  order_value: string;
  description?: string;
  issue_date?: string;
  delivery_date?: string;
  status?: ProcurementOrderStatus | string;
  notes?: string;
}

export interface ProcurementOrder {
  id: string;
  reference_number: string;
  project: string;
  project_name?: string;
  supplier: string;
  supplier_name?: string;
  order_value: string | number;
  description: string;
  delivery_date?: string;
  status: ProcurementOrderStatus | string;
  status_display?: string;
  notes?: string;
  created_by?: string;
  created_by_name?: string;
  submitted_at?: string;
  approved_at?: string;
  closed_at?: string;
  created_at: string;
  updated_at: string;
}

export interface ProcurementTimelineItem {
  label: string;
  date?: string;
  completed: boolean;
}

// ============================================================================
// SUBCONTRACTOR TYPES
// ============================================================================

export enum SubcontractorStatus {
  ACTIVE = 'ACTIVE',
  INACTIVE = 'INACTIVE',
  SUSPENDED = 'SUSPENDED',
}

export interface SubcontractorQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
  specialization?: string;
}

export interface SubcontractorProjectAssignment {
  id: string;
  name: string;
  project_code?: string;
  status?: string;
  contract_value?: string | number;
}

export interface SubcontractorFormInput {
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  specialization: string;
  address?: string;
  registration_number?: string;
  notes?: string;
}

export interface Subcontractor {
  id: string;
  subcontractor_name?: string;
  company_name: string;
  contact_person: string;
  email: string;
  phone: string;
  specialization: string;
  address?: string;
  registration_number?: string;
  notes?: string;
  status: SubcontractorStatus | string;
  assigned_projects?: SubcontractorProjectAssignment[];
  assigned_projects_count?: number;
  total_contract_value?: string | number;
  total_paid?: string | number;
  outstanding_balance?: string | number;
  created_at: string;
  updated_at: string;
}
