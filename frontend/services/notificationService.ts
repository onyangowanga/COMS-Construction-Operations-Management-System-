// ============================================================================
// NOTIFICATION SERVICE
// Handles notifications and real-time updates
// ============================================================================

import { api } from './apiClient';
import type { Notification, PaginatedResponse, QueryParams } from '@/types';

export const notificationService = {
  /**
   * Get all notifications for current user
   */
  async getNotifications(params?: QueryParams): Promise<PaginatedResponse<Notification>> {
    try {
      const response = await api.get<PaginatedResponse<Notification>>('/notifications/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get unread notification count
   */
  async getUnreadCount(): Promise<number> {
    try {
      const response = await api.get<{ unread_count: number }>('/notifications/unread_count/');
      return response.unread_count;
    } catch (error) {
      console.error('Failed to fetch unread count:', error);
      return 0;
    }
  },

  /**
   * Mark notification as read
   */
  async markAsRead(notificationId: string): Promise<Notification> {
    try {
      const response = await api.post<Notification>(`/notifications/${notificationId}/mark_read/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Mark all notifications as read
   */
  async markAllAsRead(): Promise<void> {
    try {
      await api.post('/notifications/mark_all_read/');
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete notification
   */
  async deleteNotification(notificationId: string): Promise<void> {
    try {
      await api.delete(`/notifications/${notificationId}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get notification preferences
   */
  async getPreferences(): Promise<any> {
    try {
      const response = await api.get('/notification-preferences/');
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update notification preferences
   */
  async updatePreferences(data: any): Promise<any> {
    try {
      const response = await api.patch('/notification-preferences/', data);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
