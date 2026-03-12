// ============================================================================
// API CLIENT
// Centralized Axios instance with interceptors for JWT and error handling
// ============================================================================

import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse, AxiosError } from 'axios';
import Cookies from 'js-cookie';
import { API_URL, TOKEN_KEY, REFRESH_TOKEN_KEY } from '@/utils/constants';
import type { ApiResponse, ApiError } from '@/types';

// Create Axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
  withCredentials: true, // Enable sending cookies with requests
});

// ============================================================================
// Request Interceptor - Attach JWT Token
// ============================================================================

apiClient.interceptors.request.use(
  (config) => {
    const token = Cookies.get(TOKEN_KEY);
    const csrfToken = Cookies.get('csrftoken');
    
    if (token && !config.headers.Authorization) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    
    // Add CSRF token for unsafe methods
    if (csrfToken && ['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
      config.headers['X-CSRFToken'] = csrfToken;
    }
    
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// ============================================================================
// Response Interceptor - Handle Token Refresh & Errors
// ============================================================================

let isRefreshing = false;
let failedQueue: Array<{
  resolve: (value?: any) => void;
  reject: (reason?: any) => void;
}> = [];

const processQueue = (error: any, token: string | null = null) => {
  failedQueue.forEach((prom) => {
    if (error) {
      prom.reject(error);
    } else {
      prom.resolve(token);
    }
  });
  
  failedQueue = [];
};

apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  async (error: AxiosError) => {
    const originalRequest: any = error.config;

    // Handle 401 Unauthorized - Token Refresh
    if (error.response?.status === 401 && !originalRequest._retry) {
      if (isRefreshing) {
        return new Promise((resolve, reject) => {
          failedQueue.push({ resolve, reject });
        })
          .then((token) => {
            originalRequest.headers.Authorization = `Bearer ${token}`;
            return apiClient(originalRequest);
          })
          .catch((err) => {
            return Promise.reject(err);
          });
      }

      originalRequest._retry = true;
      isRefreshing = true;

      const refreshToken = Cookies.get(REFRESH_TOKEN_KEY);

      if (!refreshToken) {
        processQueue(error, null);
        isRefreshing = false;
        
        // Redirect to login
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        
        return Promise.reject(error);
      }

      try {
        const response = await axios.post(`${API_URL}/auth/token/refresh/`, {
          refresh: refreshToken,
        });

        const { access } = response.data;
        
        Cookies.set(TOKEN_KEY, access, { expires: 1 });
        
        apiClient.defaults.headers.Authorization = `Bearer ${access}`;
        originalRequest.headers.Authorization = `Bearer ${access}`;
        
        processQueue(null, access);
        
        return apiClient(originalRequest);
      } catch (refreshError) {
        processQueue(refreshError, null);
        
        // Clear tokens and redirect to login
        Cookies.remove(TOKEN_KEY);
        Cookies.remove(REFRESH_TOKEN_KEY);
        
        if (typeof window !== 'undefined') {
          window.location.href = '/login';
        }
        
        return Promise.reject(refreshError);
      } finally {
        isRefreshing = false;
      }
    }

    // Handle other errors
    return Promise.reject(handleApiError(error));
  }
);

// ============================================================================
// Error Handler
// ============================================================================

function handleApiError(error: AxiosError): ApiError {
  if (error.response) {
    // Server responded with error
    const data: any = error.response.data;
    
    return {
      message: data?.message || data?.detail || 'An error occurred',
      status: error.response.status,
      errors: data?.errors || data,
    };
  } else if (error.request) {
    // Request made but no response
    return {
      message: 'No response from server. Please check your connection.',
      status: 0,
    };
  } else {
    // Error in request configuration
    return {
      message: error.message || 'An unexpected error occurred',
      status: 0,
    };
  }
}

// ============================================================================
// API Methods
// ============================================================================

/**
 * Fetch CSRF token from the server
 * This should be called before making any POST/PUT/PATCH/DELETE requests
 */
export const fetchCSRFToken = async (): Promise<void> => {
  try {
    // Make a GET request to get the CSRF cookie
    await apiClient.get('/csrf/');
  } catch (error) {
    console.warn('Failed to fetch CSRF token:', error);
  }
};

export const api = {
  /**
   * GET request
   */
  get: async <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.get<T>(url, config);
    return response.data;
  },

  /**
   * POST request
   */
  post: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.post<T>(url, data, config);
    return response.data;
  },

  /**
   * PUT request
   */
  put: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.put<T>(url, data, config);
    return response.data;
  },

  /**
   * PATCH request
   */
  patch: async <T = any>(
    url: string,
    data?: any,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.patch<T>(url, data, config);
    return response.data;
  },

  /**
   * DELETE request
   */
  delete: async <T = any>(
    url: string,
    config?: AxiosRequestConfig
  ): Promise<T> => {
    const response = await apiClient.delete<T>(url, config);
    return response.data;
  },

  /**
   * Upload file
   */
  upload: async <T = any>(
    url: string,
    formData: FormData,
    onUploadProgress?: (progressEvent: any) => void
  ): Promise<T> => {
    const response = await apiClient.post<T>(url, formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
      onUploadProgress,
    });
    return response.data;
  },

  /**
   * Download file
   */
  download: async (
    url: string,
    filename: string
  ): Promise<void> => {
    const response = await apiClient.get(url, {
      responseType: 'blob',
    });
    
    const blob = new Blob([response.data]);
    const link = document.createElement('a');
    link.href = window.URL.createObjectURL(blob);
    link.download = filename;
    link.click();
    window.URL.revokeObjectURL(link.href);
  },
};

export default apiClient;
