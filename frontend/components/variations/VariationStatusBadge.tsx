import React from 'react';
import { Badge } from '@/components/ui';
import { VariationStatus } from '@/types';

interface VariationStatusBadgeProps {
  status: string;
}

const variantMap: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [VariationStatus.DRAFT]: 'default',
  [VariationStatus.SUBMITTED]: 'warning',
  [VariationStatus.APPROVED]: 'success',
  [VariationStatus.REJECTED]: 'destructive',
  [VariationStatus.INVOICED]: 'secondary',
  [VariationStatus.PAID]: 'primary',
};

export function VariationStatusBadge({ status }: VariationStatusBadgeProps) {
  return <Badge variant={variantMap[status] || 'default'}>{status.replace('_', ' ')}</Badge>;
}
