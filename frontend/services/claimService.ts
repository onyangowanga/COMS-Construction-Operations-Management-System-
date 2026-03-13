// ============================================================================
// CLAIM SERVICE
// Handles claim/valuation API calls
// ============================================================================

import { api } from './apiClient';
import type { Claim, ClaimFormInput, ClaimQueryParams, PaginatedResponse } from '@/types';

async function withFallback<T>(primary: () => Promise<T>, fallback: () => Promise<T>): Promise<T> {
  try {
    return await primary();
  } catch (error: any) {
    const status = error?.status || error?.response?.status;
    if (status === 404 || status === 405) {
      return fallback();
    }
    throw error;
  }
}

export const claimService = {
  /**
   * Get all claims
   */
  async getClaims(params?: ClaimQueryParams): Promise<PaginatedResponse<Claim>> {
    return withFallback(
      () => api.get<PaginatedResponse<Claim>>('/claims/', { params }),
      () => api.get<PaginatedResponse<Claim>>('/valuations/', { params })
    );
  },

  /**
   * Get single claim
   */
  async getClaim(id: string): Promise<Claim> {
    return withFallback(() => api.get<Claim>(`/claims/${id}/`), () => api.get<Claim>(`/valuations/${id}/`));
  },

  /**
   * Create claim
   */
  async createClaim(data: ClaimFormInput): Promise<Claim> {
    return withFallback(() => api.post<Claim>('/claims/', data), () => api.post<Claim>('/valuations/', data));
  },

  /**
   * Update claim
   */
  async updateClaim(id: string, data: Partial<Claim>): Promise<Claim> {
    return withFallback(
      () => api.patch<Claim>(`/claims/${id}/`, data),
      () => api.patch<Claim>(`/valuations/${id}/`, data)
    );
  },

  /**
   * Delete claim
   */
  async deleteClaim(id: string): Promise<void> {
    await withFallback(() => api.delete(`/claims/${id}/`), () => api.delete(`/valuations/${id}/`));
  },

  /**
   * Submit claim
   */
  async submitClaim(id: string): Promise<Claim> {
    return withFallback(
      () => api.post<Claim>(`/claims/${id}/submit/`),
      () => api.post<Claim>(`/valuations/${id}/submit/`)
    );
  },

  /**
   * Certify claim
   */
  async certifyClaim(id: string, data: { certified_amount: string; notes?: string }): Promise<Claim> {
    return withFallback(
      () => api.post<Claim>(`/claims/${id}/certify/`, data),
      () => api.post<Claim>(`/valuations/${id}/certify/`, data)
    );
  },

  /**
   * Approve claim
   */
  async approveClaim(id: string): Promise<Claim> {
    return withFallback(
      () => api.post<Claim>(`/claims/${id}/approve/`),
      () => api.post<Claim>(`/valuations/${id}/approve/`)
    );
  },

  /**
   * Reject claim
   */
  async rejectClaim(id: string, reason: string): Promise<Claim> {
    return withFallback(
      () => api.post<Claim>(`/claims/${id}/reject/`, { rejection_reason: reason }),
      () => api.post<Claim>(`/valuations/${id}/reject/`, { notes: reason })
    );
  },

  /**
   * Mark claim paid
   */
  async markPaid(id: string, payment_date: string): Promise<Claim> {
    return withFallback(
      () => api.post<Claim>(`/claims/${id}/paid/`, { payment_date }),
      () => api.post<Claim>(`/valuations/${id}/mark_paid/`, { payment_date })
    );
  },
};
