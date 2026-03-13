// ============================================================================
// USE DOCUMENTS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { documentService } from '@/services';
import type {
  Document,
  DocumentApprovalPayload,
  DocumentQueryParams,
  DocumentRejectionPayload,
  DocumentUploadInput,
} from '@/types';

export function useDocuments(params?: DocumentQueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['documents', params],
    () => documentService.getDocuments(params),
    {
      staleTime: 2 * 60 * 1000,
    }
  );

  const createMutation = useMutation(
    ({ payload, onProgress }: { payload: DocumentUploadInput; onProgress?: (value: number) => void }) =>
      documentService.uploadDocument(payload, onProgress),
    {
      showSuccessToast: true,
      successMessage: 'Document Uploaded',
      onSuccess: () => {
        invalidateQueries(['documents']);
      },
    }
  );

  const approveMutation = useMutation(
    ({ id, payload }: { id: string; payload?: DocumentApprovalPayload }) =>
      documentService.approveDocument(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Document Approved',
      onSuccess: (_doc: Document, vars: { id: string; payload?: DocumentApprovalPayload }) => {
        invalidateQueries(['documents']);
        invalidateQueries(['document', vars.id]);
      },
    }
  );

  const rejectMutation = useMutation(
    ({ id, payload }: { id: string; payload: DocumentRejectionPayload }) =>
      documentService.rejectDocument(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Document Rejected',
      onSuccess: (_doc: Document, vars: { id: string; payload: DocumentRejectionPayload }) => {
        invalidateQueries(['documents']);
        invalidateQueries(['document', vars.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => documentService.deleteDocument(id), {
    showSuccessToast: true,
    successMessage: 'Document Deleted',
    onSuccess: () => {
      invalidateQueries(['documents']);
    },
  });

  return {
    documents: (data?.results || []) as Document[],
    totalCount: data?.count || 0,
    nextPage: data?.next || null,
    previousPage: data?.previous || null,
    isLoading,
    error,
    refetchDocuments: () => invalidateQueries(['documents']),
    uploadDocument: createMutation.mutateAsync,
    approveDocument: approveMutation.mutateAsync,
    rejectDocument: rejectMutation.mutateAsync,
    deleteDocument: deleteMutation.mutateAsync,
    isUploading: createMutation.isPending,
    isApproving: approveMutation.isPending,
    isRejecting: rejectMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useDocument(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['document', id],
    () => documentService.getDocument(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    document: data as Document | undefined,
    isLoading,
    error,
  };
}
