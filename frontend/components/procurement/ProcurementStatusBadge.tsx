import React from 'react';
import { Badge } from '@/components/ui';
import { ProcurementOrderStatus } from '@/types';

interface ProcurementStatusBadgeProps {
  status: string;
}

const variantMap: Record<string, 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary'> = {
  [ProcurementOrderStatus.DRAFT]:               'default',
  [ProcurementOrderStatus.APPROVED]:            'primary',
  [ProcurementOrderStatus.ISSUED]:              'warning',
  [ProcurementOrderStatus.PARTIALLY_DELIVERED]: 'warning',
  [ProcurementOrderStatus.DELIVERED]:           'success',
  [ProcurementOrderStatus.INVOICED]:            'secondary',
  [ProcurementOrderStatus.PAID]:                'success',
  [ProcurementOrderStatus.CANCELLED]:           'destructive',
};

export function ProcurementStatusBadge({ status }: ProcurementStatusBadgeProps) {
  const normalized = String(status || '').toUpperCase();
  return <Badge variant={variantMap[normalized] || 'default'}>{normalized.replace('_', ' ')}</Badge>;
}
