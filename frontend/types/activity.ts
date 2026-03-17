// ============================================================================
// ACTIVITY TYPES
// ============================================================================

export enum ActivityEventType {
  CREATE = 'CREATE',
  UPDATE = 'UPDATE',
  DELETE = 'DELETE',
  APPROVE = 'APPROVE',
  REJECT = 'REJECT',
  SUBMIT = 'SUBMIT',
  CERTIFY = 'CERTIFY',
}

export enum ActivityModuleType {
  CONTRACT = 'CONTRACT',
  PROJECT = 'PROJECT',
  DOCUMENT = 'DOCUMENT',
  VARIATION = 'VARIATION',
  CLAIM = 'CLAIM',
  PROCUREMENT = 'PROCUREMENT',
  SUPPLIER = 'SUPPLIER',
  SUBCONTRACTOR = 'SUBCONTRACTOR',
}

export interface ActivityQueryParams {
  module?: string;
  event_type?: string;
  user?: string;
  start_date?: string;
  end_date?: string;
  page?: number;
  page_size?: number;
  ordering?: string;
}

export interface Activity {
  id: string;
  event_type: ActivityEventType | string;
  module: ActivityModuleType | string;
  entity_id: string;
  entity_reference: string;
  description: string;
  metadata?: Record<string, unknown>;
  performed_by?: string;
  timestamp: string;
}
