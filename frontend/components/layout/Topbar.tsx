// ============================================================================
// TOPBAR COMPONENT
// Top navigation bar with user menu and notifications
// ============================================================================

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Bell, User, LogOut, Settings, ChevronDown } from 'lucide-react';
import { cn } from '@/utils/helpers';
import { useAuthStore, useUIStore } from '@/store';
import { useAuth, useNotifications } from '@/hooks';
import { Badge } from '../ui';
import { getInitials, getAvatarColor } from '@/utils/formatters';

export const Topbar: React.FC = () => {
  const { user } = useAuthStore();
  const { sidebarCollapsed } = useUIStore();
  const { logout } = useAuth();
  const { unreadCount } = useNotifications();
  const [showUserMenu, setShowUserMenu] = useState(false);
  const [showNotifications, setShowNotifications] = useState(false);

  return (
    <header
      className={cn(
        'fixed top-0 right-0 h-16 bg-white border-b border-gray-200 transition-all duration-300 z-20',
        sidebarCollapsed ? 'left-16' : 'left-64'
      )}
    >
      <div className="flex items-center justify-between h-full px-6">
        {/* Left side - could add breadcrumbs or search */}
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-semibold text-gray-900">Dashboard</h1>
        </div>

        {/* Right side - notifications and user menu */}
        <div className="flex items-center gap-4">
          {/* Notifications */}
          <div className="relative">
            <button
              onClick={() => setShowNotifications(!showNotifications)}
              className="relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <Bell className="h-5 w-5" />
              {unreadCount > 0 && (
                <span className="absolute top-1 right-1 h-4 w-4 bg-destructive-600 text-white text-xs rounded-full flex items-center justify-center">
                  {unreadCount > 9 ? '9+' : unreadCount}
                </span>
              )}
            </button>

            {/* Notification dropdown - simplified */}
            {showNotifications && (
              <div className="absolute right-0 mt-2 w-80 bg-white rounded-lg shadow-lg border border-gray-200 py-2">
                <div className="px-4 py-2 border-b border-gray-200">
                  <h3 className="font-semibold text-gray-900">Notifications</h3>
                </div>
                <div className="max-h-96 overflow-y-auto">
                  <div className="px-4 py-8 text-center text-gray-500">
                    No new notifications
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* User menu */}
          <div className="relative">
            <button
              onClick={() => setShowUserMenu(!showUserMenu)}
              className="flex items-center gap-3 p-2 hover:bg-gray-100 rounded-lg transition-colors"
            >
              <div
                className={cn(
                  'h-8 w-8 rounded-full flex items-center justify-center text-white font-medium text-sm',
                  getAvatarColor(user?.full_name || user?.username || '')
                )}
              >
                {getInitials(user?.full_name || user?.username || '')}
              </div>
              <div className="text-left">
                <p className="text-sm font-medium text-gray-900">
                  {user?.full_name || user?.username}
                </p>
                <p className="text-xs text-gray-500">
                  {user?.roles?.[0]?.role_name || 'User'}
                </p>
              </div>
              <ChevronDown className="h-4 w-4 text-gray-500" />
            </button>

            {/* User dropdown */}
            {showUserMenu && (
              <div className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-lg border border-gray-200 py-2">
                <Link
                  href="/profile"
                  className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <User className="h-4 w-4" />
                  <span>Profile</span>
                </Link>
                <Link
                  href="/settings"
                  className="flex items-center gap-3 px-4 py-2 text-gray-700 hover:bg-gray-100 transition-colors"
                  onClick={() => setShowUserMenu(false)}
                >
                  <Settings className="h-4 w-4" />
                  <span>Settings</span>
                </Link>
                <hr className="my-2 border-gray-200" />
                <button
                  onClick={() => {
                    setShowUserMenu(false);
                    logout();
                  }}
                  className="flex items-center gap-3 w-full px-4 py-2 text-destructive-600 hover:bg-destructive-50 transition-colors"
                >
                  <LogOut className="h-4 w-4" />
                  <span>Logout</span>
                </button>
              </div>
            )}
          </div>
        </div>
      </div>
    </header>
  );
};
