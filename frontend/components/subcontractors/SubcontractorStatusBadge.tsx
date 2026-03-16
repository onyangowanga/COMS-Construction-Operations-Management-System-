import React from 'react';
import { Badge } from '@/components/ui';
import { SubcontractorStatus } from '@/types';

interface SubcontractorStatusBadgeProps {
  status: string;
}

const variantMap: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [SubcontractorStatus.ACTIVE]: 'success',
  [SubcontractorStatus.INACTIVE]: 'secondary',
  [SubcontractorStatus.SUSPENDED]: 'destructive',
};

export function SubcontractorStatusBadge({ status }: SubcontractorStatusBadgeProps) {
  const normalized = String(status || '').toUpperCase();
  return <Badge variant={variantMap[normalized] || 'default'}>{normalized.replace('_', ' ')}</Badge>;
}
