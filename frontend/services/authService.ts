// ============================================================================
// AUTHENTICATION SERVICE
// Handles user authentication, token management, and user session
// ============================================================================

import { api } from './apiClient';
import Cookies from 'js-cookie';
import { TOKEN_KEY, REFRESH_TOKEN_KEY, USER_KEY } from '@/utils/constants';
import type { 
  LoginCredentials, 
  LoginResponse, 
  User, 
  AuthTokens 
} from '@/types';

export const authService = {
  /**
   * Login user
   */
  async login(credentials: LoginCredentials): Promise<LoginResponse> {
    try {
      const response = await api.post<LoginResponse>('/auth/login/', credentials);
      
      // Store tokens
      Cookies.set(TOKEN_KEY, response.access, { expires: 1 });
      Cookies.set(REFRESH_TOKEN_KEY, response.refresh, { expires: 7 });
      
      // Store user
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(response.user));
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Logout user
   */
  async logout(): Promise<void> {
    try {
      const refreshToken = Cookies.get(REFRESH_TOKEN_KEY);
      
      if (refreshToken) {
        await api.post('/auth/logout/', { refresh: refreshToken });
      }
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      // Clear tokens and user data
      Cookies.remove(TOKEN_KEY);
      Cookies.remove(REFRESH_TOKEN_KEY);
      
      if (typeof window !== 'undefined') {
        localStorage.removeItem(USER_KEY);
      }
    }
  },

  /**
   * Refresh access token
   */
  async refreshToken(): Promise<string> {
    const refreshToken = Cookies.get(REFRESH_TOKEN_KEY);
    
    if (!refreshToken) {
      throw new Error('No refresh token available');
    }

    try {
      const response = await api.post<{ access: string }>('/auth/token/refresh/', {
        refresh: refreshToken,
      });
      
      Cookies.set(TOKEN_KEY, response.access, { expires: 1 });
      
      return response.access;
    } catch (error) {
      // Token refresh failed, logout user
      this.logout();
      throw error;
    }
  },

  /**
   * Get current user
   */
  async getCurrentUser(): Promise<User> {
    try {
      const response = await api.get<User>('/auth/me/');
      
      // Update stored user data
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(response));
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Update user profile
   */
  async updateProfile(data: Partial<User>): Promise<User> {
    try {
      const response = await api.patch<User>('/auth/me/', data);
      
      // Update stored user data
      if (typeof window !== 'undefined') {
        localStorage.setItem(USER_KEY, JSON.stringify(response));
      }
      
      return response;
    } catch (error) {
      throw error;
    }
  },

  /**
   * Change password
   */
  async changePassword(data: {
    old_password: string;
    new_password: string;
  }): Promise<void> {
    try {
      await api.post('/auth/change-password/', data);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Request password reset
   */
  async requestPasswordReset(email: string): Promise<void> {
    try {
      await api.post('/auth/password-reset/', { email });
    } catch (error) {
      throw error;
    }
  },

  /**
   * Reset password with token
   */
  async resetPassword(data: {
    token: string;
    password: string;
  }): Promise<void> {
    try {
      await api.post('/auth/password-reset/confirm/', data);
    } catch (error) {
      throw error;
    }
  },

  /**
   * Check if user is authenticated
   */
  isAuthenticated(): boolean {
    if (typeof window === 'undefined') return false;
    
    const token = Cookies.get(TOKEN_KEY);
    return !!token;
  },

  /**
   * Get stored user
   */
  getStoredUser(): User | null {
    if (typeof window === 'undefined') return null;
    
    const userStr = localStorage.getItem(USER_KEY);
    
    if (!userStr) return null;
    
    try {
      return JSON.parse(userStr);
    } catch (error) {
      return null;
    }
  },

  /**
   * Get access token
   */
  getToken(): string | undefined {
    return Cookies.get(TOKEN_KEY);
  },

  /**
   * Get refresh token
   */
  getRefreshToken(): string | undefined {
    return Cookies.get(REFRESH_TOKEN_KEY);
  },
};
