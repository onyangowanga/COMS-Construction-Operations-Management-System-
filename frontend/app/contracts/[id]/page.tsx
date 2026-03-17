'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import {
  ContractForm,
  ContractModulesTabs,
  ContractStatusBadge,
} from '@/components/contracts';
import { Button, Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { useContract, useContracts, usePermissions } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function ContractDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasAnyPermission } = usePermissions();
  const { contract, isLoading } = useContract(params?.id);
  const { updateContract, deleteContract, isUpdating, isDeleting } = useContracts();

  if (isLoading || !contract) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canUpdate = hasAnyPermission(['contract.update', 'update_contract']);
  const canDelete = hasAnyPermission(['contract.delete', 'delete_contract']);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['contract.view', 'view_contract', 'contract.create']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{contract.contract_number}</h1>
              <p className="text-gray-600 mt-1">Contract profile and linked module activity</p>
            </div>
            <ContractStatusBadge status={String(contract.status)} />
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Contract Details</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Contract Number</p>
                <p className="font-medium text-gray-900">{contract.contract_number}</p>
              </div>
              <div>
                <p className="text-gray-500">Project Name</p>
                <p className="font-medium text-gray-900">{contract.project_name}</p>
              </div>
              <div>
                <p className="text-gray-500">Client</p>
                <p className="font-medium text-gray-900">{contract.client}</p>
              </div>
              <div>
                <p className="text-gray-500">Contractor</p>
                <p className="font-medium text-gray-900">{contract.contractor || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Consultant</p>
                <p className="font-medium text-gray-900">{contract.consultant || '-'}</p>
              </div>
              <div>
                <p className="text-gray-500">Contract Value</p>
                <p className="font-medium text-gray-900">{formatCurrency(Number(contract.contract_value || 0), contract.currency || 'KES')}</p>
              </div>
              <div>
                <p className="text-gray-500">Start Date</p>
                <p className="font-medium text-gray-900">{formatDate(contract.start_date)}</p>
              </div>
              <div>
                <p className="text-gray-500">End Date</p>
                <p className="font-medium text-gray-900">{formatDate(contract.end_date || '')}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Description</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{contract.description || '-'}</p>
              </div>
            </CardContent>
          </Card>

          <ContractModulesTabs contractId={contract.id} contractNumber={contract.contract_number} />

          {canUpdate ? (
            <Card>
              <CardHeader>
                <CardTitle>Edit Contract</CardTitle>
              </CardHeader>
              <CardContent>
                <ContractForm
                  initialValues={contract}
                  submitText="Update Contract"
                  isSubmitting={isUpdating}
                  onSubmit={async (values) => {
                    try {
                      await updateContract({ id: contract.id, payload: values });
                    } catch {
                      // Errors are already surfaced by useApi mutation toast.
                    }
                  }}
                  onCancel={() => router.push('/contracts')}
                />
              </CardContent>
            </Card>
          ) : null}

          <div className="flex items-center gap-2">
            <Button variant="outline" onClick={() => router.push('/contracts')}>
              Back to List
            </Button>
            {canDelete ? (
              <Button
                variant="destructive"
                isLoading={isDeleting}
                onClick={async () => {
                  if (!window.confirm(`Delete contract \"${contract.contract_number}\"?`)) return;

                  try {
                    await deleteContract(contract.id);
                    router.push('/contracts');
                  } catch {
                    // Errors are already surfaced by useApi mutation toast.
                  }
                }}
              >
                Delete Contract
              </Button>
            ) : null}
          </div>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
