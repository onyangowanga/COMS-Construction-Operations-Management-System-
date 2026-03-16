'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { SupplierTable } from '@/components/suppliers';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';
import { usePermissions, useSuppliers } from '@/hooks';
import type { Supplier } from '@/types';

export default function SuppliersPage() {
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('company_name');
  const [page, setPage] = useState(1);

  const { suppliers, totalCount, isLoading, deleteSupplier, isDeleting } = useSuppliers({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering: ordering === 'company_name' ? 'name' : ordering === '-company_name' ? '-name' : ordering,
  });

  const canCreate = hasAnyPermission(['supplier.create', 'create_supplier']);
  const canUpdate = hasAnyPermission(['supplier.update', 'update_supplier']);
  const canDelete = true;

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  const handleDelete = async (supplier: Supplier) => {
    if (!window.confirm(`Delete supplier \"${supplier.company_name}\"?`)) return;
    try {
      await deleteSupplier(supplier.id);
    } catch {
      // Errors are already surfaced by useApi mutation toast.
    }
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['supplier.view', 'view_supplier', 'supplier.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Suppliers</h1>
              <p className="text-gray-600 mt-1">Manage suppliers used for procurement orders.</p>
            </div>
            {canCreate ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/suppliers/create')}>
                New Supplier
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Supplier Register</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search suppliers"
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
                    { value: 'ACTIVE', label: 'Active' },
                    { value: 'INACTIVE', label: 'Inactive' },
                  ]}
                />

                <Select
                  value={ordering}
                  onChange={(event) => {
                    setPage(1);
                    setOrdering(event.target.value);
                  }}
                  options={[
                    { value: 'company_name', label: 'Company (A-Z)' },
                    { value: '-company_name', label: 'Company (Z-A)' },
                    { value: '-created_at', label: 'Newest first' },
                    { value: 'created_at', label: 'Oldest first' },
                  ]}
                />
              </div>

              <SupplierTable
                suppliers={suppliers}
                isLoading={isLoading || isDeleting}
                canEdit={canUpdate}
                canDelete={canDelete}
                onView={(supplier) => router.push(`/suppliers/${supplier.id}`)}
                onEdit={(supplier) => router.push(`/suppliers/${supplier.id}`)}
                onDelete={handleDelete}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total suppliers)
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
