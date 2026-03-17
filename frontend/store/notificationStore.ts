// ============================================================================
// NOTIFICATION STORE
// Global notification state management
// ============================================================================

import { create } from 'zustand';
import type { Notification } from '@/types';
import { notificationService } from '@/services';

interface NotificationState {
  notifications: Notification[];
  unreadCount: number;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setNotifications: (notifications: Notification[]) => void;
  addNotification: (notification: Notification) => void;
  updateNotification: (id: string, data: Partial<Notification>) => void;
  removeNotification: (id: string) => void;
  setUnreadCount: (count: number) => void;
  
  // API actions
  fetchNotifications: (params?: any) => Promise<void>;
  fetchUnreadCount: () => Promise<void>;
  markAsRead: (id: string) => Promise<void>;
  markAllAsRead: () => Promise<void>;
  deleteNotification: (id: string) => Promise<void>;
  
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useNotificationStore = create<NotificationState>((set, get) => ({
  notifications: [],
  unreadCount: 0,
  isLoading: false,
  error: null,

  setNotifications: (notifications) => {
    set({ notifications, error: null });
  },

  addNotification: (notification) => {
    set((state) => ({
      notifications: [notification, ...state.notifications],
      unreadCount: notification.is_read ? state.unreadCount : state.unreadCount + 1,
    }));
  },

  updateNotification: (id, data) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === id);
      const wasUnread = notification && !notification.is_read;
      const nowRead = data.is_read === true;
      
      return {
        notifications: state.notifications.map((n) =>
          n.id === id ? { ...n, ...data } : n
        ),
        unreadCount: wasUnread && nowRead
          ? Math.max(0, state.unreadCount - 1)
          : state.unreadCount,
      };
    });
  },

  removeNotification: (id) => {
    set((state) => {
      const notification = state.notifications.find((n) => n.id === id);
      const wasUnread = notification && !notification.is_read;
      
      return {
        notifications: state.notifications.filter((n) => n.id !== id),
        unreadCount: wasUnread
          ? Math.max(0, state.unreadCount - 1)
          : state.unreadCount,
      };
    });
  },

  setUnreadCount: (count) => {
    set({ unreadCount: count });
  },

  fetchNotifications: async (params) => {
    try {
      set({ isLoading: true, error: null });
      const response = await notificationService.getNotifications(params);
      const notifications = Array.isArray(response) ? response : response.results || [];
      set({ notifications, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch notifications',
        isLoading: false,
      });
    }
  },

  fetchUnreadCount: async () => {
    try {
      const count = await notificationService.getUnreadCount();
      set({ unreadCount: count });
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
    }
  },

  markAsRead: async (id) => {
    try {
      const notification = await notificationService.markAsRead(id);
      get().updateNotification(id, notification);
    } catch (error: any) {
      set({ error: error.message || 'Failed to mark as read' });
    }
  },

  markAllAsRead: async () => {
    try {
      await notificationService.markAllAsRead();
      set((state) => ({
        notifications: state.notifications.map((n) => ({ ...n, is_read: true })),
        unreadCount: 0,
      }));
    } catch (error: any) {
      set({ error: error.message || 'Failed to mark all as read' });
    }
  },

  deleteNotification: async (id) => {
    try {
      await notificationService.deleteNotification(id);
      get().removeNotification(id);
    } catch (error: any) {
      set({ error: error.message || 'Failed to delete notification' });
      throw error;
    }
  },

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),
}));
