// ============================================================================
// USE NOTIFICATIONS HOOK
// Custom hook for notification management
// ============================================================================

'use client';

import { useEffect } from 'react';
import { useNotificationStore } from '@/store';
import { useApi } from './useApi';
import { notificationService } from '@/services';

export function useNotifications() {
  const {
    notifications,
    unreadCount,
    isLoading,
    error,
    fetchNotifications,
    fetchUnreadCount,
    markAsRead,
    markAllAsRead,
    deleteNotification,
  } = useNotificationStore();

  const { useMutation, invalidateQueries } = useApi();

  // Fetch unread count on mount
  useEffect(() => {
    fetchUnreadCount();
    
    // Refresh unread count every minute
    const interval = setInterval(() => {
      fetchUnreadCount();
    }, 60000);

    return () => clearInterval(interval);
  }, []);

  // Mark as read mutation
  const markAsReadMutation = useMutation(
    (id: string) => notificationService.markAsRead(id),
    {
      onSuccess: (_, id) => {
        markAsRead(id);
        fetchUnreadCount();
      },
    }
  );

  // Mark all as read mutation
  const markAllAsReadMutation = useMutation(
    () => notificationService.markAllAsRead(),
    {
      showSuccessToast: true,
      successMessage: 'All notifications marked as read',
      onSuccess: () => {
        markAllAsRead();
        fetchUnreadCount();
      },
    }
  );

  // Delete notification mutation
  const deleteMutation = useMutation(
    (id: string) => notificationService.deleteNotification(id),
    {
      showSuccessToast: true,
      successMessage: 'Notification deleted',
      onSuccess: (_, id) => {
        deleteNotification(id);
        fetchUnreadCount();
      },
    }
  );

  return {
    notifications,
    unreadCount,
    isLoading,
    error,
    
    // Actions
    fetchNotifications,
    markAsRead: markAsReadMutation.mutate,
    markAllAsRead: markAllAsReadMutation.mutate,
    deleteNotification: deleteMutation.mutate,
    
    // Mutation states
    isMarkingRead: markAsReadMutation.isPending,
    isMarkingAllRead: markAllAsReadMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}
