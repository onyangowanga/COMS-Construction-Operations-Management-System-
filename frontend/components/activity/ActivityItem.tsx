'use client';

import React from 'react';
import Link from 'next/link';
import {
  Activity as ActivityIcon,
  FileText,
  FolderKanban,
  FileStack,
  GitBranch,
  Receipt,
  ShoppingCart,
  Users,
} from 'lucide-react';
import type { Activity } from '@/types';
import { formatRelativeTime } from '@/utils/formatters';
import { cn } from '@/utils/helpers';

const moduleMeta: Record<string, { icon: React.ComponentType<{ className?: string }>; color: string; path: (id: string) => string }> = {
  CONTRACT: { icon: FileText, color: 'bg-blue-100 text-blue-700', path: (id) => `/contracts/${id}` },
  PROJECT: { icon: FolderKanban, color: 'bg-indigo-100 text-indigo-700', path: (id) => `/projects/${id}` },
  DOCUMENT: { icon: FileStack, color: 'bg-gray-100 text-gray-700', path: (id) => `/documents/${id}` },
  VARIATION: { icon: GitBranch, color: 'bg-purple-100 text-purple-700', path: (id) => `/variations/${id}` },
  CLAIM: { icon: Receipt, color: 'bg-yellow-100 text-yellow-700', path: (id) => `/claims/${id}` },
  PROCUREMENT: { icon: ShoppingCart, color: 'bg-teal-100 text-teal-700', path: (id) => `/procurement/${id}` },
  SUPPLIER: { icon: Users, color: 'bg-green-100 text-green-700', path: (id) => `/suppliers/${id}` },
  SUBCONTRACTOR: { icon: Users, color: 'bg-orange-100 text-orange-700', path: (id) => `/subcontractors/${id}` },
};

function getModuleMeta(module: string) {
  return moduleMeta[String(module || '').toUpperCase()] || {
    icon: ActivityIcon,
    color: 'bg-gray-100 text-gray-700',
    path: (id: string) => `/dashboard?entity_id=${id}`,
  };
}

interface ActivityItemProps {
  activity: Activity;
}

export function ActivityItem({ activity }: ActivityItemProps) {
  const normalizedModule = String(activity.module || '').toUpperCase();
  const meta = getModuleMeta(normalizedModule);
  const Icon = meta.icon;
  const href = meta.path(String(activity.entity_id || ''));

  return (
    <Link href={href} className="block rounded-lg border border-gray-200 p-3 hover:border-primary-300 hover:bg-primary-50/30 transition-colors">
      <div className="flex items-start gap-3">
        <div className={cn('h-9 w-9 rounded-full flex items-center justify-center shrink-0', meta.color)}>
          <Icon className="h-4 w-4" />
        </div>

        <div className="min-w-0 flex-1">
          <p className="text-sm text-gray-900 leading-6">
            {activity.description}{' '}
            <span className="font-semibold text-primary-700">{activity.entity_reference}</span>
          </p>
          <p className="text-xs text-gray-500 mt-1">
            by {activity.performed_by || 'System'} • {formatRelativeTime(activity.timestamp)}
          </p>
        </div>
      </div>
    </Link>
  );
}
