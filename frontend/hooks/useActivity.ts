// ============================================================================
// USE ACTIVITY HOOK
// ============================================================================

'use client';

import { useApi } from './useApi';
import { activityService } from '@/services';
import type {
  Activity,
  ActivityQueryParams,
  PaginatedResponse,
} from '@/types';

interface UseActivityOptions {
  enabled?: boolean;
}

function normalizeList(data: PaginatedResponse<Activity> | Activity[] | undefined) {
  const activities = Array.isArray(data)
    ? data
    : Array.isArray((data as PaginatedResponse<Activity> | undefined)?.results)
      ? (data as PaginatedResponse<Activity>).results
      : [];

  const totalCount = Array.isArray(data)
    ? data.length
    : (data as PaginatedResponse<Activity> | undefined)?.count || 0;

  return {
    activities,
    totalCount,
    nextPage: Array.isArray(data) ? null : (data as PaginatedResponse<Activity> | undefined)?.next || null,
    previousPage: Array.isArray(data) ? null : (data as PaginatedResponse<Activity> | undefined)?.previous || null,
  };
}

export function useActivity(params?: ActivityQueryParams, options?: UseActivityOptions) {
  const { useQuery, invalidateQueries } = useApi();

  const { data, isLoading, error, isFetching } = useQuery(
    ['activity', params],
    () => activityService.getActivities(params),
    {
      staleTime: 60 * 1000,
      enabled: options?.enabled ?? true,
    }
  );

  const normalized = normalizeList(data);

  return {
    activities: normalized.activities as Activity[],
    totalCount: normalized.totalCount,
    nextPage: normalized.nextPage,
    previousPage: normalized.previousPage,
    isLoading,
    isFetching,
    error,
    refetchActivity: () => invalidateQueries(['activity']),
  };
}

export function useActivityItem(id?: string, options?: UseActivityOptions) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['activity-item', id],
    () => activityService.getActivity(id as string),
    {
      enabled: !!id && (options?.enabled ?? true),
      staleTime: 60 * 1000,
    }
  );

  return {
    activity: data as Activity | undefined,
    isLoading,
    error,
  };
}
