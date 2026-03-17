// ============================================================================
// NOTIFICATION SERVICE
// Handles notifications via spec-aligned endpoints
// ============================================================================

import { api } from './apiClient';
import type { Notification, NotificationQueryParams, PaginatedResponse } from '@/types';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function normalize(rawInput: unknown): Notification {
  const raw = asRecord(rawInput);
  const type = String(raw.type || raw.notification_type || 'INFO').toUpperCase();
  const module = raw.module
    ? String(raw.module).toUpperCase()
    : raw.related_object_type
    ? String(raw.related_object_type).toUpperCase()
    : undefined;
  const entityId =
    raw.entity_id != null
      ? String(raw.entity_id)
      : raw.related_object_id != null
      ? String(raw.related_object_id)
      : undefined;
  const entityReference =
    raw.entity_reference != null ? String(raw.entity_reference) : undefined;
  const priorityRaw = String(raw.priority || 'MEDIUM').toUpperCase();
  const priority = ['LOW', 'MEDIUM', 'HIGH'].includes(priorityRaw) ? priorityRaw : 'MEDIUM';

  return {
    id: String(raw.id || ''),
    title: String(raw.title || 'Notification'),
    message: String(raw.message || ''),
    type,
    module,
    entity_id: entityId,
    entity_reference: entityReference,
    is_read: Boolean(raw.is_read),
    created_at: String(raw.created_at || new Date().toISOString()),
    action_url: raw.action_url ? String(raw.action_url) : undefined,
    priority,
  };
}

function normalizeList(
  data: PaginatedResponse<unknown> | unknown[]
): PaginatedResponse<Notification> | Notification[] {
  if (Array.isArray(data)) return data.map(normalize);
  return { ...data, results: (data.results || []).map(normalize) } as PaginatedResponse<Notification>;
}

export const notificationService = {
  async getNotifications(
    params?: NotificationQueryParams
  ): Promise<PaginatedResponse<Notification> | Notification[]> {
    const data = await api.get<PaginatedResponse<unknown> | unknown[]>('/notifications/', { params });
    return normalizeList(data);
  },

  async getNotification(id: string): Promise<Notification> {
    const data = await api.get<unknown>(`/notifications/${id}/`);
    return normalize(data);
  },

  async markAsRead(id: string): Promise<Notification> {
    try {
      const data = await api.post<unknown>(`/notifications/${id}/read/`);
      const normalized = normalize(data);

      // Some backends return only a message for mark-read actions.
      if (!normalized.id) {
        return this.getNotification(id);
      }

      return normalized;
    } catch {
      await api.post(`/notifications/${id}/mark_read/`);
      return this.getNotification(id);
    }
  },

  async markAllAsRead(): Promise<void> {
    try {
      await api.post('/notifications/read-all/');
    } catch {
      await api.post('/notifications/mark_all_read/');
    }
  },

  async getUnreadCount(): Promise<number> {
    try {
      const response = await api.get<{ unread_count?: number; total?: number }>('/notifications/unread_count/');
      if (typeof response.unread_count === 'number') return response.unread_count;
      if (typeof response.total === 'number') return response.total;
      return 0;
    } catch {
      return 0;
    }
  },

  async deleteNotification(id: string): Promise<void> {
    await api.delete(`/notifications/${id}/`);
  },
};

