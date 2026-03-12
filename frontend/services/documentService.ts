// ============================================================================
// DOCUMENT SERVICE
// Handles document management API calls
// ============================================================================

import { api } from './apiClient';
import type { Document, PaginatedResponse, QueryParams } from '@/types';

export const documentService = {
  /**
   * Get all documents
   */
  async getDocuments(params?: QueryParams): Promise<PaginatedResponse<Document>> {
    try {
      const response = await api.get<PaginatedResponse<Document>>('/documents/', {
        params,
      });
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Get single document
   */
  async getDocument(id: string): Promise<Document> {
    try {
      const response = await api.get<Document>(`/documents/${id}/`);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Upload document
   */
  async uploadDocument(
    data: {
      title: string;
      description?: string;
      category: string;
      project?: string;
      file: File;
    },
    onProgress?: (progress: number) => void
  ): Promise<Document> {
    try {
      const formData = new FormData();
      formData.append('title', data.title);
      if (data.description) formData.append('description', data.description);
      formData.append('category', data.category);
      if (data.project) formData.append('project', data.project);
      formData.append('file', data.file);

      const response = await api.upload<Document>('/documents/', formData, (event) => {
        if (onProgress && event.total) {
          const progress = Math.round((event.loaded * 100) / event.total);
          onProgress(progress);
        }
      });

      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update document
   */
  async updateDocument(id: string, data: Partial<Document>): Promise<Document> {
    try {
      const response = await api.patch<Document>(`/documents/${id}/`, data);
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Delete document
   */
  async deleteDocument(id: string): Promise<void> {
    try {
      await api.delete(`/documents/${id}/`);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Download document
   */
  async downloadDocument(id: string, filename: string): Promise<void> {
    try {
      await api.download(`/documents/${id}/download/`, filename);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Approve document
   */
  async approveDocument(id: string): Promise<Document> {
    try {
      const response = await api.post<Document>(`/documents/${id}/approve/`);
      return response;
    } catch (error) {
      throw error;
    }
  },
};
