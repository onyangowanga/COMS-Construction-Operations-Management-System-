// ============================================================================
// PROJECTS PAGE
// Project list and management
// ============================================================================

'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Edit, Eye, Plus, Trash2 } from 'lucide-react';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProjectProgressBar, ProjectStatusBadge } from '@/components/projects';
import { DashboardLayout } from '@/components/layout';
import {
  Button,
  Card,
  CardContent,
  CardHeader,
  CardTitle,
  ConfirmDialog,
  DataTable,
  Input,
  Select,
  type Column,
} from '@/components/ui';
import { usePermissions, useProjects } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { Project } from '@/types';

export default function ProjectsPage() {
  const router = useRouter();
  const { hasPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('name');
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<Project | null>(null);

  const { projects, totalCount, isLoading, isDeleting, deleteProject } = useProjects({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering,
  });

  const canView = hasPermission('project.view');

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  const handleDelete = async () => {
    if (!deleteTarget) {
      return;
    }

    await deleteProject(deleteTarget.id);
    setDeleteTarget(null);
  };

  const columns: Column<Project>[] = [
    {
      key: 'name',
      title: 'Project Name',
      sortable: true,
    },
    {
      key: 'client_name',
      title: 'Client',
      sortable: true,
      render: (_, row) => row.client_name || row.client,
    },
    {
      key: 'contract_value',
      title: 'Contract Value',
      sortable: true,
      render: (value) => formatCurrency(value || 0),
    },
    {
      key: 'start_date',
      title: 'Start Date',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'end_date',
      title: 'End Date',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'status',
      title: 'Status',
      sortable: true,
      render: (value) => <ProjectStatusBadge status={value} />,
    },
    {
      key: 'completion_percentage',
      title: 'Completion %',
      sortable: true,
      render: (value: number) => <ProjectProgressBar value={value} />,
      width: '220px',
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '180px',
      render: (_, row) => (
        <div className="flex items-center gap-2" onClick={(event) => event.stopPropagation()}>
          <PermissionGuard permission="view_project">
            <Button
              variant="ghost"
              size="sm"
              leftIcon={<Eye className="h-4 w-4" />}
              onClick={() => router.push(`/projects/${row.id}`)}
            >
              View
            </Button>
          </PermissionGuard>

          <PermissionGuard permission="edit_project">
            <Button
              variant="outline"
              size="sm"
              leftIcon={<Edit className="h-4 w-4" />}
              onClick={() => router.push(`/projects/${row.id}/edit`)}
            >
              Edit
            </Button>
          </PermissionGuard>

          <PermissionGuard permission="delete_project">
            <Button
              variant="destructive"
              size="sm"
              leftIcon={<Trash2 className="h-4 w-4" />}
              onClick={() => setDeleteTarget(row)}
            >
              Delete
            </Button>
          </PermissionGuard>
        </div>
      ),
    },
  ];

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Projects</h1>
            <p className="text-gray-600 mt-1">Manage all construction projects</p>
          </div>
          <PermissionGuard permission="create_project">
            <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/projects/create')}>
              New Project
            </Button>
          </PermissionGuard>
        </div>

        {/* Projects Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
              <Input
                placeholder="Search by project name"
                value={search}
                onChange={(event) => {
                  setPage(1);
                  setSearch(event.target.value);
                }}
              />

              <Select
                value={status}
                onChange={(event) => {
                  setPage(1);
                  setStatus(event.target.value);
                }}
                options={[
                  { value: '', label: 'All statuses' },
                  { value: 'planning', label: 'Planning' },
                  { value: 'active', label: 'Active' },
                  { value: 'on_hold', label: 'On Hold' },
                  { value: 'completed', label: 'Completed' },
                  { value: 'cancelled', label: 'Cancelled' },
                ]}
              />

              <Select
                value={ordering}
                onChange={(event) => {
                  setPage(1);
                  setOrdering(event.target.value);
                }}
                options={[
                  { value: 'name', label: 'Sort: Name (A-Z)' },
                  { value: '-name', label: 'Sort: Name (Z-A)' },
                  { value: 'contract_value', label: 'Sort: Value (Low-High)' },
                  { value: '-contract_value', label: 'Sort: Value (High-Low)' },
                  { value: 'start_date', label: 'Sort: Start Date (Oldest)' },
                  { value: '-start_date', label: 'Sort: Start Date (Newest)' },
                ]}
              />
            </div>

            <DataTable
              data={projects}
              columns={columns}
              searchable={false}
              onRowClick={(project) => {
                if (canView) {
                  router.push(`/projects/${project.id}`);
                }
              }}
              isLoading={isLoading}
              emptyMessage="No projects found. Create your first project to get started."
            />

            <div className="flex items-center justify-between mt-4">
              <p className="text-sm text-gray-500">
                Page {page} of {totalPages} ({totalCount} total projects)
              </p>

              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page <= 1 || isLoading}
                  onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                >
                  Previous
                </Button>
                <Button
                  variant="outline"
                  size="sm"
                  disabled={page >= totalPages || isLoading}
                  onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                >
                  Next
                </Button>
              </div>
            </div>
          </CardContent>
        </Card>

        <ConfirmDialog
          isOpen={!!deleteTarget}
          onClose={() => setDeleteTarget(null)}
          onConfirm={handleDelete}
          title="Delete Project"
          message={`Are you sure you want to delete "${deleteTarget?.name || 'this project'}"? This action cannot be undone.`}
          confirmText="Delete"
          variant="destructive"
          isLoading={isDeleting}
        />
      </div>
    </DashboardLayout>
  );
}
