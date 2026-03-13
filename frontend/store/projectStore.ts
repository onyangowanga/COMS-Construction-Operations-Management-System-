// ============================================================================
// PROJECT STORE
// Global project state management
// ============================================================================

import { create } from 'zustand';
import type { Project, ProjectFormInput } from '@/types';
import { projectService } from '@/services';

interface ProjectState {
  projects: Project[];
  selectedProject: Project | null;
  isLoading: boolean;
  error: string | null;
  
  // Actions
  setProjects: (projects: Project[]) => void;
  addProject: (project: Project) => void;
  updateProject: (id: string, data: Partial<Project>) => void;
  removeProject: (id: string) => void;
  selectProject: (project: Project | null) => void;
  
  // API actions
  fetchProjects: (params?: any) => Promise<void>;
  fetchProject: (id: string) => Promise<void>;
  createProject: (data: ProjectFormInput) => Promise<Project>;
  updateProjectById: (id: string, data: ProjectFormInput) => Promise<void>;
  deleteProject: (id: string) => Promise<void>;
  
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
}

export const useProjectStore = create<ProjectState>((set, get) => ({
  projects: [],
  selectedProject: null,
  isLoading: false,
  error: null,

  setProjects: (projects) => {
    set({ projects, error: null });
  },

  addProject: (project) => {
    set((state) => ({
      projects: [project, ...state.projects],
    }));
  },

  updateProject: (id, data) => {
    set((state) => ({
      projects: state.projects.map((p) =>
        p.id === id ? { ...p, ...data } : p
      ),
      selectedProject:
        state.selectedProject?.id === id
          ? { ...state.selectedProject, ...data }
          : state.selectedProject,
    }));
  },

  removeProject: (id) => {
    set((state) => ({
      projects: state.projects.filter((p) => p.id !== id),
      selectedProject:
        state.selectedProject?.id === id ? null : state.selectedProject,
    }));
  },

  selectProject: (project) => {
    set({ selectedProject: project });
  },

  fetchProjects: async (params) => {
    try {
      set({ isLoading: true, error: null });
      const response = await projectService.getProjects(params);
      set({ projects: response.results, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch projects',
        isLoading: false,
      });
    }
  },

  fetchProject: async (id) => {
    try {
      set({ isLoading: true, error: null });
      const project = await projectService.getProject(id);
      set({ selectedProject: project, isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to fetch project',
        isLoading: false,
      });
    }
  },

  createProject: async (data) => {
    try {
      set({ isLoading: true, error: null });
      const project = await projectService.createProject(data);
      get().addProject(project);
      set({ isLoading: false });
      return project;
    } catch (error: any) {
      set({
        error: error.message || 'Failed to create project',
        isLoading: false,
      });
      throw error;
    }
  },

  updateProjectById: async (id, data) => {
    try {
      set({ isLoading: true, error: null });
      const project = await projectService.updateProject(id, data);
      get().updateProject(id, project);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to update project',
        isLoading: false,
      });
      throw error;
    }
  },

  deleteProject: async (id) => {
    try {
      set({ isLoading: true, error: null });
      await projectService.deleteProject(id);
      get().removeProject(id);
      set({ isLoading: false });
    } catch (error: any) {
      set({
        error: error.message || 'Failed to delete project',
        isLoading: false,
      });
      throw error;
    }
  },

  setLoading: (isLoading) => set({ isLoading }),

  setError: (error) => set({ error }),
}));
