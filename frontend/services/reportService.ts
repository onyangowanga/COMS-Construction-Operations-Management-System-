// ============================================================================
// REPORT SERVICE
// Handles report generation and management
// ============================================================================

import { api } from './apiClient';
import type { Report, ReportExecution, PaginatedResponse, QueryParams } from '@/types';

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
      const response = await api.get<PaginatedResponse<ReportExecution>>('/report-executions/', {
        params: { report: reportId, ordering: '-executed_at' },
      });
      return response.results;
    } catch (error) {
      throw error;
    }
  },
};
