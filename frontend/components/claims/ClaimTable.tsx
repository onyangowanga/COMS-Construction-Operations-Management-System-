'use client';

import React from 'react';
import { Eye } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { ClaimStatusBadge } from './ClaimStatusBadge';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { Claim } from '@/types';

interface ClaimTableProps {
  claims: Claim[];
  isLoading?: boolean;
  onView: (claim: Claim) => void;
}

export function ClaimTable({ claims, isLoading, onView }: ClaimTableProps) {
  const columns: Column<Claim>[] = [
    {
      key: 'claim_number',
      title: 'Claim Number',
      sortable: true,
    },
    {
      key: 'project_name',
      title: 'Project',
      sortable: true,
      render: (value) => value || 'N/A',
    },
    {
      key: 'claim_amount',
      title: 'Claim Amount',
      sortable: true,
      render: (value, row) => formatCurrency(value || row.gross_amount || 0),
    },
    {
      key: 'certified_amount',
      title: 'Certified Amount',
      sortable: true,
      render: (value) => formatCurrency(value || 0),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <ClaimStatusBadge status={value} />,
    },
    {
      key: 'submission_date',
      title: 'Submission Date',
      sortable: true,
      render: (_value, row) => formatDate(row.submitted_date || row.created_at),
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '120px',
      render: (_value, row) => (
        <div onClick={(event) => event.stopPropagation()}>
          <Button variant="ghost" size="sm" leftIcon={<Eye className="h-4 w-4" />} onClick={() => onView(row)}>
            View
          </Button>
        </div>
      ),
    },
  ];

  return (
    <DataTable
      data={claims}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No claims found"
      onRowClick={onView}
    />
  );
}
