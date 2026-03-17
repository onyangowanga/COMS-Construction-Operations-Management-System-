'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ReportBuilderForm } from '@/components/reports';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useReports, useToast } from '@/hooks';
import type { ReportCreatePayload } from '@/types';

export default function CreateReportPage() {
  const router = useRouter();
  const { createReport, isCreating } = useReports();
  const { success } = useToast();

  const handleCreate = async (payload: ReportCreatePayload) => {
    const created = await createReport(payload);
    success('Report Created', `${created.name} has been created successfully`);
    router.push(`/reports/${created.id}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['create_report', 'report.create']}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Report</h1>
            <p className="text-gray-600 mt-1">Build reusable reporting logic with filters, grouping, and KPIs.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Report Builder</CardTitle>
            </CardHeader>
            <CardContent>
              <ReportBuilderForm
                onSubmit={handleCreate}
                onCancel={() => router.push('/reports')}
                submitText="Create Report"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
