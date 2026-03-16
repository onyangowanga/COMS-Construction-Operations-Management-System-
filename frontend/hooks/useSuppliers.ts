// ============================================================================
// USE SUPPLIERS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { supplierService } from '@/services';
import type {
  PaginatedResponse,
  Supplier,
  SupplierCreatePayload,
  SupplierQueryParams,
  SupplierUpdatePayload,
} from '@/types';

function normalizeList(data: PaginatedResponse<Supplier> | Supplier[] | undefined) {
  const suppliers = Array.isArray(data)
    ? data
    : Array.isArray((data as any)?.results)
      ? (data as any).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as any)?.count || 0;

  return {
    suppliers,
    totalCount,
    nextPage: (data as any)?.next || null,
    previousPage: (data as any)?.previous || null,
  };
}

export function useSuppliers(params?: SupplierQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['suppliers', params],
    () => supplierService.getSuppliers(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: SupplierCreatePayload) => supplierService.createSupplier(payload), {
    showSuccessToast: true,
    successMessage: 'Supplier Created',
    onSuccess: () => invalidateQueries(['suppliers']),
  });

  const updateMutation = useMutation(
    ({ id, payload }: { id: string; payload: SupplierUpdatePayload }) => supplierService.updateSupplier(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Supplier Updated',
      onSuccess: (_supplier: Supplier, vars: { id: string; payload: SupplierUpdatePayload }) => {
        invalidateQueries(['suppliers']);
        invalidateQueries(['supplier', vars.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => supplierService.deleteSupplier(id), {
    showSuccessToast: true,
    successMessage: 'Supplier Deleted',
    onSuccess: () => invalidateQueries(['suppliers']),
  });

  const normalized = normalizeList(data);

  return {
    suppliers: normalized.suppliers as Supplier[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    isLoading,
    error,
    refetchSuppliers: () => invalidateQueries(['suppliers']),
    createSupplier: createMutation.mutateAsync,
    updateSupplier: updateMutation.mutateAsync,
    deleteSupplier: deleteMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useSupplier(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['supplier', id],
    () => supplierService.getSupplier(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    supplier: data as Supplier | undefined,
    isLoading,
    error,
  };
}
