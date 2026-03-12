// ============================================================================
// USE PROJECTS HOOK
// Custom hook for project data management
// ============================================================================

'use client';

import { useProjectStore } from '@/store';
import { useApi } from './useApi';
import { projectService } from '@/services';
import type { Project, QueryParams } from '@/types';

export function useProjects(params?: QueryParams) {
  const {
    projects,
    selectedProject,
    isLoading: storeLoading,
    error: storeError,
    fetchProjects,
    fetchProject,
    createProject,
    updateProjectById,
    deleteProject,
    selectProject,
  } = useProjectStore();

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
    (data: Partial<Project>) => projectService.createProject(data),
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
    ({ id, data }: { id: string; data: Partial<Project> }) =>
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
    selectedProject,
    isLoading: queryLoading || storeLoading,
    error: queryError || storeError,
    
    // Actions
    selectProject,
    createProject: createMutation.mutate,
    updateProject: updateMutation.mutate,
    deleteProject: deleteMutation.mutate,
    
    // Mutation states
    isCreating: createMutation.isPending,
    isUpdating: updateMutation.isPending,
    isDeleting: deleteMutation.isPending,
  };
}

// Hook for single project
export function useProject(id: string) {
  const { selectProject } = useProjectStore();
  const { useQuery } = useApi();

  const {
    data: project,
    isLoading,
    error,
  } = useQuery(
    ['project', id],
    () => projectService.getProject(id),
    {
      enabled: !!id,
      onSuccess: (data) => {
        selectProject(data);
      },
    }
  );

  return {
    project,
    isLoading,
    error,
  };
}
