// ============================================================================
// NOTIFICATIONS PAGE
// Full notifications list with filters, pagination, and bulk actions
// ============================================================================

'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { Bell, CheckCheck, ChevronLeft, ChevronRight } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { NotificationList } from '@/components/notifications';
import { Card, CardHeader, CardTitle, CardContent, Button, Badge } from '@/components/ui';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { useNotifications } from '@/hooks';

// --------------------------------------------------------------------------
// Read-filter tab type
// --------------------------------------------------------------------------

type ReadFilter = 'all' | 'unread' | 'read';

const PAGE_SIZE = 20;

// --------------------------------------------------------------------------
// Page
// --------------------------------------------------------------------------

export default function NotificationsPage() {
  const [readFilter, setReadFilter] = useState<ReadFilter>('all');
  const [page, setPage] = useState(1);

  const queryParams = {
    page,
    page_size: PAGE_SIZE,
    ...(readFilter === 'unread' ? { is_read: false } : readFilter === 'read' ? { is_read: true } : {}),
  };

  const {
    notifications,
    totalCount,
    isLoading,
    isFetching,
    unreadCount,
    markAsRead,
    markAllAsRead,
    isMarkingAllRead,
  } = useNotifications(queryParams);

  const totalPages = Math.ceil(totalCount / PAGE_SIZE);

  function handleFilterChange(filter: ReadFilter) {
    setReadFilter(filter);
    setPage(1);
  }

  return (
    <PermissionGuard permission={['notification.view', 'view_notification']}>
      <DashboardLayout>
        <div className="max-w-3xl mx-auto space-y-6">
          {/* Header */}
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Notifications</h1>
              <p className="text-gray-600 mt-1">
                {unreadCount > 0
                  ? `You have ${unreadCount} unread notification${unreadCount !== 1 ? 's' : ''}`
                  : "You're all caught up!"}
              </p>
            </div>

            {unreadCount > 0 && (
              <Button
                variant="outline"
                size="sm"
                onClick={() => markAllAsRead(undefined)}
                disabled={isMarkingAllRead}
                className="flex items-center gap-2"
              >
                <CheckCheck className="h-4 w-4" />
                Mark all as read
              </Button>
            )}
          </div>

          {/* Filter tabs */}
          <Card>
            <CardHeader className="pb-0">
              <div className="flex items-center gap-1 border-b border-gray-200 -mx-6 px-6">
                {(['all', 'unread', 'read'] as ReadFilter[]).map((filter) => (
                  <button
                    key={filter}
                    onClick={() => handleFilterChange(filter)}
                    className={`px-4 py-3 text-sm font-medium border-b-2 transition-colors capitalize ${
                      readFilter === filter
                        ? 'border-primary-600 text-primary-700'
                        : 'border-transparent text-gray-600 hover:text-gray-900'
                    }`}
                  >
                    {filter}
                    {filter === 'unread' && unreadCount > 0 && (
                      <Badge variant="destructive" size="sm" className="ml-2">
                        {unreadCount}
                      </Badge>
                    )}
                  </button>
                ))}
              </div>
            </CardHeader>

            <CardContent className="p-0">
              {/* Status bar */}
              {isFetching && !isLoading && (
                <div className="text-xs text-gray-400 text-right px-4 py-1">Refreshing…</div>
              )}

              <NotificationList
                notifications={notifications}
                isLoading={isLoading}
                onMarkAsRead={(id) => markAsRead(id)}
                emptyMessage={
                  readFilter === 'unread'
                    ? 'No unread notifications'
                    : readFilter === 'read'
                    ? 'No read notifications'
                    : 'No notifications yet'
                }
              />
            </CardContent>
          </Card>

          {/* Pagination */}
          {totalPages > 1 && (
            <div className="flex items-center justify-between text-sm text-gray-600">
              <span>
                Page {page} of {totalPages} ({totalCount} total)
              </span>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page === 1}
                  onClick={() => setPage((p) => p - 1)}
                >
                  <ChevronLeft className="h-4 w-4" />
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages}
                  onClick={() => setPage((p) => p + 1)}
                >
                  Next
                  <ChevronRight className="h-4 w-4" />
                </Button>
              </div>
            </div>
          )}
        </div>
      </DashboardLayout>
    </PermissionGuard>
  );
}
