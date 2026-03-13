// ============================================================================
// VARIATION SERVICE
// Handles variation order API calls
// ============================================================================

import { api } from './apiClient';
import type {
  PaginatedResponse,
  VariationFormInput,
  VariationOrder,
  VariationQueryParams,
} from '@/types';

export const variationService = {
  /**
   * Get all variations
   */
  async getVariations(params?: VariationQueryParams): Promise<PaginatedResponse<VariationOrder>> {
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
  async createVariation(data: VariationFormInput): Promise<VariationOrder> {
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
  async updateVariation(id: string, data: Partial<VariationFormInput>): Promise<VariationOrder> {
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

  /**
   * Certify variation
   */
  async certifyVariation(id: string, data: { certified_amount: string; notes?: string }): Promise<VariationOrder> {
    try {
      const response = await api.post<VariationOrder>(`/variations/${id}/certify/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
