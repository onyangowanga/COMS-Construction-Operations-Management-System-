'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import {
  SubcontractorFinancialSummary,
  SubcontractorForm,
  SubcontractorProjectsList,
  SubcontractorStatusBadge,
} from '@/components/subcontractors';
import { Button, Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { usePermissions, useSubcontractor, useSubcontractors } from '@/hooks';

export default function SubcontractorDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const { subcontractor, isLoading } = useSubcontractor(params?.id);
  const { updateSubcontractor, deleteSubcontractor, isUpdating, isDeleting } = useSubcontractors();

  if (isLoading || !subcontractor) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canUpdate = hasAnyPermission(['subcontractor.update', 'update_subcontractor', 'update_subcontract']);
  const canDelete = hasAnyPermission(['subcontractor.delete', 'delete_subcontractor', 'delete_subcontract']);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['subcontractor.view', 'view_subcontractor', 'view_subcontract', 'subcontractor.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{subcontractor.company_name}</h1>
              <p className="text-gray-600 mt-1">Subcontractor profile and assignments</p>
            </div>
            <SubcontractorStatusBadge status={String(subcontractor.status)} />
          </div>

          <SubcontractorFinancialSummary subcontractor={subcontractor} />

          <Card>
            <CardHeader>
              <CardTitle>Assigned Projects</CardTitle>
            </CardHeader>
            <CardContent>
              <SubcontractorProjectsList subcontractor={subcontractor} />
            </CardContent>
          </Card>

          {canUpdate ? (
            <SubcontractorForm
              initialValues={subcontractor}
              isSubmitting={isUpdating}
              onSubmit={async (values) => {
                try {
                  await updateSubcontractor({ id: subcontractor.id, payload: values });
                  router.push(`/subcontractors/${subcontractor.id}`);
                } catch {
                  // Errors are already surfaced by useApi mutation toast.
                }
              }}
              onCancel={() => router.push('/subcontractors')}
            />
          ) : null}

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push('/subcontractors')}>
              Back to List
            </Button>
            {canDelete ? (
              <Button
                variant="destructive"
                isLoading={isDeleting}
                onClick={async () => {
                  await deleteSubcontractor(subcontractor.id);
                  router.push('/subcontractors');
                }}
              >
                Delete Subcontractor
              </Button>
            ) : null}
          </div>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
