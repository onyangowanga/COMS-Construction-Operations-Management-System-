// ============================================================================
// CONTRACT SERVICE
// ============================================================================

import { api } from './apiClient';
import type {
  Contract,
  ContractCreatePayload,
  ContractQueryParams,
  ContractUpdatePayload,
  PaginatedResponse,
} from '@/types';

function normalize(raw: Contract): Contract {
  return {
    ...raw,
    status: String(raw.status || 'DRAFT').toUpperCase(),
    currency: raw.currency || 'KES',
  };
}

function normalizeList(
  data: PaginatedResponse<Contract> | Contract[]
): PaginatedResponse<Contract> | Contract[] {
  if (Array.isArray(data)) return data.map(normalize);
  return {
    ...data,
    results: data.results.map(normalize),
  };
}

export const contractService = {
  async getNextNumber(): Promise<{ contract_reference: string; sequence: number; year: number }> {
    const data = await api.get<{ contract_reference: string; sequence: number; year: number }>('/subcontracts/next-reference/');
    return data;
  },

  async getContracts(params?: ContractQueryParams): Promise<PaginatedResponse<Contract> | Contract[]> {
    const data = await api.get<PaginatedResponse<Contract> | Contract[]>('/contracts/', {
      params,
    });
    return normalizeList(data);
  },

  async getContract(id: string): Promise<Contract> {
    const data = await api.get<Contract>(`/contracts/${id}/`);
    return normalize(data);
  },

  async createContract(data: ContractCreatePayload): Promise<Contract> {
    const result = await api.post<Contract>('/contracts/', data);
    return normalize(result);
  },

  async updateContract(id: string, data: ContractUpdatePayload): Promise<Contract> {
    const result = await api.put<Contract>(`/contracts/${id}/`, data);
    return normalize(result);
  },

  async deleteContract(id: string): Promise<void> {
    await api.delete(`/contracts/${id}/`);
  },
};
