import { api } from './apiClient';
import type { WorkflowStateSnapshot, WorkflowTransitionPayload } from '@/types/workflow';

export const workflowService = {
  async getWorkflowState(module: string, entityId: string): Promise<WorkflowStateSnapshot> {
    return api.get<WorkflowStateSnapshot>(`/workflows/${module}/${entityId}/`);
  },

  async performTransition(module: string, entityId: string, body: WorkflowTransitionPayload): Promise<WorkflowStateSnapshot> {
    return api.post<WorkflowStateSnapshot>(`/workflows/${module}/${entityId}/transition/`, body);
  },
};
