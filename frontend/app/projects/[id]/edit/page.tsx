'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProjectForm } from '@/components/projects';
import { DashboardLayout } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { useProject, useProjects, useToast } from '@/hooks';
import type { ProjectFormInput } from '@/types';

export default function EditProjectPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const projectId = params?.id;

  const { project, isLoading } = useProject(projectId);
  const { updateProject, isUpdating } = useProjects();
  const { success } = useToast();

  const handleUpdate = async (values: ProjectFormInput) => {
    if (!projectId) return;

    await updateProject({ id: projectId, data: values });
    success('Project Updated', 'Project details were updated successfully');
    router.push(`/projects/${projectId}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard
        permission="project.update"
        fallback={
          <Card>
            <CardContent>
              <p className="text-gray-600">You do not have permission to update projects.</p>
            </CardContent>
          </Card>
        }
      >
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Edit Project</h1>
            <p className="text-gray-600 mt-1">Update project details.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Project Information</CardTitle>
            </CardHeader>
            <CardContent>
              {isLoading || !project ? (
                <div className="py-10 flex justify-center">
                  <LoadingSpinner size="lg" />
                </div>
              ) : (
                <ProjectForm
                  initialValues={project}
                  onSubmit={handleUpdate}
                  onCancel={() => router.push(`/projects/${projectId}`)}
                  submitText="Save Changes"
                  isSubmitting={isUpdating}
                />
              )}
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
