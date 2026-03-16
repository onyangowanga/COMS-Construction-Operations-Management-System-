'use client';

import React from 'react';
import { Eye } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { SubcontractorStatusBadge } from './SubcontractorStatusBadge';
import { formatCurrency } from '@/utils/formatters';
import type { Subcontractor } from '@/types';

interface SubcontractorTableProps {
  subcontractors: Subcontractor[];
  isLoading?: boolean;
  onView: (subcontractor: Subcontractor) => void;
}

export function SubcontractorTable({ subcontractors, isLoading, onView }: SubcontractorTableProps) {
  const columns: Column<Subcontractor>[] = [
    {
      key: 'subcontractor_name',
      title: 'Subcontractor Name',
      sortable: true,
      render: (value, row) => value || row.contact_person,
    },
    {
      key: 'company_name',
      title: 'Company',
      sortable: true,
    },
    {
      key: 'specialization',
      title: 'Specialization',
      sortable: true,
    },
    {
      key: 'assigned_projects_count',
      title: 'Assigned Projects',
      sortable: true,
      render: (value, row) => Number(value ?? row.assigned_projects?.length ?? 0),
    },
    {
      key: 'total_contract_value',
      title: 'Total Contract Value',
      sortable: true,
      render: (value) => formatCurrency(value || 0),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <SubcontractorStatusBadge status={value} />,
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
      data={subcontractors}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No subcontractors found"
      onRowClick={onView}
    />
  );
}
