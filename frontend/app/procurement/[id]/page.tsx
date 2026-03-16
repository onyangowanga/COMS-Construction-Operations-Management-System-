'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import {
  ProcurementFinancialSummary,
  ProcurementStatusBadge,
  ProcurementTimeline,
} from '@/components/procurement';
import { Button, Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { usePermissions, useProcurement, useProcurementOrder } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function ProcurementDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const { order, isLoading } = useProcurementOrder(params?.id);
  const { submitOrder, approveOrder, closeOrder, isSubmitting, isApproving, isClosing } = useProcurement();

  if (isLoading || !order) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canSubmit = hasAnyPermission(['procurement.create', 'procurement.submit', 'submit_procurement_order']);
  const canApprove = hasAnyPermission(['procurement.approve', 'approve_procurement', 'approve_procurement_order']);
  const canClose = hasAnyPermission(['procurement.approve', 'procurement.close', 'close_procurement_order']);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['procurement.view', 'view_procurement', 'view_procurement_order', 'procurement.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{order.reference_number}</h1>
              <p className="text-gray-600 mt-1">Procurement order details and workflow</p>
            </div>
            <ProcurementStatusBadge status={String(order.status)} />
          </div>

          <div className="flex items-center gap-2">
            {canSubmit ? (
              <Button onClick={() => submitOrder(order.id)} isLoading={isSubmitting}>
                Submit
              </Button>
            ) : null}
            {canApprove ? (
              <Button variant="primary" onClick={() => approveOrder(order.id)} isLoading={isApproving}>
                Approve
              </Button>
            ) : null}
            {canClose ? (
              <Button variant="secondary" onClick={() => closeOrder(order.id)} isLoading={isClosing}>
                Close
              </Button>
            ) : null}
            <Button variant="outline" onClick={() => router.push('/procurement')}>
              Back to List
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Order Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Project</p>
                <p className="font-medium text-gray-900">{order.project_name || order.project}</p>
              </div>
              <div>
                <p className="text-gray-500">Supplier</p>
                <p className="font-medium text-gray-900">{order.supplier_name || order.supplier}</p>
              </div>
              <div>
                <p className="text-gray-500">Order Value</p>
                <p className="font-medium text-gray-900">{formatCurrency(order.order_value || 0)}</p>
              </div>
              <div>
                <p className="text-gray-500">Delivery Date</p>
                <p className="font-medium text-gray-900">{order.delivery_date ? formatDate(order.delivery_date) : '-'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Description</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{order.description || '-'}</p>
              </div>
            </CardContent>
          </Card>

          <ProcurementFinancialSummary order={order} />

          <Card>
            <CardHeader>
              <CardTitle>Workflow Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ProcurementTimeline order={order} />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
