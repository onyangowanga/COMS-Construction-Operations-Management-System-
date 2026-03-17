// ============================================================================
// CONTRACT TYPES
// ============================================================================

export enum ContractStatus {
  DRAFT = 'DRAFT',
  ACTIVE = 'ACTIVE',
  COMPLETED = 'COMPLETED',
  TERMINATED = 'TERMINATED',
}

export interface ContractQueryParams {
  page?: number;
  page_size?: number;
  search?: string;
  ordering?: string;
  status?: string;
}

export interface ContractCreatePayload {
  contract_number: string;
  project_name: string;
  client: string;
  contractor?: string;
  consultant?: string;
  contract_value: number | string;
  currency?: string;
  start_date: string;
  end_date?: string;
  status?: ContractStatus | string;
  description?: string;
}

export interface ContractUpdatePayload extends Partial<ContractCreatePayload> {}

export interface Contract {
  id: string;
  contract_number: string;
  project_name: string;
  client: string;
  contractor?: string;
  consultant?: string;
  contract_value: number | string;
  currency: string;
  start_date: string;
  end_date?: string;
  status: ContractStatus | string;
  description?: string;
  created_at: string;
  updated_at: string;
}
