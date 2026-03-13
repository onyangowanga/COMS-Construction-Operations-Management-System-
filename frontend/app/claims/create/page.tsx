'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ClaimForm } from '@/components/claims';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useClaims } from '@/hooks';
import type { ClaimFormInput } from '@/types';

export default function CreateClaimPage() {
  const router = useRouter();
  const { createClaim, isCreating } = useClaims();

  const handleSubmit = async (values: ClaimFormInput) => {
    const created = await createClaim(values);
    router.push(`/claims/${created.id}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission="create_claim">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Claim</h1>
            <p className="text-gray-600 mt-1">Register a new valuation/claim entry.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Claim Information</CardTitle>
            </CardHeader>
            <CardContent>
              <ClaimForm onSubmit={handleSubmit} onCancel={() => router.push('/claims')} submitText="Create Claim" isSubmitting={isCreating} />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
