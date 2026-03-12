// ============================================================================
// USE API HOOK
// Custom hook for API calls with React Query
// ============================================================================

'use client';

import { useQuery, useMutation, useQueryClient, type UseQueryOptions, type UseMutationOptions } from '@tanstack/react-query';
import { useToast } from './useToast';

interface UseApiOptions<TData, TError, TVariables> {
  onSuccess?: (data: TData, variables: TVariables, context: any) => void;
  onError?: (error: TError, variables: TVariables, context: any) => void;
  showSuccessToast?: boolean;
  showErrorToast?: boolean;
  successMessage?: string;
  errorMessage?: string;
}

export function useApi() {
  const queryClient = useQueryClient();
  const { success, error: showError } = useToast();

  // Wrapper for useQuery with error handling
  function useApiQuery<TData = unknown, TError = Error>(
    queryKey: any[],
    queryFn: () => Promise<TData>,
    options?: Omit<UseQueryOptions<TData, TError>, 'queryKey' | 'queryFn'> & {
      showErrorToast?: boolean;
      errorMessage?: string;
    }
  ) {
    return useQuery<TData, TError>({
      queryKey,
      queryFn,
      ...options,
      meta: {
        ...options?.meta,
        onError: (error: any) => {
          if (options?.showErrorToast !== false) {
            showError(
              options?.errorMessage || 'Request Failed',
              error?.message || 'An error occurred'
            );
          }
        },
      },
    });
  }

  // Wrapper for useMutation with success/error handling
  function useApiMutation<TData = unknown, TError = Error, TVariables = void>(
    mutationFn: (variables: TVariables) => Promise<TData>,
    options?: UseMutationOptions<TData, TError, TVariables> & UseApiOptions<TData, TError, TVariables>
  ) {
    return useMutation<TData, TError, TVariables>({
      mutationFn,
      onSuccess: (data: TData, variables: TVariables, context: any) => {
        if (options?.showSuccessToast) {
          success(options.successMessage || 'Success', 'Operation completed successfully');
        }
        options?.onSuccess?.(data, variables, context);
      },
      onError: (error: any, variables: TVariables, context: any) => {
        if (options?.showErrorToast !== false) {
          showError(
            options?.errorMessage || 'Error',
            error?.message || 'An error occurred'
          );
        }
        options?.onError?.(error, variables, context);
      },
      ...options,
    });
  }

  // Invalidate queries helper
  const invalidateQueries = (queryKey: any[]) => {
    queryClient.invalidateQueries({ queryKey });
  };

  return {
    useQuery: useApiQuery,
    useMutation: useApiMutation,
    invalidateQueries,
    queryClient,
  };
}
