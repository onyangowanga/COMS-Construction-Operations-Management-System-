'use client';

import { useApi } from './useApi';
import { workflowService } from '@/services/workflowService';
import type { WorkflowModule, WorkflowStateSnapshot } from '@/types/workflow';

export function useWorkflow(module: WorkflowModule | string, entityId?: string) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const queryKey = ['workflow', module, entityId];

  const { data, isLoading, error } = useQuery(
    queryKey,
    () => workflowService.getWorkflowState(module, entityId as string),
    {
      enabled: Boolean(module && entityId),
      staleTime: 30 * 1000,
    }
  );

  const transitionMutation = useMutation(
    ({ action, comment, payload }: { action: string; comment?: string; payload?: Record<string, unknown> }) =>
      workflowService.performTransition(module, entityId as string, { action, comment, payload }),
    {
      showSuccessToast: true,
      successMessage: 'Workflow Updated',
      onSuccess: () => {
        invalidateQueries(queryKey);
      },
    }
  );

  return {
    workflow: data as WorkflowStateSnapshot | undefined,
    availableActions: (data as WorkflowStateSnapshot | undefined)?.available_actions || [],
    history: (data as WorkflowStateSnapshot | undefined)?.history || [],
    currentState: (data as WorkflowStateSnapshot | undefined)?.current_state,
    isLoading,
    error,
    transition: transitionMutation.mutateAsync,
    isTransitioning: transitionMutation.isPending,
    refetchWorkflow: () => invalidateQueries(queryKey),
  };
}
