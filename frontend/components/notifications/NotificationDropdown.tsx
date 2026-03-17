'use client';

import React, { useRef, useEffect } from 'react';
import Link from 'next/link';
import { CheckCheck } from 'lucide-react';
import { NotificationList } from './NotificationList';
import { Button } from '@/components/ui';
import { useNotifications } from '@/hooks';

interface NotificationDropdownProps {
  onClose: () => void;
}

export function NotificationDropdown({ onClose }: NotificationDropdownProps) {
  const ref = useRef<HTMLDivElement>(null);

  const { notifications, isLoading, markAsRead, markAllAsRead, isMarkingAllRead } =
    useNotifications({ page: 1, page_size: 10 });

  // Close when clicking outside
  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) {
        onClose();
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, [onClose]);

  const unread = notifications.filter((n) => !n.is_read);

  return (
    <div
      ref={ref}
      className="absolute right-0 mt-2 w-96 bg-white rounded-xl shadow-xl border border-gray-200 z-50 overflow-hidden"
    >
      {/* Header */}
      <div className="flex items-center justify-between px-4 py-3 border-b border-gray-200">
        <h3 className="font-semibold text-gray-900">Notifications</h3>
        {unread.length > 0 && (
          <Button
            variant="ghost"
            size="sm"
            onClick={() => markAllAsRead(undefined)}
            disabled={isMarkingAllRead}
            className="text-xs text-primary-600 hover:text-primary-800 flex items-center gap-1 px-2"
          >
            <CheckCheck className="h-3.5 w-3.5" />
            Mark all as read
          </Button>
        )}
      </div>

      {/* List */}
      <div className="max-h-[400px] overflow-y-auto">
        <NotificationList
          notifications={notifications}
          isLoading={isLoading}
          onMarkAsRead={(id) => markAsRead(id)}
          compact
          emptyMessage="You're all caught up!"
        />
      </div>

      {/* Footer */}
      <div className="px-4 py-3 border-t border-gray-200 bg-gray-50">
        <Link
          href="/notifications"
          onClick={onClose}
          className="block text-center text-sm font-medium text-primary-700 hover:text-primary-900 transition-colors"
        >
          View all notifications
        </Link>
      </div>
    </div>
  );
}
