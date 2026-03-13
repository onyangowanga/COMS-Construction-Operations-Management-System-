import React from 'react';
import { Badge } from '@/components/ui';
import { ProjectStatus } from '@/types';

interface ProjectStatusBadgeProps {
  status: string;
}

const STATUS_LABELS: Record<string, string> = {
  [ProjectStatus.PLANNING]: 'Planning',
  [ProjectStatus.ACTIVE]: 'Active',
  [ProjectStatus.ON_HOLD]: 'On Hold',
  [ProjectStatus.COMPLETED]: 'Completed',
  [ProjectStatus.CANCELLED]: 'Cancelled',
};

const STATUS_VARIANTS: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [ProjectStatus.PLANNING]: 'default',
  [ProjectStatus.ACTIVE]: 'success',
  [ProjectStatus.ON_HOLD]: 'warning',
  [ProjectStatus.COMPLETED]: 'primary',
  [ProjectStatus.CANCELLED]: 'destructive',
};

export function ProjectStatusBadge({ status }: ProjectStatusBadgeProps) {
  return (
    <Badge variant={STATUS_VARIANTS[status] || 'default'}>
      {STATUS_LABELS[status] || status}
    </Badge>
  );
}
