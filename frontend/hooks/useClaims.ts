// ============================================================================
// USE CLAIMS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { claimService } from '@/services';
import type { Claim, ClaimFormInput, ClaimQueryParams } from '@/types';

export function useClaims(params?: ClaimQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['claims', params],
    () => claimService.getClaims(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: ClaimFormInput) => claimService.createClaim(payload), {
    showSuccessToast: true,
    successMessage: 'Claim Created',
    onSuccess: () => invalidateQueries(['claims']),
  });

  const submitMutation = useMutation((id: string) => claimService.submitClaim(id), {
    showSuccessToast: true,
    successMessage: 'Claim Submitted',
    onSuccess: (_data: Claim, id: string) => {
      invalidateQueries(['claims']);
      invalidateQueries(['claim', id]);
    },
  });

  const certifyMutation = useMutation(
    ({ id, certified_amount, notes }: { id: string; certified_amount: string; notes?: string }) =>
      claimService.certifyClaim(id, { certified_amount, notes }),
    {
      showSuccessToast: true,
      successMessage: 'Claim Certified',
      onSuccess: (_data: Claim, vars: { id: string; certified_amount: string; notes?: string }) => {
        invalidateQueries(['claims']);
        invalidateQueries(['claim', vars.id]);
      },
    }
  );

  const rejectMutation = useMutation(
    ({ id, reason }: { id: string; reason: string }) => claimService.rejectClaim(id, reason),
    {
      showSuccessToast: true,
      successMessage: 'Claim Rejected',
      onSuccess: (_data: Claim, vars: { id: string; reason: string }) => {
        invalidateQueries(['claims']);
        invalidateQueries(['claim', vars.id]);
      },
    }
  );

  return {
    claims: (data?.results || []) as Claim[],
    totalCount: data?.count || 0,
    nextPage: data?.next || null,
    previousPage: data?.previous || null,
    isLoading,
    error,
    refetchClaims: () => invalidateQueries(['claims']),
    createClaim: createMutation.mutateAsync,
    submitClaim: submitMutation.mutateAsync,
    certifyClaim: certifyMutation.mutateAsync,
    rejectClaim: rejectMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isSubmitting: submitMutation.isPending,
    isCertifying: certifyMutation.isPending,
    isRejecting: rejectMutation.isPending,
  };
}

export function useClaim(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['claim', id],
    () => claimService.getClaim(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    claim: data as Claim | undefined,
    isLoading,
    error,
  };
}
