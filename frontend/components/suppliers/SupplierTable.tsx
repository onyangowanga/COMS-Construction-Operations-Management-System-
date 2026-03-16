'use client';

import React from 'react';
import { Eye, Pencil, Trash2 } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { SupplierStatusBadge } from './SupplierStatusBadge';
import { formatDate } from '@/utils/formatters';
import type { Supplier } from '@/types';

interface SupplierTableProps {
  suppliers: Supplier[];
  isLoading?: boolean;
  onView: (supplier: Supplier) => void;
  onEdit?: (supplier: Supplier) => void;
  onDelete?: (supplier: Supplier) => void;
  canEdit?: boolean;
  canDelete?: boolean;
}

export function SupplierTable({
  suppliers,
  isLoading,
  onView,
  onEdit,
  onDelete,
  canEdit = false,
  canDelete = false,
}: SupplierTableProps) {
  const columns: Column<Supplier>[] = [
    {
      key: 'company_name',
      title: 'Company Name',
      sortable: true,
      render: (value, row) => value || row.name || '-',
    },
    {
      key: 'contact_person',
      title: 'Contact Person',
      sortable: true,
      render: (value) => value || '-',
    },
    {
      key: 'email',
      title: 'Email',
      sortable: true,
    },
    {
      key: 'phone',
      title: 'Phone',
      sortable: true,
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <SupplierStatusBadge status={value} />,
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
      width: '280px',
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
      data={suppliers}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No suppliers found"
      onRowClick={onView}
    />
  );
}
