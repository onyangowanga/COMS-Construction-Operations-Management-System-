// ============================================================================
// USE PROJECTS HOOK
// Custom hook for project data management
// ============================================================================

'use client';

import { useEffect } from 'react';
import { useProjectStore } from '@/store';
import { useApi } from './useApi';
import { projectService } from '@/services';
import type {
  Project,
  ProjectDashboardData,
  ProjectFormInput,
  ProjectMetrics,
  ProjectStage,
  QueryParams,
} from '@/types';

export function useProjects(params?: QueryParams) {
  const { projects, selectedProject, isLoading: storeLoading, error: storeError, selectProject } = useProjectStore();

  const { useQuery, useMutation, invalidateQueries } = useApi();

  // Fetch projects with React Query
  const {
    data: projectsData,
    isLoading: queryLoading,
    error: queryError,
  } = useQuery(
    ['projects', params],
    () => projectService.getProjects(params),
    {
      enabled: true,
      staleTime: 5 * 60 * 1000, // 5 minutes
    }
  );

  // Create project mutation
  const createMutation = useMutation(
    (data: ProjectFormInput) => projectService.createProject(data),
    {
      showSuccessToast: true,
      successMessage: 'Project Created',
      onSuccess: () => {
        invalidateQueries(['projects']);
      },
    }
  );

  // Update project mutation
  const updateMutation = useMutation(
    ({ id, data }: { id: string; data: ProjectFormInput }) =>
      projectService.updateProject(id, data),
    {
      showSuccessToast: true,
      successMessage: 'Project Updated',
      onSuccess: () => {
        invalidateQueries(['projects']);
        if (selectedProject) {
          invalidateQueries(['project', selectedProject.id]);
        }
      },
    }
  );

  // Delete project mutation
  const deleteMutation = useMutation(
    (id: string) => projectService.deleteProject(id),
    {
      showSuccessToast: true,
      successMessage: 'Project Deleted',
      onSuccess: () => {
        invalidateQueries(['projects']);
      },
    }
  );

  return {
    projects: projectsData?.results || projects,
    totalCount: projectsData?.count || 0,
    nextPage: projectsData?.next || null,
    previousPage: projectsData?.previous || null,
    selectedProject,
    isLoading: queryLoading || storeLoading,
    error: queryError || storeError,
    
    // Actions
    selectProject,
    refetchProjects: () => invalidateQueries(['projects']),
    createProject: createMutation.mutateAsync,
    updateProject: updateMutation.mutateAsync,
    deleteProject: deleteMutation.mutateAsync,
    
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

// Hook for single project
export function useProject(id?: string) {
  const { selectProject } = useProjectStore();
  const { useQuery } = useApi();

  const {
    data: project,
    isLoading,
    error,
  } = useQuery(
    ['project', id],
    () => projectService.getProject(id as string),
    {
      enabled: !!id,
    }
  );

  // Select project when data is loaded
  useEffect(() => {
    if (project && typeof project === 'object' && 'id' in project) {
      selectProject(project as Project);
    }
  }, [project, selectProject]);

  return {
    project,
    isLoading,
    error,
  };
}

export function useProjectMetrics(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['project-metrics', id],
    () => projectService.getProjectMetrics(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    metrics: data as ProjectMetrics | undefined,
    isLoading,
    error,
  };
}

export function useProjectDashboard(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['project-dashboard', id],
    () => projectService.getProjectDashboard(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    dashboard: data as ProjectDashboardData | undefined,
    isLoading,
    error,
  };
}

export function useProjectStages(id?: string) {
  const { useQuery } = useApi();

  const { data, isLoading, error } = useQuery(
    ['project-stages', id],
    () => projectService.getProjectStages(id as string),
    {
      enabled: !!id,
      staleTime: 2 * 60 * 1000,
    }
  );

  return {
    stages: (data || []) as ProjectStage[],
    isLoading,
    error,
  };
}
