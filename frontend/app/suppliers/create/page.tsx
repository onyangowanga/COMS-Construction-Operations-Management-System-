'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { SupplierForm } from '@/components/suppliers';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useSuppliers } from '@/hooks';
import type { SupplierCreatePayload } from '@/types';

export default function CreateSupplierPage() {
  const router = useRouter();
  const { createSupplier, isCreating } = useSuppliers();

  const handleSubmit = async (values: SupplierCreatePayload) => {
    try {
      const created = await createSupplier(values);
      router.push(`/suppliers/${created.id}`);
    } catch {
      // Errors are already surfaced by useApi mutation toast.
    }
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['supplier.create', 'create_supplier']}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Supplier</h1>
            <p className="text-gray-600 mt-1">Register a supplier for procurement workflows.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Supplier Information</CardTitle>
            </CardHeader>
            <CardContent>
              <SupplierForm
                onSubmit={handleSubmit}
                onCancel={() => router.push('/suppliers')}
                submitText="Create Supplier"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
