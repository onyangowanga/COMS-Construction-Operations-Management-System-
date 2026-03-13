// ============================================================================
// USE VARIATIONS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { variationService } from '@/services';
import type { VariationFormInput, VariationOrder, VariationQueryParams } from '@/types';

export function useVariations(params?: VariationQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['variations', params],
    () => variationService.getVariations(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: VariationFormInput) => variationService.createVariation(payload), {
    showSuccessToast: true,
    successMessage: 'Variation Created',
    onSuccess: () => invalidateQueries(['variations']),
  });

  const submitMutation = useMutation((id: string) => variationService.submitVariation(id), {
    showSuccessToast: true,
    successMessage: 'Variation Submitted',
    onSuccess: (_data: VariationOrder, id: string) => {
      invalidateQueries(['variations']);
      invalidateQueries(['variation', id]);
    },
  });

  const approveMutation = useMutation(
    ({ id, approved_value, notes }: { id: string; approved_value: string; notes?: string }) =>
      variationService.approveVariation(id, { approved_value, notes }),
    {
      showSuccessToast: true,
      successMessage: 'Variation Approved',
      onSuccess: (_data: VariationOrder, vars: { id: string; approved_value: string; notes?: string }) => {
        invalidateQueries(['variations']);
        invalidateQueries(['variation', vars.id]);
      },
    }
  );

  const rejectMutation = useMutation(
    ({ id, reason }: { id: string; reason: string }) => variationService.rejectVariation(id, reason),
    {
      showSuccessToast: true,
      successMessage: 'Variation Rejected',
      onSuccess: (_data: VariationOrder, vars: { id: string; reason: string }) => {
        invalidateQueries(['variations']);
        invalidateQueries(['variation', vars.id]);
      },
    }
  );

  return {
    variations: (data?.results || []) as VariationOrder[],
    totalCount: data?.count || 0,
    nextPage: data?.next || null,
    previousPage: data?.previous || null,
    isLoading,
    error,
    refetchVariations: () => invalidateQueries(['variations']),
    createVariation: createMutation.mutateAsync,
    submitVariation: submitMutation.mutateAsync,
    approveVariation: approveMutation.mutateAsync,
    rejectVariation: rejectMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isSubmitting: submitMutation.isPending,
    isApproving: approveMutation.isPending,
    isRejecting: rejectMutation.isPending,
  };
}

export function useVariation(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['variation', id],
    () => variationService.getVariation(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    variation: data as VariationOrder | undefined,
    isLoading,
    error,
  };
}
