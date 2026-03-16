// ============================================================================
// SUPPLIER SERVICE
// Frontend ↔ backend field mapping for Supplier
// Backend fields: name, tax_pin, is_active
// Frontend fields: company_name, tax_number, status
// ============================================================================

import { api } from './apiClient';
import type {
  PaginatedResponse,
  Supplier,
  SupplierCreatePayload,
  SupplierQueryParams,
  SupplierUpdatePayload,
} from '@/types';

function normalize(raw: Record<string, unknown>): Supplier {
  const status = raw.status ?? (raw.is_active === false ? 'INACTIVE' : 'ACTIVE');

  return {
    ...(raw as unknown as Supplier),
    company_name: ((raw.company_name || raw.name) as string) ?? '',
    contact_person: ((raw.contact_person as string) || ''),
    registration_number: ((raw.registration_number || raw.company_registration) as string | undefined),
    tax_number: ((raw.tax_number || raw.tax_pin) as string | undefined),
    notes: ((raw.notes as string) || ''),
    status: String(status).toUpperCase(),
    is_active: raw.is_active as boolean | undefined,
  } as Supplier;
}

function normalizeList(
  data: PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]
): PaginatedResponse<Supplier> | Supplier[] {
  if (Array.isArray(data)) return data.map(normalize);
  return {
    ...data,
    results: (data.results as Record<string, unknown>[]).map(normalize),
  } as PaginatedResponse<Supplier>;
}

function toPayload(data: Partial<SupplierCreatePayload>): Record<string, unknown> {
  const payload: Record<string, unknown> = {};

  if (data.company_name !== undefined) payload.name = data.company_name;
  if (data.email !== undefined) payload.email = data.email;
  if (data.phone !== undefined) payload.phone = data.phone;
  if (data.address !== undefined) payload.address = data.address;
  if (data.tax_number !== undefined) payload.tax_pin = data.tax_number;

  if (data.status !== undefined) {
    payload.is_active = String(data.status).toUpperCase() !== 'INACTIVE';
  }

  return payload;
}

export const supplierService = {
  async getSuppliers(params?: SupplierQueryParams): Promise<PaginatedResponse<Supplier> | Supplier[]> {
    const backendParams: Record<string, unknown> = { ...(params as Record<string, unknown>) };

    if (backendParams.status) {
      const normalized = String(backendParams.status).toUpperCase();
      if (normalized === 'ACTIVE') backendParams.is_active = true;
      if (normalized === 'INACTIVE') backendParams.is_active = false;
      delete backendParams.status;
    }

    const data = await api.get<PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]>(
      '/suppliers/',
      { params: backendParams },
    );
    return normalizeList(data);
  },

  async getSupplier(id: string): Promise<Supplier> {
    const data = await api.get<Record<string, unknown>>(`/suppliers/${id}/`);
    return normalize(data);
  },

  async createSupplier(data: SupplierCreatePayload): Promise<Supplier> {
    const payload = toPayload(data);
    const result = await api.post<Record<string, unknown>>('/suppliers/', payload);
    return normalize(result);
  },

  async updateSupplier(id: string, data: SupplierUpdatePayload): Promise<Supplier> {
    const payload = toPayload(data);
    const result = await api.put<Record<string, unknown>>(`/suppliers/${id}/`, payload);
    return normalize(result);
  },

  async deleteSupplier(id: string): Promise<void> {
    await api.delete(`/suppliers/${id}/`);
  },
};
