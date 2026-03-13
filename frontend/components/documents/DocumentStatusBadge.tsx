import React from 'react';
import { Badge } from '@/components/ui';

interface DocumentStatusBadgeProps {
  status?: string;
  isApproved?: boolean;
}

export function DocumentStatusBadge({ status, isApproved }: DocumentStatusBadgeProps) {
  const normalized = (status || '').toUpperCase();

  if (normalized === 'APPROVED' || isApproved) {
    return <Badge variant="success">Approved</Badge>;
  }

  if (normalized === 'REJECTED') {
    return <Badge variant="destructive">Rejected</Badge>;
  }

  return <Badge variant="warning">Pending</Badge>;
}
