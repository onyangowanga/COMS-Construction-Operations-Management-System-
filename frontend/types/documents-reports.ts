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
  code: string;
  year: number;
  sequence: number;
  name: string;
  description: string;
  module: string;
  report_type: 'TABLE' | 'SUMMARY' | 'CHART' | 'PROJECT_FINANCIAL' | 'CASH_FLOW' | 'VARIATION_IMPACT' | 'SUBCONTRACTOR_PAYMENT' | 'DOCUMENT_AUDIT' | 'PROCUREMENT_SUMMARY' | 'CUSTOM';
  filters: Record<string, unknown>;
  columns: string[];
  aggregations: Record<string, unknown>;
  group_by: string[];
  default_parameters: Record<string, unknown>;
  is_active: boolean;
  is_public: boolean;
  cache_duration: number;
  created_by?: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
  updated_at: string;
  total_executions?: number;
  last_execution?: string | null;
}

export interface ReportExecution {
  id: string;
  report: Report;
  schedule?: string | null;
  status: 'PENDING' | 'RUNNING' | 'COMPLETED' | 'FAILED' | 'CACHED';
  export_format: 'PDF' | 'EXCEL' | 'CSV' | 'JSON';
  parameters: Record<string, unknown>;
  file_path?: string;
  file_size?: number | null;
  row_count?: number | null;
  execution_time?: number | null;
  error_message?: string;
  cache_key?: string;
  cache_expires_at?: string | null;
  progress?: number;
  queued_at?: string | null;
  started_at?: string | null;
  attempt_count?: number;
  max_attempts?: number;
  worker_id?: string;
  executed_by?: {
    id: string;
    username: string;
    first_name: string;
    last_name: string;
  };
  created_at: string;
  completed_at?: string;
  duration?: number;
  was_successful?: boolean;
}

export interface ReportExecutionProgress {
  id: string;
  status: ReportExecution['status'];
  progress: number;
  attempt_count: number;
  max_attempts: number;
  error_message: string;
}

export interface ReportCreatePayload {
  name: string;
  description?: string;
  module: string;
  report_type: Report['report_type'];
  filters?: Record<string, unknown>;
  columns?: string[];
  aggregations?: Record<string, unknown>;
  group_by?: string[];
  default_parameters?: Record<string, unknown>;
  is_public?: boolean;
  cache_duration?: number;
  code?: string;
}

export interface ReportSchedule {
  id: string;
  report: Report;
  name: string;
  frequency: 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'CUSTOM';
  cron_expression?: string;
  export_format: 'PDF' | 'EXCEL' | 'CSV' | 'JSON';
  parameters: Record<string, unknown>;
  delivery_method: 'EMAIL' | 'DASHBOARD' | 'STORAGE' | 'ALL';
  recipients: string[];
  is_active: boolean;
  last_run?: string | null;
  next_run?: string | null;
  created_at: string;
  updated_at: string;
}

export interface ReportScheduleCreatePayload {
  report_id: string;
  name: string;
  frequency: ReportSchedule['frequency'];
  cron_expression?: string;
  export_format: ReportSchedule['export_format'];
  parameters?: Record<string, unknown>;
  delivery_method: ReportSchedule['delivery_method'];
  recipients?: string[];
}

export interface ReportWidget {
  id: string;
  name: string;
  widget_type: 'KPI' | 'CHART' | 'TABLE' | 'GAUGE' | 'TREND';
  chart_type?: 'LINE' | 'BAR' | 'PIE' | 'DONUT' | 'AREA';
  data_source: string;
  query_parameters: Record<string, unknown>;
  display_order: number;
  refresh_interval: number;
  icon?: string;
  color?: string;
  is_active: boolean;
  report?: string | null;
}

export interface DashboardWidgetData {
  widget: ReportWidget;
  data: {
    value?: unknown;
    widget_type?: string;
    chart_type?: string;
    timestamp?: string;
    error?: string;
    source_report_id?: string;
    source_report_name?: string;
    drilldown?: {
      route: string;
      report_id?: string;
      filters?: Record<string, unknown>;
    };
    [key: string]: unknown;
  };
}
