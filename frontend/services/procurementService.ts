// ============================================================================
// PROCUREMENT SERVICE
// Handles purchase order and procurement API calls
// ============================================================================

import { api } from './apiClient';
import type { PurchaseOrder, PaginatedResponse, QueryParams } from '@/types';

export const procurementService = {
  /**
   * Get all purchase orders
   */
  async getPurchaseOrders(params?: QueryParams): Promise<PaginatedResponse<PurchaseOrder>> {
    try {
      const response = await api.get<PaginatedResponse<PurchaseOrder>>('/procurement/purchase-orders/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single purchase order
   */
  async getPurchaseOrder(id: string): Promise<PurchaseOrder> {
    try {
      const response = await api.get<PurchaseOrder>(`/procurement/purchase-orders/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create purchase order
   */
  async createPurchaseOrder(data: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    try {
      const response = await api.post<PurchaseOrder>('/procurement/purchase-orders/', data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update purchase order
   */
  async updatePurchaseOrder(id: string, data: Partial<PurchaseOrder>): Promise<PurchaseOrder> {
    try {
      const response = await api.patch<PurchaseOrder>(`/procurement/purchase-orders/${id}/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete purchase order
   */
  async deletePurchaseOrder(id: string): Promise<void> {
    try {
      await api.delete(`/procurement/purchase-orders/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Approve purchase order
   */
  async approvePurchaseOrder(id: string): Promise<PurchaseOrder> {
    try {
      const response = await api.post<PurchaseOrder>(`/procurement/purchase-orders/${id}/approve/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Mark purchase order as received
   */
  async receivePurchaseOrder(id: string, data: { received_date: string; notes?: string }): Promise<PurchaseOrder> {
    try {
      const response = await api.post<PurchaseOrder>(`/procurement/purchase-orders/${id}/receive/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
