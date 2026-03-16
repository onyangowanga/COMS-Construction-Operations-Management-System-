'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { SubcontractorForm } from '@/components/subcontractors';
import { useSubcontractors } from '@/hooks';

export default function CreateSubcontractorPage() {
  const router = useRouter();
  const { createSubcontractor, isCreating } = useSubcontractors();

  return (
    <DashboardLayout>
      <PermissionGuard permission={['subcontractor.create', 'create_subcontractor', 'create_subcontract']}>
        <div className="space-y-6 max-w-4xl mx-auto">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Subcontractor</h1>
            <p className="text-gray-600 mt-1">Add a new subcontractor profile and commercial details.</p>
          </div>

          <SubcontractorForm
            isSubmitting={isCreating}
            onSubmit={async (values) => {
              const created = await createSubcontractor(values as never);
              if (created?.id) {
                router.push(`/subcontractors/${created.id}`);
                return;
              }
              router.push('/subcontractors');
            }}
            onCancel={() => router.push('/subcontractors')}
          />
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
