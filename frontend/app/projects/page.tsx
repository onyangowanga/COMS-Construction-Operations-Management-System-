// ============================================================================
// PROJECTS PAGE
// Project list and management
// ============================================================================

'use client';

import React, { useState } from 'react';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { Card, CardHeader, CardTitle, CardContent, Button, DataTable, Badge, type Column } from '@/components/ui';
import { useProjects } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';
import type { Project } from '@/types';

export default function ProjectsPage() {
  const { projects, isLoading } = useProjects();
  const [selectedProject, setSelectedProject] = useState<Project | null>(null);

  const columns: Column<Project>[] = [
    {
      key: 'project_code',
      title: 'Code',
      sortable: true,
      width: '120px',
    },
    {
      key: 'name',
      title: 'Project Name',
      sortable: true,
    },
    {
      key: 'client_name',
      title: 'Client',
      sortable: true,
    },
    {
      key: 'status',
      title: 'Status',
      sortable: true,
      render: (value) => (
        <Badge
          variant={
            value === 'active'
              ? 'success'
              : value === 'completed'
              ? 'primary'
              : value === 'on_hold'
              ? 'warning'
              : 'default'
          }
        >
          {value?.replace('_', ' ')}
        </Badge>
      ),
    },
    {
      key: 'contract_value',
      title: 'Contract Value',
      sortable: true,
      render: (value) => formatCurrency(value),
    },
    {
      key: 'start_date',
      title: 'Start Date',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'completion_percentage',
      title: 'Progress',
      render: (value: number) => (
        <div className="flex items-center gap-2">
          <div className="w-24 h-2 bg-gray-200 rounded-full overflow-hidden">
            <div
              className="h-full bg-primary-600"
              style={{ width: `${value || 0}%` }}
            />
          </div>
          <span className="text-sm text-gray-600">{value || 0}%</span>
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
          <Button leftIcon={<Plus className="h-5 w-5" />}>
            New Project
          </Button>
        </div>

        {/* Projects Table */}
        <Card>
          <CardHeader>
            <CardTitle>All Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <DataTable
              data={projects}
              columns={columns}
              searchable
              searchPlaceholder="Search projects..."
              onRowClick={(project) => setSelectedProject(project)}
              isLoading={isLoading}
              emptyMessage="No projects found. Create your first project to get started."
            />
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
