// ============================================================================
// USE NOTIFICATIONS HOOK
// React Query-based hook for notification management
// ============================================================================

'use client';

import { useApi } from './useApi';
import { notificationService } from '@/services';
import { useNotificationStore } from '@/store';
import type { Notification, NotificationQueryParams, PaginatedResponse } from '@/types';

interface UseNotificationsOptions {
  enabled?: boolean;
}

function normalizeList(data: PaginatedResponse<Notification> | Notification[] | undefined) {
  const notifications = Array.isArray(data)
    ? data
    : Array.isArray((data as PaginatedResponse<Notification> | undefined)?.results)
    ? (data as PaginatedResponse<Notification>).results
    : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as PaginatedResponse<Notification> | undefined)?.count || 0;

  return {
    notifications,
    totalCount,
    nextPage: Array.isArray(data) ? null : (data as PaginatedResponse<Notification> | undefined)?.next || null,
    previousPage: Array.isArray(data) ? null : (data as PaginatedResponse<Notification> | undefined)?.previous || null,
  };
}

export function useNotifications(params?: NotificationQueryParams, options?: UseNotificationsOptions) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  // Zustand store exposes unreadCount synced by the notificationStore pollers
  const { unreadCount } = useNotificationStore();

  const { data, isLoading, isFetching, error } = useQuery(
    ['notifications', params],
    () => notificationService.getNotifications(params),
    {
      staleTime: 30 * 1000,
      enabled: options?.enabled ?? true,
    }
  );

  const normalized = normalizeList(data as PaginatedResponse<Notification> | Notification[] | undefined);

  // Unread count query (lightweight poll)
  const { data: unreadData } = useQuery(
    ['notifications-unread-count'],
    () => notificationService.getUnreadCount(),
    {
      staleTime: 30 * 1000,
      refetchInterval: 60 * 1000,
      enabled: options?.enabled ?? true,
    }
  );

  const resolvedUnreadCount = typeof unreadData === 'number' ? unreadData : unreadCount;

  const markAsReadMutation = useMutation(
    (id: string) => notificationService.markAsRead(id),
    {
      onSuccess: () => {
        invalidateQueries(['notifications']);
        invalidateQueries(['notifications-unread-count']);
      },
    }
  );

  const markAllAsReadMutation = useMutation(
    () => notificationService.markAllAsRead(),
    {
      onSuccess: () => {
        invalidateQueries(['notifications']);
        invalidateQueries(['notifications-unread-count']);
      },
    }
  );

  return {
    notifications: normalized.notifications as Notification[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    unreadCount: resolvedUnreadCount,
    isLoading,
    isFetching,
    error,

    markAsRead: markAsReadMutation.mutate,
    markAllAsRead: markAllAsReadMutation.mutate,
    isMarkingRead: markAsReadMutation.isPending,
    isMarkingAllRead: markAllAsReadMutation.isPending,

    refetchNotifications: () => invalidateQueries(['notifications']),
  };
}

