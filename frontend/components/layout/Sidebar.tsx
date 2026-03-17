// ============================================================================
// SIDEBAR COMPONENT
// Navigation sidebar with menu items and permission-based rendering
// ============================================================================

'use client';

import React from 'react';
import Link from 'next/link';
import Image from 'next/image';
import { usePathname } from 'next/navigation';
import { 
  Activity as ActivityIcon,
  Bell,
  ChevronLeft, 
  ChevronRight,
  LayoutDashboard,
  FolderKanban,
  FileText,
  FileStack,
  GitBranch,
  Receipt,
  ShoppingCart,
  BarChart3,
  Settings,
  Settings2,
  Users,
  type LucideIcon
} from 'lucide-react';
import { cn } from '@/utils/helpers';
import { useUIStore, useAuthStore } from '@/store';
import { SIDEBAR_NAVIGATION } from '@/utils/constants';

// Icon mapping
const iconMap: Record<string, LucideIcon> = {
  Activity: ActivityIcon,
  Bell,
  LayoutDashboard,
  FolderKanban,
  FileText,
  FileStack,
  GitBranch,
  Receipt,
  ShoppingCart,
  BarChart3,
  Settings,
  Settings2,
  Users,
};

export const Sidebar: React.FC = () => {
  const pathname = usePathname();
  const { sidebarCollapsed, toggleSidebarCollapse } = useUIStore();
  const { hasPermission, hasAnyPermission } = useAuthStore();

  // Filter navigation items based on permissions
  const visibleNavItems = SIDEBAR_NAVIGATION.filter((item) => {
    if (!item.permission) return true;
    if (Array.isArray(item.permission)) {
      return hasAnyPermission(item.permission);
    }
    return hasPermission(item.permission);
  });

  return (
    <aside
      className={cn(
        'fixed left-0 top-0 h-screen bg-gray-900 text-white transition-all duration-300 z-30',
        sidebarCollapsed ? 'w-16' : 'w-64'
      )}
    >
      {/* Logo */}
      <div className="flex items-center justify-between h-16 px-4 border-b border-gray-800">
        {!sidebarCollapsed && (
          <div className="flex items-center gap-2">
            <Image 
              src="/logo.png" 
              alt="COMS Logo" 
              width={32} 
              height={32}
              className="rounded"
            />
            <span className="text-xl font-bold">COMS</span>
          </div>
        )}
        {sidebarCollapsed && (
          <div className="flex items-center justify-center w-full">
            <Image 
              src="/favicon-96x96.png" 
              alt="COMS" 
              width={24} 
              height={24}
              className="rounded"
            />
          </div>
        )}
        <button
          onClick={toggleSidebarCollapse}
          className={cn(
            "p-1.5 rounded-lg hover:bg-gray-800 transition-colors",
            sidebarCollapsed && "absolute right-1"
          )}
        >
          {sidebarCollapsed ? (
            <ChevronRight className="h-5 w-5" />
          ) : (
            <ChevronLeft className="h-5 w-5" />
          )}
        </button>
      </div>

      {/* Navigation */}
      <nav className="flex-1 overflow-y-auto py-4">
        {visibleNavItems.map((item) => {
          const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
          const Icon = iconMap[item.icon] || LayoutDashboard;

          return (
            <div key={item.href}>
              <Link
                href={item.href}
                className={cn(
                  'flex items-center gap-3 px-4 py-3 mx-2 rounded-lg transition-colors',
                  'hover:bg-gray-800',
                  isActive ? 'bg-primary-600 text-white' : 'text-gray-300',
                  sidebarCollapsed && 'justify-center'
                )}
                title={sidebarCollapsed ? item.name : undefined}
              >
                <Icon className="h-5 w-5 shrink-0" />
                {!sidebarCollapsed && (
                  <span className="font-medium">{item.name}</span>
                )}
              </Link>

              {/* Subsections */}
              {!sidebarCollapsed && item.subsections && isActive && (
                <div className="ml-8 mt-1 space-y-1">
                  {item.subsections.map((sub) => {
                    const isSubActive = pathname === sub.href;
                    return (
                      <Link
                        key={sub.href}
                        href={sub.href}
                        className={cn(
                          'block px-4 py-2 text-sm rounded-lg transition-colors',
                          isSubActive
                            ? 'text-white bg-gray-800'
                            : 'text-gray-400 hover:text-white hover:bg-gray-800'
                        )}
                      >
                        {sub.name}
                      </Link>
                    );
                  })}
                </div>
              )}
            </div>
          );
        })}
      </nav>
    </aside>
  );
};
