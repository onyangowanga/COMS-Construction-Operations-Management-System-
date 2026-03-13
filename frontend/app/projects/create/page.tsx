'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProjectForm } from '@/components/projects';
import { DashboardLayout } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useProjects, useToast } from '@/hooks';
import type { ProjectFormInput } from '@/types';

export default function CreateProjectPage() {
  const router = useRouter();
  const { createProject, isCreating } = useProjects();
  const { success } = useToast();

  const handleCreate = async (values: ProjectFormInput) => {
    const created = await createProject(values);
    success('Project Created', `${created.name} has been created successfully`);
    router.push(`/projects/${created.id}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard
        permission="create_project"
        fallback={
          <Card>
            <CardContent>
              <p className="text-gray-600">You do not have permission to create projects.</p>
            </CardContent>
          </Card>
        }
      >
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Project</h1>
            <p className="text-gray-600 mt-1">Add a new project to the system.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Project Information</CardTitle>
            </CardHeader>
            <CardContent>
              <ProjectForm
                onSubmit={handleCreate}
                onCancel={() => router.push('/projects')}
                submitText="Create Project"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
