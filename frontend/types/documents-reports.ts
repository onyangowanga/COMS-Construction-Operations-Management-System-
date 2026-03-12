// ============================================================================
// DOCUMENT TYPES
// ============================================================================

export interface Document {
  id: string;
  title: string;  name: string;
  description: string;
  file: string;
  file_size: number;
  file_type: string;
  category: string;
  uploaded_by: string;
  uploaded_by_name: string;
  uploaded_at: string;
  project?: string;
  project_name?: string;
  version: number;
  is_approved: boolean;
  approved_by?: string;
  approved_by_name?: string;
  approved_at?: string;
  tags?: string[];
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
