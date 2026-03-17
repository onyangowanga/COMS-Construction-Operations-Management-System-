// ============================================================================
// USE REPORTS HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { reportService } from '@/services';
import type {
  DashboardWidgetData,
  PaginatedResponse,
  QueryParams,
  Report,
  ReportCreatePayload,
  ReportExecution,
  ReportExecutionProgress,
  ReportSchedule,
  ReportScheduleCreatePayload,
} from '@/types';

function normalizeList<T>(data: PaginatedResponse<T> | T[] | undefined) {
  const results = Array.isArray(data)
    ? data
    : Array.isArray((data as PaginatedResponse<T> | undefined)?.results)
      ? (data as PaginatedResponse<T>).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as PaginatedResponse<T> | undefined)?.count || 0;

  return { results, totalCount };
}

export function useReports(params?: QueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(['reports', params], () => reportService.getReports(params), {
    staleTime: 2 * 60 * 1000,
  });

  const createMutation = useMutation((payload: ReportCreatePayload) => reportService.createReport(payload), {
    showSuccessToast: true,
    successMessage: 'Report Created',
    onSuccess: () => invalidateQueries(['reports']),
  });

  const updateMutation = useMutation(
    ({ id, payload }: { id: string; payload: Partial<ReportCreatePayload> }) =>
      reportService.updateReport(id, payload),
    {
      showSuccessToast: true,
      successMessage: 'Report Updated',
      onSuccess: (updated: Report) => {
        invalidateQueries(['reports']);
        invalidateQueries(['report', updated.id]);
      },
    }
  );

  const deleteMutation = useMutation((id: string) => reportService.deleteReport(id), {
    showSuccessToast: true,
    successMessage: 'Report Deleted',
    onSuccess: () => invalidateQueries(['reports']),
  });

  const normalized = normalizeList<Report>(data);

  return {
    reports: normalized.results,
    totalCount: normalized.totalCount,
    isLoading,
    error,
    createReport: createMutation.mutateAsync,
    updateReport: updateMutation.mutateAsync,
    deleteReport: deleteMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useReport(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(['report', id], () => reportService.getReport(id as string), {
    enabled: !!id,
    staleTime: 2 * 60 * 1000,
  });

  return {
    report: data,
    isLoading,
    error,
  };
}

export function useReportExecutions(reportId?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error, refetch } = useQuery(
    ['report-executions', reportId],
    () => reportService.getExecutionHistory(reportId as string),
    {
      enabled: !!reportId,
      staleTime: 30 * 1000,
    }
  );

  return {
    executions: (data || []) as ReportExecution[],
    isLoading,
    error,
    refetch,
  };
}

export function useReportExecutionProgress(executionId?: string, enabled = true) {
  const { useQuery } = useApi();

  const { data, isLoading, error, refetch } = useQuery(
    ['report-execution-progress', executionId],
    () => reportService.getExecutionProgress(executionId as string),
    {
      enabled: Boolean(executionId) && enabled,
      staleTime: 0,
      refetchInterval: 2000,
      refetchIntervalInBackground: true,
    }
  );

  return {
    progress: data as ReportExecutionProgress | undefined,
    isLoading,
    error,
    refetch,
  };
}

export function useReportSchedules(params?: QueryParams) {
  const { useQuery, useMutation, invalidateQueries } = useApi();

  const { data, isLoading, error } = useQuery(
    ['report-schedules', params],
    () => reportService.getSchedules(params),
    {
      staleTime: 30 * 1000,
    }
  );

  const createMutation = useMutation((payload: ReportScheduleCreatePayload) => reportService.createSchedule(payload), {
    showSuccessToast: true,
    successMessage: 'Schedule Created',
    onSuccess: () => invalidateQueries(['report-schedules']),
  });

  const deleteMutation = useMutation((id: string) => reportService.deleteSchedule(id), {
    showSuccessToast: true,
    successMessage: 'Schedule Deleted',
    onSuccess: () => invalidateQueries(['report-schedules']),
  });

  const normalized = normalizeList<ReportSchedule>(data);

  return {
    schedules: normalized.results,
    totalCount: normalized.totalCount,
    isLoading,
    error,
    createSchedule: createMutation.mutateAsync,
    deleteSchedule: deleteMutation.mutateAsync,
    isCreating: createMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

export function useDashboardWidgets() {
  const { useQuery } = useApi();

  const { data, isLoading, error, refetch } = useQuery(
    ['dashboard-widgets'],
    () => reportService.getDashboardWidgets(),
    {
      staleTime: 30 * 1000,
    }
  );

  return {
    widgets: (data || []) as DashboardWidgetData[],
    isLoading,
    error,
    refetch,
  };
}
