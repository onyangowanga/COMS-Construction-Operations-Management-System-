// ============================================================================
// USE SUBCONTRACTORS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { subcontractorService } from '@/services';
import type {
  PaginatedResponse,
  Subcontractor,
  SubcontractorFormInput,
  SubcontractorQueryParams,
} from '@/types';

function normalizeList(data: PaginatedResponse<Subcontractor> | Subcontractor[] | undefined) {
  const subcontractors = Array.isArray(data)
    ? data
    : Array.isArray((data as any)?.results)
      ? (data as any).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as any)?.count || 0;

  return {
    subcontractors,
    totalCount,
    nextPage: (data as any)?.next || null,
    previousPage: (data as any)?.previous || null,
  };
}

export function useSubcontractors(params?: SubcontractorQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['subcontractors', params],
    () => subcontractorService.getSubcontractors(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: SubcontractorFormInput) => subcontractorService.createSubcontractor(payload), {
    showSuccessToast: true,
    successMessage: 'Subcontractor Created',
    onSuccess: () => invalidateQueries(['subcontractors']),
  });

  const updateMutation = useMutation(
    ({ id, payload }: { id: string; payload: Partial<SubcontractorFormInput> }) =>
      subcontractorService.updateSubcontractor(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Subcontractor Updated',
      onSuccess: (_subcontractor: Subcontractor, vars: { id: string; payload: Partial<SubcontractorFormInput> }) => {
        invalidateQueries(['subcontractors']);
        invalidateQueries(['subcontractor', vars.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => subcontractorService.deleteSubcontractor(id), {
    showSuccessToast: true,
    successMessage: 'Subcontractor Deleted',
    onSuccess: () => invalidateQueries(['subcontractors']),
  });

  const normalized = normalizeList(data);

  return {
    subcontractors: normalized.subcontractors as Subcontractor[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    isLoading,
    error,
    refetchSubcontractors: () => invalidateQueries(['subcontractors']),
    createSubcontractor: createMutation.mutateAsync,
    updateSubcontractor: updateMutation.mutateAsync,
    deleteSubcontractor: deleteMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useSubcontractor(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['subcontractor', id],
    () => subcontractorService.getSubcontractor(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    subcontractor: data as Subcontractor | undefined,
    isLoading,
    error,
  };
}
