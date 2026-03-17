// ============================================================================
// PROJECT TYPES
// ============================================================================

export interface Project {
  id: string;
  name: string;
  code: string;
  description: string;
  client: string;
  client_name: string;
  organization: string;
  organization_name: string;
  status: ProjectStatus;
  type: ProjectType;
  contract_value: string;
  start_date: string;
  end_date: string;
  completion_percentage: number;
  budget_consumed: number;
  variation_value: string;
  claim_value: string;
  location?: string;
  project_manager?: string;
  project_manager_name?: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectFormInput {
  code?: string;
  name: string;
  client: string;
  contract_value: string;
  project_manager?: string;
  start_date: string;
  end_date: string;
  status: ProjectStatus;
  description?: string;
}

export enum ProjectStatus {
  PLANNING = 'planning',
  ACTIVE = 'active',
  ON_HOLD = 'on_hold',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled',
}

export enum ProjectType {
  BUILDING = 'building',
  INFRASTRUCTURE = 'infrastructure',
  RENOVATION = 'renovation',
  CIVIL_WORKS = 'civil_works',
}

export interface ProjectStage {
  id: string;
  project: string;
  name: string;
  description: string;
  start_date: string;
  end_date: string;
  status: 'not_started' | 'in_progress' | 'completed' | 'delayed';
  completion_percentage: number;
  order: number;
}

export interface ProjectMetrics {
  project_id: string;
  project_name: string;
  total_budget: number;
  spent_amount: number;
  remaining_budget: number;
  budget_utilization: number;
  completion_percentage: number;
  schedule_variance: number;
  cost_variance: number;
  earned_value: number;
  planned_value: number;
  actual_cost: number;
}

export interface BudgetVsActualPoint {
  period: string;
  budget: number;
  actual: number;
}

export interface VariationTrendPoint {
  period: string;
  value: number;
}

export interface ClaimProgressPoint {
  period: string;
  certified: number;
  submitted: number;
}

export interface ProjectDashboardData {
  kpis: {
    contract_value: number;
    total_variations: number;
    approved_claims: number;
    completion_percentage: number;
  };
  budget_vs_actual: BudgetVsActualPoint[];
  variation_trend: VariationTrendPoint[];
  claim_progress: ClaimProgressPoint[];
  recent_documents: Array<{
    id: string;
    title: string;
    created_at: string;
  }>;
  recent_variations: Array<{
    id: string;
    title: string;
    status: string;
    estimated_value?: number;
    created_at: string;
  }>;
  recent_activity: Array<{
    id: string;
    action: string;
    actor_name?: string;
    created_at: string;
  }>;
}
