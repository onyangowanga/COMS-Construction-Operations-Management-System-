// ============================================================================
// SUBCONTRACTOR SERVICE
// Handles subcontractor API calls
// Backend model uses `name`, `company_registration`, `is_active` — mapped here.
// ============================================================================

import { api } from './apiClient';
import type {
  PaginatedResponse,
  Subcontractor,
  SubcontractorFormInput,
  SubcontractorQueryParams,
} from '@/types';

// Normalize a raw backend subcontractor record to the frontend Subcontractor shape
function normalize(raw: Record<string, unknown>): Subcontractor {
  return {
    ...(raw as unknown as Subcontractor),
    // Backend field `name` → frontend `company_name`
    company_name: ((raw.company_name || raw.name) as string) ?? '',
    // Backend field `company_registration` → frontend `registration_number`
    registration_number: ((raw.registration_number || raw.company_registration) as string | undefined),
    // Backend uses is_active boolean; derive status string for UI
    status: raw.status ?? (raw.is_active === false ? 'INACTIVE' : 'ACTIVE'),
  } as Subcontractor;
}

function normalizeList(data: PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]): PaginatedResponse<Subcontractor> | Subcontractor[] {
  if (Array.isArray(data)) return data.map(normalize);
  return { ...data, results: (data.results as Record<string, unknown>[]).map(normalize) } as PaginatedResponse<Subcontractor>;
}

export const subcontractorService = {
  async getSubcontractors(params?: SubcontractorQueryParams): Promise<PaginatedResponse<Subcontractor> | Subcontractor[]> {
    // Map frontend `status` filter to backend `is_active`
    const backendParams: Record<string, unknown> = { ...(params as Record<string, unknown>) };
    if (backendParams.status) {
      if (String(backendParams.status).toUpperCase() === 'ACTIVE') backendParams.is_active = true;
      else if (String(backendParams.status).toUpperCase() === 'INACTIVE') backendParams.is_active = false;
      delete backendParams.status;
    }
    const data = await api.get<PaginatedResponse<Record<string, unknown>> | Record<string, unknown>[]>('/subcontractors/', { params: backendParams });
    return normalizeList(data);
  },

  async getSubcontractor(id: string): Promise<Subcontractor> {
    const data = await api.get<Record<string, unknown>>(`/subcontractors/${id}/`);
    return normalize(data);
  },

  async createSubcontractor(data: SubcontractorFormInput): Promise<Subcontractor> {
    // Map frontend field names to backend field names
    const payload = {
      name: data.company_name,
      contact_person: data.contact_person,
      email: data.email,
      phone: data.phone,
      specialization: data.specialization ?? '',
      address: data.address ?? '',
      company_registration: data.registration_number ?? '',
      notes: data.notes ?? '',
    };
    const result = await api.post<Record<string, unknown>>('/subcontractors/', payload);
    return normalize(result);
  },

  async updateSubcontractor(id: string, data: Partial<SubcontractorFormInput>): Promise<Subcontractor> {
    const payload: Record<string, unknown> = {};
    if (data.company_name    !== undefined) payload.name                 = data.company_name;
    if (data.contact_person  !== undefined) payload.contact_person       = data.contact_person;
    if (data.email           !== undefined) payload.email                = data.email;
    if (data.phone           !== undefined) payload.phone                = data.phone;
    if (data.specialization  !== undefined) payload.specialization       = data.specialization;
    if (data.address         !== undefined) payload.address              = data.address;
    if (data.registration_number !== undefined) payload.company_registration = data.registration_number;
    if (data.notes           !== undefined) payload.notes                = data.notes;
    const result = await api.put<Record<string, unknown>>(`/subcontractors/${id}/`, payload);
    return normalize(result);
  },

  async deleteSubcontractor(id: string): Promise<void> {
    await api.delete(`/subcontractors/${id}/`);
  },
};
