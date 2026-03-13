import React from 'react';
import { Badge } from '@/components/ui';
import { ClaimStatus } from '@/types';

interface ClaimStatusBadgeProps {
  status: string;
}

const variantMap: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [ClaimStatus.DRAFT]: 'default',
  [ClaimStatus.SUBMITTED]: 'warning',
  [ClaimStatus.CERTIFIED]: 'success',
  [ClaimStatus.REJECTED]: 'destructive',
  [ClaimStatus.PAID]: 'primary',
};

export function ClaimStatusBadge({ status }: ClaimStatusBadgeProps) {
  return <Badge variant={variantMap[status] || 'default'}>{status.replace('_', ' ')}</Badge>;
}
