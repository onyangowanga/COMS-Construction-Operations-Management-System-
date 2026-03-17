'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ContractTable } from '@/components/contracts';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';
import { useContracts, usePermissions } from '@/hooks';
import type { Contract } from '@/types';

export default function ContractsPage() {
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('contract_number');
  const [page, setPage] = useState(1);

  const { contracts, totalCount, isLoading, deleteContract, isDeleting } = useContracts({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering,
  });

  const canCreate = hasAnyPermission(['contract.create', 'create_contract']);
  const canUpdate = hasAnyPermission(['contract.update', 'update_contract']);
  const canDelete = hasAnyPermission(['contract.delete', 'delete_contract']);

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  const handleDelete = async (contract: Contract) => {
    if (!window.confirm(`Delete contract \"${contract.contract_number}\"?`)) return;

    try {
      await deleteContract(contract.id);
    } catch {
      // Errors are already surfaced by useApi mutation toast.
    }
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['contract.view', 'view_contract', 'contract.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Contracts</h1>
              <p className="text-gray-600 mt-1">Manage legal agreements for projects and related workflows.</p>
            </div>
            {canCreate ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/contracts/create')}>
                New Contract
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Contract Register</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search contracts"
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
                    { value: 'ACTIVE', label: 'Active' },
                    { value: 'COMPLETED', label: 'Completed' },
                    { value: 'TERMINATED', label: 'Terminated' },
                  ]}
                />

                <Select
                  value={ordering}
                  onChange={(event) => {
                    setPage(1);
                    setOrdering(event.target.value);
                  }}
                  options={[
                    { value: 'contract_number', label: 'Contract Number (A-Z)' },
                    { value: '-contract_number', label: 'Contract Number (Z-A)' },
                    { value: '-created_at', label: 'Newest first' },
                    { value: 'created_at', label: 'Oldest first' },
                  ]}
                />
              </div>

              <ContractTable
                contracts={contracts}
                isLoading={isLoading || isDeleting}
                canEdit={canUpdate}
                canDelete={canDelete}
                onView={(contract) => router.push(`/contracts/${contract.id}`)}
                onEdit={(contract) => router.push(`/contracts/${contract.id}`)}
                onDelete={handleDelete}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total contracts)
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
