// ============================================================================
// DASHBOARD LAYOUT
// Main layout wrapper for authenticated pages
// ============================================================================

'use client';

import React, { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { cn } from '@/utils/helpers';
import { useUIStore, useAuthStore } from '@/store';
import { Sidebar } from './Sidebar';
import { Topbar } from './Topbar';
import { LoadingSpinner } from '@/components/ui';

export interface DashboardLayoutProps {
  children: React.ReactNode;
}

export const DashboardLayout: React.FC<DashboardLayoutProps> = ({ children }) => {
  const router = useRouter();
  const { sidebarCollapsed } = useUIStore();
  const { isAuthenticated, isLoading, user } = useAuthStore();

  useEffect(() => {
    // Only redirect if definitely not authenticated and not loading
    if (!isLoading && !isAuthenticated && !user) {
      router.push('/login');
    }
  }, [isAuthenticated, isLoading, user, router]);

  // Show loading while checking authentication
  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <LoadingSpinner size="lg" />
      </div>
    );
  }

  // Don't render if not authenticated
  if (!isAuthenticated && !user) {
    return null;
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Sidebar />
      <Topbar />
      <main
        className={cn(
          'pt-16 transition-all duration-300',
          sidebarCollapsed ? 'ml-16' : 'ml-64'
        )}
      >
        <div className="p-6">{children}</div>
      </main>
    </div>
  );
};
