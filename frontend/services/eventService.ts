// ============================================================================
// EVENT SERVICE
// Handles system events and activity feed
// ============================================================================

import { api } from './apiClient';
import type { SystemEvent, ActivityFeedItem, PaginatedResponse, QueryParams } from '@/types';

export const eventService = {
  /**
   * Get system events (activity feed)
   */
  async getEvents(params?: QueryParams): Promise<PaginatedResponse<SystemEvent>> {
    try {
      const response = await api.get<PaginatedResponse<SystemEvent>>('/events/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get recent activity feed
   */
  async getActivityFeed(limit: number = 20): Promise<SystemEvent[]> {
    try {
      const response = await api.get<PaginatedResponse<SystemEvent>>('/events/', {
        params: {
          page_size: limit,
          ordering: '-timestamp',
        },
      });
      return response.results;
    } catch (error) {
      console.error('Failed to fetch activity feed:', error);
      return [];
    }
  },

  /**
   * Get events by category
   */
  async getEventsByCategory(category: string, params?: QueryParams): Promise<PaginatedResponse<SystemEvent>> {
    try {
      const response = await api.get<PaginatedResponse<SystemEvent>>('/events/', {
        params: {
          ...params,
          category,
        },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get events by user
   */
  async getEventsByUser(userId: number, params?: QueryParams): Promise<PaginatedResponse<SystemEvent>> {
    try {
      const response = await api.get<PaginatedResponse<SystemEvent>>('/events/', {
        params: {
          ...params,
          user: userId,
        },
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get event analytics
   */
  async getAnalytics(params?: {
    startDate?: string;
    endDate?: string;
    category?: string;
  }): Promise<any> {
    try {
      const response = await api.get('/events/analytics/', { params });
      return response;
    } catch (error) {
      throw error;
    }
  },
};
