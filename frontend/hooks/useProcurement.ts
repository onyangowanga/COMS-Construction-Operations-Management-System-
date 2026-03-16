// ============================================================================
// USE PROCUREMENT HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { procurementService } from '@/services';
import type {
  PaginatedResponse,
  ProcurementOrder,
  ProcurementOrderFormInput,
  ProcurementQueryParams,
} from '@/types';

function normalizeList(data: PaginatedResponse<ProcurementOrder> | ProcurementOrder[] | undefined) {
  const orders = Array.isArray(data)
    ? data
    : Array.isArray((data as any)?.results)
      ? (data as any).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as any)?.count || 0;

  return {
    orders,
    totalCount,
    nextPage: (data as any)?.next || null,
    previousPage: (data as any)?.previous || null,
  };
}

export function useProcurement(params?: ProcurementQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['procurement-orders', params],
    () => procurementService.getOrders(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation((payload: ProcurementOrderFormInput) => procurementService.createOrder(payload), {
    showSuccessToast: true,
    successMessage: 'Procurement Order Created',
    onSuccess: () => invalidateQueries(['procurement-orders']),
  });

  const updateMutation = useMutation(
    ({ id, payload }: { id: string; payload: Partial<ProcurementOrderFormInput> }) =>
      procurementService.updateOrder(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Procurement Order Updated',
      onSuccess: (_order: ProcurementOrder, vars: { id: string; payload: Partial<ProcurementOrderFormInput> }) => {
        invalidateQueries(['procurement-orders']);
        invalidateQueries(['procurement-order', vars.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => procurementService.deleteOrder(id), {
    showSuccessToast: true,
    successMessage: 'Procurement Order Deleted',
    onSuccess: () => invalidateQueries(['procurement-orders']),
  });

  const submitMutation = useMutation((id: string) => procurementService.submitOrder(id), {
    showSuccessToast: true,
    successMessage: 'Order Submitted',
    onSuccess: (_order: ProcurementOrder, id: string) => {
      invalidateQueries(['procurement-orders']);
      invalidateQueries(['procurement-order', id]);
    },
  });

  const approveMutation = useMutation((id: string) => procurementService.approveOrder(id), {
    showSuccessToast: true,
    successMessage: 'Order Approved',
    onSuccess: (_order: ProcurementOrder, id: string) => {
      invalidateQueries(['procurement-orders']);
      invalidateQueries(['procurement-order', id]);
    },
  });

  const closeMutation = useMutation((id: string) => procurementService.closeOrder(id), {
    showSuccessToast: true,
    successMessage: 'Order Closed',
    onSuccess: (_order: ProcurementOrder, id: string) => {
      invalidateQueries(['procurement-orders']);
      invalidateQueries(['procurement-order', id]);
    },
  });

  const normalized = normalizeList(data);

  return {
    orders: normalized.orders as ProcurementOrder[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    isLoading,
    error,
    refetchOrders: () => invalidateQueries(['procurement-orders']),
    createOrder: createMutation.mutateAsync,
    updateOrder: updateMutation.mutateAsync,
    deleteOrder: deleteMutation.mutateAsync,
    submitOrder: submitMutation.mutateAsync,
    approveOrder: approveMutation.mutateAsync,
    closeOrder: closeMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
    isSubmitting: submitMutation.isPending,
    isApproving: approveMutation.isPending,
    isClosing: closeMutation.isPending,
  };
}

export function useProcurementOrder(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['procurement-order', id],
    () => procurementService.getOrder(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    order: data as ProcurementOrder | undefined,
    isLoading,
    error,
  };
}
