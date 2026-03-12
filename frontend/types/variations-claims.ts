// ============================================================================
// VARIATION ORDER TYPES
// ============================================================================

export interface VariationOrder {
  id: string;
  project: string;
  project_name: string;
  variation_number: string;
  title: string;
  description: string;
  status: VariationStatus;
  priority: 'low' | 'medium' | 'high' | 'critical';
  estimated_value: string;
  approved_value?: string;
  requested_by: string;
  requested_by_name: string;
  requested_date: string;
  reviewed_by?: string;
  reviewed_by_name?: string;
  reviewed_date?: string;
  approved_by?: string;
  approved_by_name?: string;
  approved_date?: string;
  rejection_reason?: string;
  created_at: string;
  updated_at: string;
}

export enum VariationStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  APPROVED = 'approved',
  REJECTED = 'rejected',
  IMPLEMENTED = 'implemented',
}

// ============================================================================
// CLAIM/VALUATION TYPES
// ============================================================================

export interface Claim {
  id: string;
  project: string;
  project_name: string;
  claim_number: string;
  title: string;
  claim_period_start: string;
  claim_period_end: string;
  status: ClaimStatus;
  gross_amount: string;
  retention: string;
  net_amount: string;
  submitted_by: string;
  submitted_by_name: string;
  submitted_date: string;
  certified_by?: string;
  certified_by_name?: string;
  certified_date?: string;
  certified_amount?: string;
  created_at: string;
  updated_at: string;
}

export enum ClaimStatus {
  DRAFT = 'draft',
  SUBMITTED = 'submitted',
  UNDER_REVIEW = 'under_review',
  CERTIFIED = 'certified',
  APPROVED = 'approved',
  PAID = 'paid',
  REJECTED = 'rejected',
}
