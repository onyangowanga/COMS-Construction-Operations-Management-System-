'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProcurementForm } from '@/components/procurement';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useProcurement } from '@/hooks';
import type { ProcurementOrderFormInput } from '@/types';

export default function CreateProcurementPage() {
  const router = useRouter();
  const { createOrder, isCreating } = useProcurement();

  const handleSubmit = async (values: ProcurementOrderFormInput) => {
    const created = await createOrder(values);
    router.push(`/procurement/${created.id}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['procurement.create', 'create_procurement', 'create_procurement_order']}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Procurement Order</h1>
            <p className="text-gray-600 mt-1">Create a new purchase order for a project.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Order Information</CardTitle>
            </CardHeader>
            <CardContent>
              <ProcurementForm
                onSubmit={handleSubmit}
                onCancel={() => router.push('/procurement')}
                submitText="Create Order"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
