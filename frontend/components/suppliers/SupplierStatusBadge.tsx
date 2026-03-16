import React from 'react';
import { Badge } from '@/components/ui';
import { SupplierStatus } from '@/types';

interface SupplierStatusBadgeProps {
  status: string;
}

const variantMap: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [SupplierStatus.ACTIVE]: 'success',
  [SupplierStatus.INACTIVE]: 'secondary',
};

export function SupplierStatusBadge({ status }: SupplierStatusBadgeProps) {
  const normalized = String(status || '').toUpperCase();
  return <Badge variant={variantMap[normalized] || 'default'}>{normalized.replace('_', ' ')}</Badge>;
}
