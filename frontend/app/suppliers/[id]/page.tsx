'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import {
  SupplierForm,
  SupplierOrdersList,
  SupplierStatusBadge,
} from '@/components/suppliers';
import { Button, Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { usePermissions, useSupplier, useSuppliers } from '@/hooks';
import { formatDate } from '@/utils/formatters';

export default function SupplierDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const { supplier, isLoading } = useSupplier(params?.id);
  const { updateSupplier, deleteSupplier, isUpdating, isDeleting } = useSuppliers();

  if (isLoading || !supplier) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canUpdate = hasAnyPermission(['supplier.update', 'update_supplier']);
  const canDelete = true;

  return (
    <DashboardLayout>
      <PermissionGuard permission={['supplier.view', 'view_supplier', 'supplier.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{supplier.company_name}</h1>
              <p className="text-gray-600 mt-1">Supplier profile and procurement history</p>
            </div>
            <SupplierStatusBadge status={String(supplier.status)} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Supplier Details</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Company Name</p>
                <p className="font-medium text-gray-900">{supplier.company_name}</p>
              </div>
              <div>
                <p className="text-gray-500">Contact Person</p>
                <p className="font-medium text-gray-900">{supplier.contact_person || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Email</p>
                <p className="font-medium text-gray-900">{supplier.email}</p>
              </div>
              <div>
                <p className="text-gray-500">Phone</p>
                <p className="font-medium text-gray-900">{supplier.phone}</p>
              </div>
              <div>
                <p className="text-gray-500">Registration Number</p>
                <p className="font-medium text-gray-900">{supplier.registration_number || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Tax Number</p>
                <p className="font-medium text-gray-900">{supplier.tax_number || '-'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Address</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{supplier.address || '-'}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Notes</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{supplier.notes || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Created Date</p>
                <p className="font-medium text-gray-900">{formatDate(supplier.created_at)}</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Related Procurement Orders</CardTitle>
            </CardHeader>
            <CardContent>
              <SupplierOrdersList supplierId={supplier.id} />
            </CardContent>
          </Card>

          {canUpdate ? (
            <Card>
              <CardHeader>
                <CardTitle>Edit Supplier</CardTitle>
              </CardHeader>
              <CardContent>
                <SupplierForm
                  initialValues={supplier}
                  submitText="Update Supplier"
                  isSubmitting={isUpdating}
                  onSubmit={async (values) => {
                    try {
                      await updateSupplier({ id: supplier.id, payload: values });
                    } catch {
                      // Errors are already surfaced by useApi mutation toast.
                    }
                  }}
                  onCancel={() => router.push('/suppliers')}
                />
              </CardContent>
            </Card>
          ) : null}

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push('/suppliers')}>
              Back to List
            </Button>
            {canDelete ? (
              <Button
                variant="destructive"
                isLoading={isDeleting}
                onClick={async () => {
                  if (!window.confirm(`Delete supplier \"${supplier.company_name}\"?`)) return;
                  try {
                    await deleteSupplier(supplier.id);
                    router.push('/suppliers');
                  } catch {
                    // Errors are already surfaced by useApi mutation toast.
                  }
                }}
              >
                Delete Supplier
              </Button>
            ) : null}
          </div>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
