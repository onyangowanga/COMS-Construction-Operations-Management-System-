'use client';

import React from 'react';
import { NotificationItem } from './NotificationItem';
import type { Notification } from '@/types';
import { cn } from '@/utils/helpers';

// --------------------------------------------------------------------------
// Skeleton
// --------------------------------------------------------------------------

function NotificationSkeleton() {
  return (
    <div className="flex items-start gap-3 px-4 py-3">
      <div className="h-9 w-9 rounded-full bg-gray-200 animate-pulse shrink-0" />
      <div className="flex-1 space-y-2">
        <div className="h-3 w-3/4 rounded bg-gray-200 animate-pulse" />
        <div className="h-3 w-1/2 rounded bg-gray-200 animate-pulse" />
      </div>
    </div>
  );
}

// --------------------------------------------------------------------------
// Component
// --------------------------------------------------------------------------

interface NotificationListProps {
  notifications: Notification[];
  isLoading?: boolean;
  onMarkAsRead?: (id: string) => void;
  compact?: boolean;
  emptyMessage?: string;
}

export function NotificationList({
  notifications,
  isLoading,
  onMarkAsRead,
  compact = false,
  emptyMessage = 'No notifications',
}: NotificationListProps) {
  if (isLoading) {
    return (
      <div className="divide-y divide-gray-100">
        {Array.from({ length: compact ? 3 : 5 }).map((_, i) => (
          <NotificationSkeleton key={i} />
        ))}
      </div>
    );
  }

  if (notifications.length === 0) {
    return (
      <div className={cn('px-4 text-center text-gray-500', compact ? 'py-6' : 'py-12')}>
        <p className="text-sm">{emptyMessage}</p>
      </div>
    );
  }

  return (
    <div className={cn('divide-y divide-gray-100', compact && 'divide-y-0')}>
      {notifications.map((n) => (
        <NotificationItem
          key={n.id}
          notification={n}
          onMarkAsRead={onMarkAsRead}
          compact={compact}
        />
      ))}
    </div>
  );
}
