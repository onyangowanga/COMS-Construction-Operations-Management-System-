// ============================================================================
// PROCUREMENT SERVICE
// Frontend ↔ backend field mapping for the LocalPurchaseOrder (LPO) model.
// Backend endpoint: /api/purchase-orders/
// Frontend fields  →  Backend fields
//   reference_number → lpo_number
//   order_value      → total_amount
//   delivery_date    → delivery_deadline
//   description      → notes (when notes not supplied separately)
//   supplier         → supplier  (must be a Supplier UUID)
// Workflow actions: /approve/, /mark-delivered/, /mark-invoiced/, /mark-paid/
// ============================================================================

import { api } from './apiClient';
import type {
  PaginatedResponse,
  ProcurementOrder,
  ProcurementOrderFormInput,
  ProcurementQueryParams,
} from '@/types';

// Normalize backend LPO record to frontend ProcurementOrder shape
function normalize(raw: Record<string, unknown>): ProcurementOrder {
  return {
    ...(raw as unknown as ProcurementOrder),
    // Map backend names → frontend names for consistent UI rendering
    reference_number: ((raw.reference_number || raw.lpo_number) as string) ?? '',
    order_value: raw.order_value ?? raw.total_amount ?? 0,
    delivery_date: (raw.delivery_date || raw.delivery_deadline || '') as string,
    description: (raw.description || raw.notes || '') as string,
  } as ProcurementOrder;
}

function normalizeList(data: PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]): PaginatedResponse<ProcurementOrder> | ProcurementOrder[] {
  if (Array.isArray(data)) return data.map(normalize);
  return { ...data, results: (data.results as Record<string, unknown>[]).map(normalize) } as PaginatedResponse<ProcurementOrder>;
}

function toPayload(data: Partial<ProcurementOrderFormInput>): Record<string, unknown> {
  const payload: Record<string, unknown> = {};
  if (data.reference_number !== undefined) payload.lpo_number       = data.reference_number;
  if (data.project          !== undefined) payload.project          = data.project;
  if (data.supplier         !== undefined) payload.supplier         = data.supplier;
  if (data.order_value      !== undefined) payload.total_amount     = data.order_value;
  if (data.delivery_date    !== undefined) payload.delivery_deadline = data.delivery_date || null;
  if (data.notes            !== undefined) payload.notes            = data.notes;
  if (data.description      !== undefined && !data.notes) payload.notes = data.description;
  if (data.status           !== undefined) payload.status           = data.status;
  return payload;
}

export const procurementService = {
  // List suppliers so the form can render a supplier dropdown
  async getSuppliers(): Promise<Array<{ id: string; name: string }>> {
    const data = await api.get<PaginatedResponse<{ id: string; name: string }> | { id: string; name: string }[]>('/suppliers/');
    if (Array.isArray(data)) return data;
    return (data as PaginatedResponse<{ id: string; name: string }>).results ?? [];
  },

  async getOrders(params?: ProcurementQueryParams): Promise<PaginatedResponse<ProcurementOrder> | ProcurementOrder[]> {
    const data = await api.get<PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]>('/purchase-orders/', { params });
    return normalizeList(data);
  },

  async getOrder(id: string): Promise<ProcurementOrder> {
    const data = await api.get<Record<string, unknown>>(`/purchase-orders/${id}/`);
    return normalize(data);
  },

  async createOrder(data: ProcurementOrderFormInput): Promise<ProcurementOrder> {
    const payload = toPayload(data);
    // issue_date is required by backend – default to today
    if (!payload.issue_date) {
      payload.issue_date = new Date().toISOString().split('T')[0];
    }
    const result = await api.post<Record<string, unknown>>('/purchase-orders/', payload);
    return normalize(result);
  },

  async updateOrder(id: string, data: Partial<ProcurementOrderFormInput>): Promise<ProcurementOrder> {
    const result = await api.put<Record<string, unknown>>(`/purchase-orders/${id}/`, toPayload(data));
    return normalize(result);
  },

  async deleteOrder(id: string): Promise<void> {
    await api.delete(`/purchase-orders/${id}/`);
  },

  // Backend workflow actions on LocalPurchaseOrder
  async approveOrder(id: string): Promise<ProcurementOrder> {
    const result = await api.post<Record<string, unknown>>(`/purchase-orders/${id}/approve/`);
    return normalize(result);
  },

  async markDelivered(id: string): Promise<ProcurementOrder> {
    const result = await api.post<Record<string, unknown>>(`/purchase-orders/${id}/mark-delivered/`);
    return normalize(result);
  },

  async markInvoiced(id: string, invoiceNumber?: string): Promise<ProcurementOrder> {
    const result = await api.post<Record<string, unknown>>(`/purchase-orders/${id}/mark-invoiced/`, invoiceNumber ? { invoice_number: invoiceNumber } : {});
    return normalize(result);
  },

  async markPaid(id: string, paymentReference?: string): Promise<ProcurementOrder> {
    const result = await api.post<Record<string, unknown>>(`/purchase-orders/${id}/mark-paid/`, paymentReference ? { payment_reference: paymentReference } : {});
    return normalize(result);
  },

  // Keep submitOrder / closeOrder as aliases so existing hook calls don't break
  async submitOrder(id: string): Promise<ProcurementOrder> {
    return procurementService.approveOrder(id);
  },

  async closeOrder(id: string): Promise<ProcurementOrder> {
    return procurementService.markPaid(id);
  },
};
