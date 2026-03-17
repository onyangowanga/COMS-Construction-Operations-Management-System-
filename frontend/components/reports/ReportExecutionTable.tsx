'use client';

import React from 'react';
import { DataTable, type Column } from '@/components/ui';
import { formatDate } from '@/utils/formatters';
import type { ReportExecution } from '@/types';

interface ReportExecutionTableProps {
  executions: ReportExecution[];
  isLoading?: boolean;
}

export function ReportExecutionTable({ executions, isLoading = false }: ReportExecutionTableProps) {
  const columns: Column<ReportExecution>[] = [
    {
      key: 'status',
      title: 'Status',
      sortable: true,
    },
    {
      key: 'export_format',
      title: 'Format',
      sortable: true,
    },
    {
      key: 'row_count',
      title: 'Rows',
      sortable: true,
      render: (value) => value ?? '-',
    },
    {
      key: 'duration',
      title: 'Duration',
      sortable: true,
      render: (value, row) => `${value ?? row.execution_time ?? 0}s`,
    },
    {
      key: 'created_at',
      title: 'Executed At',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'error_message',
      title: 'Error',
      render: (value) => value || '-',
      width: '320px',
    },
  ];

  return (
    <DataTable
      data={executions}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No executions yet"
    />
  );
}
