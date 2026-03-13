'use client';

import React from 'react';
import { Eye } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { VariationStatusBadge } from './VariationStatusBadge';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { VariationOrder } from '@/types';

interface VariationTableProps {
  variations: VariationOrder[];
  isLoading?: boolean;
  onView: (variation: VariationOrder) => void;
}

export function VariationTable({ variations, isLoading, onView }: VariationTableProps) {
  const columns: Column<VariationOrder>[] = [
    {
      key: 'reference_number',
      title: 'Reference Number',
      sortable: true,
      render: (value, row) => value || row.variation_number || 'Pending Reference',
    },
    {
      key: 'project_name',
      title: 'Project',
      sortable: true,
      render: (value, row) => value || (typeof row.project === 'object' ? row.project.name : row.project),
    },
    {
      key: 'description',
      title: 'Description',
      render: (value) => <span className="line-clamp-2">{value}</span>,
    },
    {
      key: 'estimated_value',
      title: 'Variation Value',
      sortable: true,
      render: (value) => formatCurrency(value || 0),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <VariationStatusBadge status={value} />,
    },
    {
      key: 'created_by',
      title: 'Created By',
      render: (_value, row) => row.created_by?.full_name || row.requested_by_name || 'System',
    },
    {
      key: 'created_at',
      title: 'Created Date',
      sortable: true,
      render: (value) => formatDate(value),
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
      data={variations}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No variations found"
      onRowClick={onView}
    />
  );
}
