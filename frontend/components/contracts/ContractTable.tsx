'use client';

import React from 'react';
import { Eye, Pencil, Trash2 } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { ContractStatusBadge } from './ContractStatusBadge';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { Contract } from '@/types';

interface ContractTableProps {
  contracts: Contract[];
  isLoading?: boolean;
  onView: (contract: Contract) => void;
  onEdit?: (contract: Contract) => void;
  onDelete?: (contract: Contract) => void;
  canEdit?: boolean;
  canDelete?: boolean;
}

export function ContractTable({
  contracts,
  isLoading,
  onView,
  onEdit,
  onDelete,
  canEdit = false,
  canDelete = false,
}: ContractTableProps) {
  const columns: Column<Contract>[] = [
    {
      key: 'contract_number',
      title: 'Contract Number',
      sortable: true,
    },
    {
      key: 'project_name',
      title: 'Project Name',
      sortable: true,
    },
    {
      key: 'client',
      title: 'Client',
      sortable: true,
    },
    {
      key: 'contract_value',
      title: 'Contract Value',
      sortable: true,
      render: (value, row) => formatCurrency(Number(value || 0), row.currency || 'KES'),
    },
    {
      key: 'start_date',
      title: 'Start Date',
      sortable: true,
      render: (value) => formatDate(String(value || '')),
    },
    {
      key: 'end_date',
      title: 'End Date',
      sortable: true,
      render: (value) => formatDate(String(value || '')),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <ContractStatusBadge status={String(value)} />,
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '260px',
      render: (_value, row) => (
        <div className="flex flex-wrap items-center gap-2" onClick={(event) => event.stopPropagation()}>
          <Button variant="ghost" size="sm" leftIcon={<Eye className="h-4 w-4" />} onClick={() => onView(row)}>
            View
          </Button>
          {canEdit && onEdit ? (
            <Button variant="outline" size="sm" leftIcon={<Pencil className="h-4 w-4" />} onClick={() => onEdit(row)}>
              Edit
            </Button>
          ) : null}
          {canDelete && onDelete ? (
            <Button variant="destructive" size="sm" leftIcon={<Trash2 className="h-4 w-4" />} onClick={() => onDelete(row)}>
              Delete
            </Button>
          ) : null}
        </div>
      ),
    },
  ];

  return (
    <DataTable
      data={contracts}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No contracts found"
      onRowClick={onView}
    />
  );
}
