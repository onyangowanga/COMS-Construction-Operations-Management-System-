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
      const response = await api.post<Project>('/projects/', data);
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
      const response = await api.put<Project>(`/projects/${id}/`, data);
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
      const response = await api.get<ProjectStage[]>(`/project-stages/`, {
        params: { project: projectId },
      });
      return response;
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
