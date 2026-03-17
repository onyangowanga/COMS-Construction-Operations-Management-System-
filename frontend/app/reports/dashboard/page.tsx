'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { RefreshCw } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { DashboardWidgetGrid } from '@/components/reports';
import { Button, Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useDashboardWidgets } from '@/hooks';

export default function ReportsDashboardPage() {
  const router = useRouter();
  const { widgets, isLoading, refetch } = useDashboardWidgets();

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_report', 'report.view']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Reporting Dashboard</h1>
              <p className="text-gray-600 mt-1">KPI analytics and widget-driven operational insights.</p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={() => router.push('/reports')}>
                Back to Reports
              </Button>
              <Button variant="outline" leftIcon={<RefreshCw className="h-4 w-4" />} onClick={() => void refetch()}>
                Refresh
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Dashboard Widgets</CardTitle>
            </CardHeader>
            <CardContent>
              <DashboardWidgetGrid widgets={widgets} isLoading={isLoading} />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
