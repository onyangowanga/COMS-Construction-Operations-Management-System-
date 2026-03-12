// ============================================================================
// USE AUTH HOOK
// Custom hook for authentication functionality
// ============================================================================

'use client';

import { useCallback, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store';
import { authService } from '@/services';

export function useAuth() {
  const router = useRouter();
  const {
    user,
    isAuthenticated,
    isLoading,
    isInitialized,
    error,
    initializeAuth,
    login,
    logout,
    refreshUser,
    updateUser,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions,
  } = useAuthStore();

  // Check if user is authenticated on mount
  useEffect(() => {
    initializeAuth();
  }, [initializeAuth]);

  // Login handler
  const handleLogin = useCallback(
    async (credentials: { email: string; password: string }) => {
      await login(credentials);
      router.push('/dashboard');
    },
    [login, router]
  );

  // Logout handler
  const handleLogout = useCallback(async () => {
    await logout();
    router.push('/login');
  }, [logout, router]);

  // Update profile handler
  const handleUpdateProfile = useCallback(
    async (data: any) => {
      try {
        const updatedUser = await authService.updateProfile(data);
        updateUser(updatedUser);
        return updatedUser;
      } catch (error) {
        throw error;
      }
    },
    [updateUser]
  );

  // Change password handler
  const handleChangePassword = useCallback(
    async (oldPassword: string, newPassword: string) => {
      await authService.changePassword({ old_password: oldPassword, new_password: newPassword });
    },
    []
  );

  return {
    user,
    isAuthenticated,
    isLoading,
    isInitialized,
    error,
    login: handleLogin,
    logout: handleLogout,
    refreshUser,
    updateProfile: handleUpdateProfile,
    changePassword: handleChangePassword,
    hasPermission,
    hasRole,
    hasAnyPermission,
    hasAllPermissions,
  };
}
