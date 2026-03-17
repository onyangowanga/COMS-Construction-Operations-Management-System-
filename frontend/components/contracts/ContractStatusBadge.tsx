'use client';

import React from 'react';
import { Badge } from '@/components/ui';
import { ContractStatus } from '@/types';

interface ContractStatusBadgeProps {
  status: string;
}

const variantByStatus: Record<string, 'secondary' | 'primary' | 'success' | 'destructive'> = {
  [ContractStatus.DRAFT]: 'secondary',
  [ContractStatus.ACTIVE]: 'primary',
  [ContractStatus.COMPLETED]: 'success',
  [ContractStatus.TERMINATED]: 'destructive',
};

export function ContractStatusBadge({ status }: ContractStatusBadgeProps) {
  const normalized = String(status || ContractStatus.DRAFT).toUpperCase();
  const variant = variantByStatus[normalized] || 'secondary';

  return (
    <Badge variant={variant} size="sm">
      {normalized.replace('_', ' ')}
    </Badge>
  );
}
