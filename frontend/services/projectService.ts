// ============================================================================
// PROJECT SERVICE
// Handles project-related API calls
// ============================================================================

import { api } from './apiClient';
import type {
  Project,
  ProjectDashboardData,
  ProjectFormInput,
  ProjectMetrics,
  ProjectStage,
  PaginatedResponse,
  QueryParams,
} from '@/types';

function mapProjectStatus(status: string): string {
  const normalized = String(status || '').toLowerCase();

  const statusMap: Record<string, string> = {
    planning: 'DESIGN',
    active: 'IMPLEMENTATION',
    on_hold: 'ON_HOLD',
    completed: 'COMPLETED',
    cancelled: 'CANCELLED',
    design: 'DESIGN',
    approval: 'APPROVAL',
    implementation: 'IMPLEMENTATION',
  };

  return statusMap[normalized] || 'DESIGN';
}

function buildProjectPayload(data: ProjectFormInput) {
  const generatedCode = `PRJ-${Date.now().toString().slice(-8)}`;

  return {
    name: data.name,
    code: (data as any).code || generatedCode,
    client_name: data.client,
    project_value: data.contract_value,
    start_date: data.start_date,
    end_date: data.end_date,
    status: mapProjectStatus(String(data.status)),
    description: data.description || '',
  };
}

function mapProjectStage(raw: any): ProjectStage {
  const isCompleted = Boolean(raw?.is_completed);

  return {
    id: String(raw?.id || ''),
    project: String(raw?.project || ''),
    name: String(raw?.name || 'Stage'),
    description: String(raw?.description || ''),
    start_date: String(raw?.start_date || ''),
    end_date: String(raw?.end_date || ''),
    status: isCompleted ? 'completed' : 'not_started',
    completion_percentage: isCompleted ? 100 : 0,
    order: Number(raw?.order || 0),
  };
}

export const projectService = {
  /**
   * Get all projects
   */
  async getProjects(params?: QueryParams): Promise<PaginatedResponse<Project>> {
    try {
      const response = await api.get<PaginatedResponse<Project>>('/projects/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single project
   */
  async getProject(id: string): Promise<Project> {
    try {
      const response = await api.get<Project>(`/projects/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create project
   */
  async createProject(data: ProjectFormInput): Promise<Project> {
    try {
      const response = await api.post<Project>('/projects/', buildProjectPayload(data));
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update project
   */
  async updateProject(id: string, data: ProjectFormInput): Promise<Project> {
    try {
      const response = await api.put<Project>(`/projects/${id}/`, buildProjectPayload(data));
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete project
   */
  async deleteProject(id: string): Promise<void> {
    try {
      await api.delete(`/projects/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get project metrics
   */
  async getProjectMetrics(id: string): Promise<ProjectMetrics> {
    try {
      const response = await api.get<ProjectMetrics>(`/projects/${id}/metrics/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get project stages
   */
  async getProjectStages(projectId: string): Promise<ProjectStage[]> {
    try {
      const response = await api.get<any>(`/project-stages/`, {
        params: { project: projectId },
      });
      const stageList = Array.isArray(response)
        ? response
        : Array.isArray(response?.results)
          ? response.results
          : [];

      return stageList.map(mapProjectStage);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get project dashboard data
   */
  async getProjectDashboard(id: string): Promise<ProjectDashboardData> {
    try {
      const response = await api.get<ProjectDashboardData>(`/projects/${id}/dashboard/`);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
