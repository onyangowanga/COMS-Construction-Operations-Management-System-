'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ContractForm } from '@/components/contracts';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useContracts } from '@/hooks';
import type { ContractCreatePayload } from '@/types';

export default function CreateContractPage() {
  const router = useRouter();
  const { createContract, isCreating } = useContracts();

  const handleSubmit = async (values: ContractCreatePayload) => {
    try {
      const created = await createContract(values);
      router.push(`/contracts/${created.id}`);
    } catch {
      // Errors are already surfaced by useApi mutation toast.
    }
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['contract.create', 'create_contract']}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Contract</h1>
            <p className="text-gray-600 mt-1">Register a new legal agreement and track linked modules.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Contract Information</CardTitle>
            </CardHeader>
            <CardContent>
              <ContractForm
                onSubmit={handleSubmit}
                onCancel={() => router.push('/contracts')}
                submitText="Create Contract"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
