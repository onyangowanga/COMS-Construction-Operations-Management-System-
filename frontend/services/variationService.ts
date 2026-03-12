// ============================================================================
// VARIATION SERVICE
// Handles variation order API calls
// ============================================================================

import { api } from './apiClient';
import type { VariationOrder, PaginatedResponse, QueryParams } from '@/types';

export const variationService = {
  /**
   * Get all variations
   */
  async getVariations(params?: QueryParams): Promise<PaginatedResponse<VariationOrder>> {
    try {
      const response = await api.get<PaginatedResponse<VariationOrder>>('/variations/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single variation
   */
  async getVariation(id: string): Promise<VariationOrder> {
    try {
      const response = await api.get<VariationOrder>(`/variations/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create variation
   */
  async createVariation(data: Partial<VariationOrder>): Promise<VariationOrder> {
    try {
      const response = await api.post<VariationOrder>('/variations/', data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update variation
   */
  async updateVariation(id: string, data: Partial<VariationOrder>): Promise<VariationOrder> {
    try {
      const response = await api.patch<VariationOrder>(`/variations/${id}/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete variation
   */
  async deleteVariation(id: string): Promise<void> {
    try {
      await api.delete(`/variations/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Submit variation for review
   */
  async submitVariation(id: string): Promise<VariationOrder> {
    try {
      const response = await api.post<VariationOrder>(`/variations/${id}/submit/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Approve variation
   */
  async approveVariation(id: string, data: { approved_value: string; notes?: string }): Promise<VariationOrder> {
    try {
      const response = await api.post<VariationOrder>(`/variations/${id}/approve/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Reject variation
   */
  async rejectVariation(id: string, reason: string): Promise<VariationOrder> {
    try {
      const response = await api.post<VariationOrder>(`/variations/${id}/reject/`, {
        rejection_reason: reason,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },
};
