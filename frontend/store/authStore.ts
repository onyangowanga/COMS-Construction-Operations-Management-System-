// ============================================================================
// AUTH STORE
// Global authentication state management with Zustand
// ============================================================================

import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User, LoginCredentials } from '@/types';
import { authService } from '@/services';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  isInitialized: boolean;
  error: string | null;
  
  // Actions
  setUser: (user: User | null) => void;
  setLoading: (loading: boolean) => void;
  setError: (error: string | null) => void;
  initializeAuth: () => Promise<void>;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => Promise<void>;
  refreshUser: () => Promise<void>;
  updateUser: (data: Partial<User>) => void;
  
  // Permission helpers
  hasPermission: (permissionCode: string) => boolean;
  hasRole: (roleCode: string) => boolean;
  hasAnyPermission: (permissionCodes: string[]) => boolean;
  hasAllPermissions: (permissionCodes: string[]) => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,
      isInitialized: false,
      error: null,

      setUser: (user) => {
        set({ 
          user, 
          isAuthenticated: !!user,
          isInitialized: true,
          error: null 
        });
      },

      setLoading: (isLoading) => set({ isLoading }),

      setError: (error) => set({ error }),

      initializeAuth: async () => {
        if (get().isInitialized || get().isLoading) {
          return;
        }

        try {
          set({ isLoading: true, error: null });
          const user = await authService.getCurrentUser();
          set({
            user,
            isAuthenticated: true,
            isLoading: false,
            isInitialized: true,
            error: null,
          });
        } catch (error) {
          authService.clearStoredAuth();
          set({
            user: null,
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true,
          });
        }
      },

      login: async (credentials) => {
        try {
          set({ isLoading: true, error: null });
          const response = await authService.login(credentials);
          set({ 
            user: response.user, 
            isAuthenticated: true,
            isLoading: false,
            isInitialized: true,
          });
        } catch (error: any) {
          set({ 
            error: error.message || 'Login failed',
            isLoading: false,
            isInitialized: true,
          });
          throw error;
        }
      },

      logout: async () => {
        try {
          set({ isLoading: true });
          await authService.logout();
          set({ 
            user: null, 
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true,
            error: null
          });
        } catch (error) {
          console.error('Logout error:', error);
          // Clear state anyway
          set({ 
            user: null, 
            isAuthenticated: false,
            isLoading: false,
            isInitialized: true,
          });
        }
      },

      refreshUser: async () => {
        try {
          set({ isLoading: true, error: null });
          const user = await authService.getCurrentUser();
          set({ user, isAuthenticated: true, isLoading: false, isInitialized: true });
        } catch (error) {
          console.error('Failed to refresh user:', error);
          authService.clearStoredAuth();
          set({ user: null, isAuthenticated: false, isLoading: false, isInitialized: true });
        }
      },

      updateUser: (data) => {
        const { user } = get();
        if (user) {
          set({ user: { ...user, ...data } });
        }
      },

      hasPermission: (permissionCode) => {
        const { user } = get();
        if (!user) return false;
        return user.permissions?.includes(permissionCode) || false;
      },

      hasRole: (roleCode) => {
        const { user } = get();
        if (!user) return false;
        return user.roles?.some(r => r.role_code === roleCode) || false;
      },

      hasAnyPermission: (permissionCodes) => {
        const { user } = get();
        if (!user) return false;
        return permissionCodes.some(code => 
          user.permissions?.includes(code)
        );
      },

      hasAllPermissions: (permissionCodes) => {
        const { user } = get();
        if (!user) return false;
        return permissionCodes.every(code => 
          user.permissions?.includes(code)
        );
      },
    }),
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);
