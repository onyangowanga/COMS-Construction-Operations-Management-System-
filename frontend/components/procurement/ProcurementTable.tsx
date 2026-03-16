'use client';

import React from 'react';
import { Eye, Send, CheckCircle2, Lock } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { ProcurementStatusBadge } from './ProcurementStatusBadge';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { ProcurementOrder } from '@/types';

interface ProcurementTableProps {
  orders: ProcurementOrder[];
  isLoading?: boolean;
  onView: (order: ProcurementOrder) => void;
  onSubmit?: (order: ProcurementOrder) => void;
  onApprove?: (order: ProcurementOrder) => void;
  onClose?: (order: ProcurementOrder) => void;
  canSubmit?: boolean;
  canApprove?: boolean;
  canClose?: boolean;
}

export function ProcurementTable({
  orders,
  isLoading,
  onView,
  onSubmit,
  onApprove,
  onClose,
  canSubmit = false,
  canApprove = false,
  canClose = false,
}: ProcurementTableProps) {
  const columns: Column<ProcurementOrder>[] = [
    { key: 'reference_number', title: 'Reference Number', sortable: true },
    {
      key: 'project_name',
      title: 'Project',
      sortable: true,
      render: (value, row) => value || row.project,
    },
    {
      key: 'supplier_name',
      title: 'Supplier',
      sortable: true,
      render: (value, row) => value || row.supplier,
    },
    {
      key: 'order_value',
      title: 'Order Value',
      sortable: true,
      render: (value) => formatCurrency(value || 0),
    },
    {
      key: 'status',
      title: 'Status',
      render: (value) => <ProcurementStatusBadge status={value} />,
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
      width: '330px',
      render: (_value, row) => (
        <div className="flex flex-wrap items-center gap-2" onClick={(event) => event.stopPropagation()}>
          <Button variant="ghost" size="sm" leftIcon={<Eye className="h-4 w-4" />} onClick={() => onView(row)}>
            View
          </Button>
          {canSubmit && onSubmit ? (
            <Button variant="outline" size="sm" leftIcon={<Send className="h-4 w-4" />} onClick={() => onSubmit(row)}>
              Submit
            </Button>
          ) : null}
          {canApprove && onApprove ? (
            <Button variant="primary" size="sm" leftIcon={<CheckCircle2 className="h-4 w-4" />} onClick={() => onApprove(row)}>
              Approve
            </Button>
          ) : null}
          {canClose && onClose ? (
            <Button variant="secondary" size="sm" leftIcon={<Lock className="h-4 w-4" />} onClick={() => onClose(row)}>
              Close
            </Button>
          ) : null}
        </div>
      ),
    },
  ];

  return (
    <DataTable
      data={orders}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No procurement orders found"
      onRowClick={onView}
    />
  );
}
