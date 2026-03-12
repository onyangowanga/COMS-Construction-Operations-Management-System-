// ============================================================================
// CLAIM SERVICE
// Handles claim/valuation API calls
// ============================================================================

import { api } from './apiClient';
import type { Claim, PaginatedResponse, QueryParams } from '@/types';

export const claimService = {
  /**
   * Get all claims
   */
  async getClaims(params?: QueryParams): Promise<PaginatedResponse<Claim>> {
    try {
      const response = await api.get<PaginatedResponse<Claim>>('/valuations/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single claim
   */
  async getClaim(id: string): Promise<Claim> {
    try {
      const response = await api.get<Claim>(`/valuations/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create claim
   */
  async createClaim(data: Partial<Claim>): Promise<Claim> {
    try {
      const response = await api.post<Claim>('/valuations/', data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update claim
   */
  async updateClaim(id: string, data: Partial<Claim>): Promise<Claim> {
    try {
      const response = await api.patch<Claim>(`/valuations/${id}/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete claim
   */
  async deleteClaim(id: string): Promise<void> {
    try {
      await api.delete(`/valuations/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Submit claim
   */
  async submitClaim(id: string): Promise<Claim> {
    try {
      const response = await api.post<Claim>(`/valuations/${id}/submit/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Certify claim
   */
  async certifyClaim(id: string, data: { certified_amount: string; notes?: string }): Promise<Claim> {
    try {
      const response = await api.post<Claim>(`/valuations/${id}/certify/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Approve claim
   */
  async approveClaim(id: string): Promise<Claim> {
    try {
      const response = await api.post<Claim>(`/valuations/${id}/approve/`);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
