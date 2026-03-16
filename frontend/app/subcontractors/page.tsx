'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { SubcontractorTable } from '@/components/subcontractors';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';
import { usePermissions, useSubcontractors } from '@/hooks';

export default function SubcontractorsPage() {
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('-created_at');
  const [page, setPage] = useState(1);

  const { subcontractors, totalCount, isLoading } = useSubcontractors({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering,
  });

  const canCreate = hasAnyPermission(['subcontractor.create', 'create_subcontractor', 'create_subcontract']);
  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['subcontractor.view', 'view_subcontractor', 'view_subcontract', 'subcontractor.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Subcontractors</h1>
              <p className="text-gray-600 mt-1">Manage subcontractor registry and assignments.</p>
            </div>
            {canCreate ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/subcontractors/create')}>
                New Subcontractor
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Subcontractor Register</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search subcontractors"
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
                    { value: 'SUSPENDED', label: 'Suspended' },
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
                    { value: 'company_name', label: 'Company (A-Z)' },
                    { value: '-company_name', label: 'Company (Z-A)' },
                  ]}
                />
              </div>

              <SubcontractorTable
                subcontractors={subcontractors}
                isLoading={isLoading}
                onView={(subcontractor) => router.push(`/subcontractors/${subcontractor.id}`)}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total subcontractors)
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
