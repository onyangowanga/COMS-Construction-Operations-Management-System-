'use client';

import React, { useMemo, useState, type ChangeEvent, type MouseEvent } from 'react';
import { useRouter } from 'next/navigation';
import { BarChart3, Eye, Plus, Trash2 } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { Button, Card, CardContent, CardHeader, CardTitle, DataTable, Input, Select, type Column } from '@/components/ui';
import { useReports } from '@/hooks';
import { formatDate } from '@/utils/formatters';
import type { Report } from '@/types';

export default function ReportsPage() {
  const router = useRouter();
  const [search, setSearch] = useState('');
  const [reportType, setReportType] = useState('');
  const [ordering, setOrdering] = useState('-created_at');
  const [page, setPage] = useState(1);

  const { reports, totalCount, isLoading, isDeleting, deleteReport } = useReports({
    page,
    page_size: 10,
    search: search || undefined,
    report_type: reportType || undefined,
    ordering,
  });

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  const columns: Column<Report>[] = [
    { key: 'code', title: 'Code', sortable: true },
    { key: 'name', title: 'Name', sortable: true },
    { key: 'module', title: 'Module', sortable: true },
    { key: 'report_type', title: 'Type', sortable: true },
    {
      key: 'created_at',
      title: 'Created',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (_, row) => (
        <div className="flex items-center gap-2" onClick={(event: MouseEvent<HTMLDivElement>) => event.stopPropagation()}>
          <Button
            variant="ghost"
            size="sm"
            leftIcon={<Eye className="h-4 w-4" />}
            onClick={() => router.push(`/reports/${row.id}`)}
          >
            View
          </Button>
          <Button
            variant="destructive"
            size="sm"
            leftIcon={<Trash2 className="h-4 w-4" />}
            onClick={async () => {
              if (!window.confirm(`Delete report \"${row.name}\"?`)) {
                return;
              }

              await deleteReport(row.id);
            }}
          >
            Delete
          </Button>
        </div>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_report', 'report.view', 'create_report']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Reports</h1>
              <p className="text-gray-600 mt-1">Build and manage advanced reporting assets.</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" leftIcon={<BarChart3 className="h-5 w-5" />} onClick={() => router.push('/reports/dashboard')}>
                Dashboard
              </Button>
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/reports/create')}>
                New Report
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Report Builder Library</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search reports"
                  value={search}
                  onChange={(event: ChangeEvent<HTMLInputElement>) => {
                    setPage(1);
                    setSearch(event.target.value);
                  }}
                />

                <Select
                  value={reportType}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                    setPage(1);
                    setReportType(event.target.value);
                  }}
                  options={[
                    { value: '', label: 'All report types' },
                    { value: 'TABLE', label: 'Table' },
                    { value: 'SUMMARY', label: 'Summary' },
                    { value: 'CHART', label: 'Chart' },
                    { value: 'CUSTOM', label: 'Custom' },
                  ]}
                />

                <Select
                  value={ordering}
                  onChange={(event: ChangeEvent<HTMLSelectElement>) => {
                    setPage(1);
                    setOrdering(event.target.value);
                  }}
                  options={[
                    { value: '-created_at', label: 'Newest first' },
                    { value: 'created_at', label: 'Oldest first' },
                    { value: 'name', label: 'Name (A-Z)' },
                    { value: '-name', label: 'Name (Z-A)' },
                    { value: 'code', label: 'Code (A-Z)' },
                  ]}
                />
              </div>

              <DataTable
                data={reports}
                columns={columns}
                isLoading={isLoading || isDeleting}
                searchable={false}
                onRowClick={(report) => router.push(`/reports/${report.id}`)}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total reports)
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1 || isLoading}
                    onClick={() => setPage((prev: number) => Math.max(1, prev - 1))}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages || isLoading}
                    onClick={() => setPage((prev: number) => Math.min(totalPages, prev + 1))}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
