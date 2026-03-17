// ============================================================================
// REPORT SERVICE
// Handles report generation and management
// ============================================================================

import { api } from './apiClient';
import type {
  DashboardWidgetData,
  PaginatedResponse,
  QueryParams,
  Report,
  ReportCreatePayload,
  ReportExecution,
  ReportSchedule,
  ReportScheduleCreatePayload,
} from '@/types';

export const reportService = {
  /**
   * Get all reports
   */
  async getReports(params?: QueryParams): Promise<PaginatedResponse<Report>> {
    try {
      const response = await api.get<PaginatedResponse<Report>>('/reports/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single report
   */
  async getReport(id: string): Promise<Report> {
    try {
      const response = await api.get<Report>(`/reports/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create report definition
   */
  async createReport(payload: ReportCreatePayload): Promise<Report> {
    try {
      const response = await api.post<Report>('/reports/', payload);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update report definition
   */
  async updateReport(id: string, payload: Partial<ReportCreatePayload>): Promise<Report> {
    try {
      const response = await api.patch<Report>(`/reports/${id}/`, payload);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete report
   */
  async deleteReport(id: string): Promise<void> {
    try {
      await api.delete(`/reports/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get next auto-generated report code preview
   */
  async getNextCode(): Promise<{ code: string; sequence: number; year: number }> {
    try {
      const response = await api.get<{ code: string; sequence: number; year: number }>('/reports/next-code/');
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Execute report
   */
  async executeReport(
    id: string,
    parameters?: Record<string, any>
  ): Promise<ReportExecution> {
    try {
      const response = await api.post<ReportExecution>(`/reports/${id}/execute/`, {
        parameters,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get report execution status
   */
  async getExecutionStatus(executionId: string): Promise<ReportExecution> {
    try {
      const response = await api.get<ReportExecution>(`/report-executions/${executionId}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Download report output
   */
  async downloadReport(executionId: string, filename: string): Promise<void> {
    try {
      await api.download(`/report-executions/${executionId}/download/`, filename);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get report executions history
   */
  async getExecutionHistory(reportId: string): Promise<ReportExecution[]> {
    try {
      const response = await api.get<ReportExecution[]>(`/reports/${reportId}/executions/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get global execution history
   */
  async getExecutions(params?: QueryParams): Promise<PaginatedResponse<ReportExecution>> {
    try {
      const response = await api.get<PaginatedResponse<ReportExecution>>('/report-executions/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * List report schedules
   */
  async getSchedules(params?: QueryParams): Promise<PaginatedResponse<ReportSchedule>> {
    try {
      const response = await api.get<PaginatedResponse<ReportSchedule>>('/report-schedules/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Create schedule for a report
   */
  async createSchedule(payload: ReportScheduleCreatePayload): Promise<ReportSchedule> {
    try {
      const response = await api.post<ReportSchedule>('/report-schedules/', payload);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete report schedule
   */
  async deleteSchedule(id: string): Promise<void> {
    try {
      await api.delete(`/report-schedules/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Load dashboard widget payloads
   */
  async getDashboardWidgets(): Promise<DashboardWidgetData[]> {
    try {
      const response = await api.get<DashboardWidgetData[]>('/widgets/dashboard/');
      return response;
    } catch (error) {
      throw error;
    }
  },
};
