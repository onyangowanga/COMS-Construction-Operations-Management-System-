'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProcurementTable } from '@/components/procurement';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';
import { usePermissions, useProcurement } from '@/hooks';

export default function ProcurementPage() {
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('-created_at');
  const [page, setPage] = useState(1);

  const { orders, totalCount, isLoading, submitOrder, approveOrder, closeOrder, isSubmitting, isApproving, isClosing } =
    useProcurement({
      page,
      page_size: 10,
      search: search || undefined,
      status: status || undefined,
      ordering,
    });

  const canCreate = hasAnyPermission(['procurement.create', 'create_procurement', 'create_procurement_order']);
  const canSubmit = hasAnyPermission(['procurement.create', 'procurement.submit', 'submit_procurement_order']);
  const canApprove = hasAnyPermission(['procurement.approve', 'approve_procurement', 'approve_procurement_order']);
  const canClose = hasAnyPermission(['procurement.approve', 'procurement.close', 'close_procurement_order']);

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['procurement.view', 'view_procurement', 'view_procurement_order', 'procurement.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Procurement Orders</h1>
              <p className="text-gray-600 mt-1">Track purchasing activities and order workflow.</p>
            </div>
            {canCreate ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/procurement/create')}>
                New Order
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Procurement Register</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search orders"
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
                    { value: 'DRAFT', label: 'Draft' },
                    { value: 'SUBMITTED', label: 'Submitted' },
                    { value: 'APPROVED', label: 'Approved' },
                    { value: 'ORDERED', label: 'Ordered' },
                    { value: 'DELIVERED', label: 'Delivered' },
                    { value: 'CLOSED', label: 'Closed' },
                  ]}
                />

                <Select
                  value={ordering}
                  onChange={(event) => {
                    setPage(1);
                    setOrdering(event.target.value);
                  }}
                  options={[
                    { value: '-created_at', label: 'Newest first' },
                    { value: 'created_at', label: 'Oldest first' },
                    { value: '-order_value', label: 'Value high-low' },
                    { value: 'order_value', label: 'Value low-high' },
                  ]}
                />
              </div>

              <ProcurementTable
                orders={orders}
                isLoading={isLoading || isSubmitting || isApproving || isClosing}
                canSubmit={canSubmit}
                canApprove={canApprove}
                canClose={canClose}
                onView={(order) => router.push(`/procurement/${order.id}`)}
                onSubmit={(order) => submitOrder(order.id)}
                onApprove={(order) => approveOrder(order.id)}
                onClose={(order) => closeOrder(order.id)}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total orders)
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
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
