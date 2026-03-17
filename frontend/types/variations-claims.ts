// ============================================================================
// VARIATION ORDER TYPES
// ============================================================================

export interface VariationQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
  project?: string;
}

export interface VariationFormInput {
  project_id: string;
  reference_number?: string;
  title: string;
  description: string;
  estimated_value: string;
  priority?: string;
  change_type?: string;
  impact_on_schedule?: string;
  technical_notes?: string;
  justification?: string;
  client_reference?: string;
  instruction_date?: string;
  required_by_date?: string;
}

export interface VariationTimelineItem {
  label: string;
  date?: string;
  completed: boolean;
}

export interface VariationOrder {
  id: string;
  project: string | {
    id: string;
    name: string;
    project_code?: string;
  };
  project_name?: string;
  reference_number?: string;
  variation_number?: string;
  title: string;
  description: string;
  status: VariationStatus;
  status_display?: string;
  priority: string;
  priority_display?: string;
  estimated_value: string | number;
  approved_value?: string;
  certified_amount?: string;
  paid_value?: string;
  invoiced_value?: string;
  requested_by: string;
  requested_by_name?: string;
  requested_date?: string;
  created_by?: {
    id: string;
    username: string;
    full_name?: string;
  };
  reviewed_by?: string;
  reviewed_by_name?: string;
  reviewed_date?: string;
  approved_by?: string;
  approved_by_name?: string;
  approved_date?: string;
  rejection_reason?: string;
  change_type?: string;
  change_type_display?: string;
  impact_on_schedule?: string;
  technical_notes?: string;
  justification?: string;
  client_reference?: string;
  can_submit?: boolean;
  can_approve?: boolean;
  can_reject?: boolean;
  created_at: string;
  updated_at: string;
}

export enum VariationStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
  INVOICED = 'INVOICED',
  PAID = 'PAID',
}

// ============================================================================
// CLAIM/VALUATION TYPES
// ============================================================================

export interface ClaimQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
  project?: string;
}

export interface ClaimFormInput {
  claim_number: string;
  project: string;
  claim_amount: string;
  description: string;
  supporting_documents?: string[];
}

export interface ClaimTimelineItem {
  label: string;
  date?: string;
  completed: boolean;
}

export interface Claim {
  id: string;
  project: string;
  project_name?: string;
  claim_number: string;
  title?: string;
  claim_period_start?: string;
  claim_period_end?: string;
  status: ClaimStatus;
  status_display?: string;
  claim_amount?: string;
  gross_amount?: string;
  retention?: string;
  net_amount?: string;
  submitted_by?: string;
  submitted_by_name?: string;
  submitted_date?: string;
  certified_by?: string;
  certified_by_name?: string;
  certified_date?: string;
  certified_amount?: string;
  payment_date?: string;
  description?: string;
  amount_due?: string;
  valuation_date?: string;
  notes?: string;
  created_at: string;
  updated_at: string;
}

export enum ClaimStatus {
  DRAFT = 'DRAFT',
  SUBMITTED = 'SUBMITTED',
  CERTIFIED = 'CERTIFIED',
  REJECTED = 'REJECTED',
  PAID = 'PAID',
}
