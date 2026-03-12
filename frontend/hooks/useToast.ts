// ============================================================================
// USE TOAST HOOK
// Custom hook for showing toast notifications
// ============================================================================

'use client';

import { useCallback } from 'react';
import { useUIStore } from '@/store';

export function useToast() {
  const { addToast, removeToast, toasts } = useUIStore();

  const toast = useCallback(
    ({
      title,
      message,
      type = 'info',
      duration = 5000,
    }: {
      title: string;
      message?: string;
      type?: 'success' | 'error' | 'warning' | 'info';
      duration?: number;
    }) => {
      addToast({ title, message, type, duration });
    },
    [addToast]
  );

  const success = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast({ title, message, type: 'success', duration });
    },
    [toast]
  );

  const error = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast({ title, message, type: 'error', duration });
    },
    [toast]
  );

  const warning = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast({ title, message, type: 'warning', duration });
    },
    [toast]
  );

  const info = useCallback(
    (title: string, message?: string, duration?: number) => {
      toast({ title, message, type: 'info', duration });
    },
    [toast]
  );

  return {
    toast,
    success,
    error,
    warning,
    info,
    remove: removeToast,
    toasts,
  };
}
