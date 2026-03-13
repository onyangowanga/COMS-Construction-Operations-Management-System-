// ============================================================================
// DOCUMENT TYPES
// ============================================================================

export enum DocumentApprovalStatus {
  PENDING = 'PENDING',
  APPROVED = 'APPROVED',
  REJECTED = 'REJECTED',
}

export interface DocumentUploadInput {
  file: File;
  title: string;
  document_type: string;
  project?: string;
  description?: string;
}

export interface DocumentQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  document_type?: string;
  project?: string;
  status?: string;
}

export interface Document {
  id: string;
  title: string;
  name?: string;
  description: string;
  document_type?: string;
  document_type_display?: string;
  file: string;
  file_name?: string;
  file_url?: string;
  file_size: number;
  file_size_display?: string;
  file_type: string;
  file_extension?: string;
  category?: string;
  uploaded_by: string;
  uploaded_by_name: string;
  uploaded_by_data?: {
    id: string;
    username: string;
    full_name?: string;
    email?: string;
  };
  uploaded_at: string;
  project?: string;
  project_name?: string;
  version: number;
  is_latest?: boolean;
  status?: DocumentApprovalStatus | string;
  is_approved: boolean;
  rejection_reason?: string;
  approved_by?: string;
  approved_by_name?: string;
  approved_at?: string;
  visibility?: string;
  tags?: string[] | string;
  reference_number?: string;
  is_confidential?: boolean;
  updated_at?: string;
}

export interface DocumentApprovalPayload {
  notes?: string;
}

export interface DocumentRejectionPayload {
  reason: string;
}

// ============================================================================
// PROCUREMENT TYPES
// ============================================================================

export interface PurchaseOrder {
  id: string;
  po_number: string;
  project: string;
  project_name: string;
  supplier: string;
  supplier_name: string;
  description: string;
  status: 'draft' | 'submitted' | 'approved' | 'received' | 'cancelled';
  order_date: string;
  delivery_date?: string;
  total_amount: string;
  created_by: string;
  created_by_name: string;
  approved_by?: string;
  approved_by_name?: string;
  created_at: string;
  updated_at: string;
}

// ============================================================================
// REPORT TYPES
// ============================================================================

export interface Report {
  id: string;
  name: string;
  description: string;
  report_type: string;
  category: string;
  created_by: string;
  created_by_name: string;
  created_at: string;
  last_executed?: string;
  is_scheduled: boolean;
}

export interface ReportExecution {
  id: string;
  report: string;
  report_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  executed_by: string;
  executed_by_name: string;
  executed_at: string;
  completed_at?: string;
  output_file?: string;
  error_message?: string;
}
