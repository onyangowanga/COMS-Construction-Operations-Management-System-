'use client';

import React from 'react';
import Link from 'next/link';
import { useRouter } from 'next/navigation';
import {
  FileText,
  FolderKanban,
  FileStack,
  GitBranch,
  Receipt,
  ShoppingCart,
  Users,
  Bell,
  CheckCircle,
  AlertTriangle,
  XCircle,
  Info,
} from 'lucide-react';
import { cn } from '@/utils/helpers';
import { formatRelativeTime } from '@/utils/formatters';
import type { Notification } from '@/types';

// --------------------------------------------------------------------------
// Type → visual config
// --------------------------------------------------------------------------

const typeMeta: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; dot: string }> = {
  INFO:    { icon: Info,          color: 'bg-blue-100 text-blue-700',   dot: 'bg-blue-500' },
  SUCCESS: { icon: CheckCircle,   color: 'bg-green-100 text-green-700', dot: 'bg-green-500' },
  WARNING: { icon: AlertTriangle, color: 'bg-yellow-100 text-yellow-700', dot: 'bg-yellow-500' },
  ERROR:   { icon: XCircle,       color: 'bg-red-100 text-red-700',     dot: 'bg-red-500' },
};

function getTypeMeta(type: string) {
  return typeMeta[String(type || '').toUpperCase()] || typeMeta.INFO;
}

// --------------------------------------------------------------------------
// Module → route resolver
// --------------------------------------------------------------------------

const moduleRoutes: Record<string, (id: string) => string> = {
  CONTRACT:      (id) => `/contracts/${id}`,
  PROJECT:       (id) => `/projects/${id}`,
  DOCUMENT:      (id) => `/documents/${id}`,
  VARIATION:     (id) => `/variations/${id}`,
  CLAIM:         (id) => `/claims/${id}`,
  PROCUREMENT:   (id) => `/procurement/${id}`,
  SUPPLIER:      (id) => `/suppliers/${id}`,
  SUBCONTRACTOR: (id) => `/subcontractors/${id}`,
};

const moduleIcons: Record<string, React.ComponentType<{ className?: string }>> = {
  CONTRACT:      FileText,
  PROJECT:       FolderKanban,
  DOCUMENT:      FileStack,
  VARIATION:     GitBranch,
  CLAIM:         Receipt,
  PROCUREMENT:   ShoppingCart,
  SUPPLIER:      Users,
  SUBCONTRACTOR: Users,
};

function resolveHref(notification: Notification): string {
  if (notification.action_url) return notification.action_url;
  const mod = String(notification.module || '').toUpperCase();
  const id = String(notification.entity_id || '');
  if (id && moduleRoutes[mod]) return moduleRoutes[mod](id);
  return '/notifications';
}

function getModuleIcon(module?: string): React.ComponentType<{ className?: string }> {
  return moduleIcons[String(module || '').toUpperCase()] || Bell;
}

// --------------------------------------------------------------------------
// Component
// --------------------------------------------------------------------------

interface NotificationItemProps {
  notification: Notification;
  onMarkAsRead?: (id: string) => void;
  compact?: boolean;
}

export function NotificationItem({ notification, onMarkAsRead, compact = false }: NotificationItemProps) {
  const router = useRouter();
  const meta = getTypeMeta(notification.type);
  const TypeIcon = meta.icon;
  const ModuleIcon = getModuleIcon(notification.module);
  const href = resolveHref(notification);

  function handleClick(e: React.MouseEvent) {
    e.preventDefault();
    if (!notification.is_read && onMarkAsRead) {
      onMarkAsRead(notification.id);
    }
    router.push(href);
  }

  return (
    <Link
      href={href}
      onClick={handleClick}
      className={cn(
        'flex items-start gap-3 px-4 py-3 hover:bg-gray-50 transition-colors rounded-lg',
        !notification.is_read && 'bg-blue-50/60 hover:bg-blue-50',
        compact && 'py-2'
      )}
    >
      {/* Icon */}
      <div className={cn('h-9 w-9 rounded-full flex items-center justify-center shrink-0', meta.color)}>
        <TypeIcon className="h-4 w-4" />
      </div>

      {/* Content */}
      <div className="min-w-0 flex-1">
        <div className="flex items-start justify-between gap-2">
          <p className={cn('text-sm font-medium text-gray-900 leading-snug', compact && 'text-xs')}>
            {notification.title}
          </p>
          {!notification.is_read && (
            <span className={cn('inline-block h-2 w-2 rounded-full shrink-0 mt-1', meta.dot)} />
          )}
        </div>
        {!compact && (
          <p className="text-xs text-gray-600 mt-0.5 line-clamp-2">{notification.message}</p>
        )}
        <div className="flex items-center gap-2 mt-1">
          {notification.module && (
            <span className="inline-flex items-center gap-1 text-xs text-gray-400">
              <ModuleIcon className="h-3 w-3" />
              {notification.entity_reference || notification.module}
            </span>
          )}
          <span className="text-xs text-gray-400">
            {formatRelativeTime(notification.created_at)}
          </span>
        </div>
      </div>
    </Link>
  );
}
