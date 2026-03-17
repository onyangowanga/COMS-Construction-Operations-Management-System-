// ============================================================================
// USE CONTRACTS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { contractService } from '@/services';
import type {
  Contract,
  ContractCreatePayload,
  ContractQueryParams,
  ContractUpdatePayload,
  PaginatedResponse,
} from '@/types';

function normalizeList(data: PaginatedResponse<Contract> | Contract[] | undefined) {
  const contracts = Array.isArray(data)
    ? data
    : Array.isArray((data as PaginatedResponse<Contract> | undefined)?.results)
      ? (data as PaginatedResponse<Contract>).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as PaginatedResponse<Contract> | undefined)?.count || 0;

  return {
    contracts,
    totalCount,
    nextPage: Array.isArray(data) ? null : (data as PaginatedResponse<Contract> | undefined)?.next || null,
    previousPage: Array.isArray(data) ? null : (data as PaginatedResponse<Contract> | undefined)?.previous || null,
  };
}

export function useContracts(params?: ContractQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['contracts', params],
    () => contractService.getContracts(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: ContractCreatePayload) => contractService.createContract(payload), {
    showSuccessToast: true,
    successMessage: 'Contract Created',
    onSuccess: () => invalidateQueries(['contracts']),
  });

  const updateMutation = useMutation(
    ({ id, payload }: { id: string; payload: ContractUpdatePayload }) => contractService.updateContract(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Contract Updated',
      onSuccess: (_contract: Contract, vars: { id: string; payload: ContractUpdatePayload }) => {
        invalidateQueries(['contracts']);
        invalidateQueries(['contract', vars.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => contractService.deleteContract(id), {
    showSuccessToast: true,
    successMessage: 'Contract Deleted',
    onSuccess: () => invalidateQueries(['contracts']),
  });

  const normalized = normalizeList(data);

  return {
    contracts: normalized.contracts as Contract[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    isLoading,
    error,
    refetchContracts: () => invalidateQueries(['contracts']),
    createContract: createMutation.mutateAsync,
    updateContract: updateMutation.mutateAsync,
    deleteContract: deleteMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useContract(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['contract', id],
    () => contractService.getContract(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    contract: data as Contract | undefined,
    isLoading,
    error,
  };
}
