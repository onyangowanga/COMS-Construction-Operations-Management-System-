'use client';

import React, { useState } from 'react';
import { Bell } from 'lucide-react';
import { NotificationDropdown } from './NotificationDropdown';
import { useNotifications } from '@/hooks';
import { cn } from '@/utils/helpers';

export function NotificationBell() {
  const [open, setOpen] = useState(false);
  const { unreadCount } = useNotifications({ page: 1, page_size: 1 });

  return (
    <div className="relative">
      <button
        aria-label="Notifications"
        onClick={() => setOpen((prev) => !prev)}
        className={cn(
          'relative p-2 text-gray-600 hover:text-gray-900 hover:bg-gray-100 rounded-lg transition-colors',
          open && 'bg-gray-100 text-gray-900'
        )}
      >
        <Bell className="h-5 w-5" />
        {unreadCount > 0 && (
          <span className="absolute top-1 right-1 h-4 w-4 bg-red-500 text-white text-[10px] font-bold rounded-full flex items-center justify-center leading-none">
            {unreadCount > 9 ? '9+' : unreadCount}
          </span>
        )}
      </button>

      {open && <NotificationDropdown onClose={() => setOpen(false)} />}
    </div>
  );
}
