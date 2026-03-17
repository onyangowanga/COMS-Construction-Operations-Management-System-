export type WorkflowModule = 'VARIATION' | 'PROCUREMENT' | 'CLAIM' | 'CONTRACT';

export interface WorkflowAvailableAction {
  action: string;
  to_state: string;
  allowed_roles: string[];
}

export interface WorkflowHistoryItem {
  id: string;
  from_state: string | null;
  to_state: string | null;
  action: string;
  performed_by: string | null;
  performed_by_id: string | null;
  timestamp: string;
  comment: string;
}

export interface WorkflowStateSnapshot {
  instance_id: string;
  module: WorkflowModule | string;
  entity_id: string;
  current_state: string;
  available_actions: WorkflowAvailableAction[];
  history: WorkflowHistoryItem[];
  last_transition_by: string | null;
  last_transition_at: string | null;
}

export interface WorkflowTransitionPayload {
  action: string;
  comment?: string;
  payload?: Record<string, unknown>;
}
