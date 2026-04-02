'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { useParams } from 'next/navigation';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProjectDetailTab, ProjectProgressBar, ProjectStatusBadge, ProjectTabs } from '@/components/projects';
import { DashboardLayout } from '@/components/layout';
import { Badge, Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { useProject, useProjectStages } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function ProjectDetailPage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id;
  const [activeTab, setActiveTab] = useState<ProjectDetailTab>('overview');

  const { project, isLoading } = useProject(projectId);
  const { stages } = useProjectStages(projectId);

  const tabContent = useMemo(() => {
    switch (activeTab) {
      case 'overview':
        return (
          <div className="space-y-4">
            <p className="text-gray-700">{project?.description || 'No project description available.'}</p>
            <div>
              <h3 className="text-sm font-semibold text-gray-700 mb-2">Project Stages</h3>
              <div className="space-y-3">
                {stages.length === 0 ? (
                  <p className="text-sm text-gray-500">No stages available yet.</p>
                ) : (
                  stages.map((stage) => (
                    <div key={stage.id} className="p-3 border border-gray-200 rounded-lg">
                      <div className="flex items-center justify-between">
                        <p className="font-medium text-gray-900">{stage.name}</p>
                        <Badge variant={stage.status === 'completed' ? 'success' : stage.status === 'in_progress' ? 'warning' : 'default'}>
                          {stage.status.replace('_', ' ')}
                        </Badge>
                      </div>
                      <p className="text-xs text-gray-500 mt-2">{formatDate(stage.start_date)} - {formatDate(stage.end_date)}</p>
                      <div className="mt-2">
                        <ProjectProgressBar value={stage.completion_percentage} />
                      </div>
                    </div>
                  ))
                )}
              </div>
            </div>
          </div>
        );
      case 'documents':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Documents</p>
            <p className="text-sm text-gray-500 mt-2">Open all documents scoped to this project.</p>
            <Link href={`/documents?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Documents Module
            </Link>
          </div>
        );
      case 'variations':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Variations</p>
            <p className="text-sm text-gray-500 mt-2">View and manage variation orders for this project.</p>
            <Link href={`/variations?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Variations Module
            </Link>
          </div>
        );
      case 'claims':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Claims</p>
            <p className="text-sm text-gray-500 mt-2">Review subcontract claims associated with this project.</p>
            <Link href={`/claims?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Claims Module
            </Link>
          </div>
        );
      case 'procurement':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Procurement</p>
            <p className="text-sm text-gray-500 mt-2">Open procurement and purchase order records for this project.</p>
            <Link href={`/procurement?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Procurement Module
            </Link>
          </div>
        );
      case 'reports':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Reports</p>
            <p className="text-sm text-gray-500 mt-2">Generate reports focused on this project.</p>
            <Link href={`/reports?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Reports Module
            </Link>
          </div>
        );
      case 'activity':
        return (
          <div className="p-6 border border-dashed border-gray-300 rounded-lg bg-gray-50">
            <p className="text-gray-700 font-medium">Activity</p>
            <p className="text-sm text-gray-500 mt-2">Open project activity timeline.</p>
            <Link href={`/activity?project=${projectId}`} className="inline-flex mt-3 text-sm font-medium text-primary-700 hover:text-primary-900">
              Open Activity Module
            </Link>
          </div>
        );
      default:
        return null;
    }
  }, [activeTab, project?.description, stages]);

  return (
    <DashboardLayout>
      <PermissionGuard
        permission="view_project"
        fallback={
          <Card>
            <CardContent>
              <p className="text-gray-600">You do not have permission to view project details.</p>
            </CardContent>
          </Card>
        }
      >
        {isLoading || !project ? (
          <div className="py-20 flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{project.name}</h1>
                <p className="text-gray-600 mt-1">Project Details and Status Tracking</p>
              </div>
              <Link href={`/projects/${project.id}/dashboard`} className="text-sm font-medium text-primary-700 hover:text-primary-900">
                Open Project Dashboard
              </Link>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Project Summary</CardTitle>
              </CardHeader>
              <CardContent className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
                <div>
                  <p className="text-xs uppercase text-gray-500">Client</p>
                  <p className="font-medium text-gray-900">{project.client_name || project.client}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-gray-500">Contract Value</p>
                  <p className="font-medium text-gray-900">{formatCurrency(project.contract_value || 0)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-gray-500">Project Manager</p>
                  <p className="font-medium text-gray-900">{project.project_manager_name || project.project_manager || 'Not assigned'}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-gray-500">Start Date</p>
                  <p className="font-medium text-gray-900">{formatDate(project.start_date)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-gray-500">End Date</p>
                  <p className="font-medium text-gray-900">{formatDate(project.end_date)}</p>
                </div>
                <div>
                  <p className="text-xs uppercase text-gray-500">Status</p>
                  <ProjectStatusBadge status={project.status} />
                </div>
                <div className="lg:col-span-3">
                  <p className="text-xs uppercase text-gray-500 mb-2">Completion</p>
                  <ProjectProgressBar value={project.completion_percentage || 0} />
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardContent>
                <ProjectTabs activeTab={activeTab} onChange={setActiveTab} />
                <div className="pt-4">{tabContent}</div>
              </CardContent>
            </Card>
          </div>
        )}
      </PermissionGuard>
    </DashboardLayout>
  );
}
