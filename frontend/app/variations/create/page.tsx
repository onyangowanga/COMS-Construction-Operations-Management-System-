'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { VariationForm } from '@/components/variations';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useVariations } from '@/hooks';
import type { VariationFormInput } from '@/types';

export default function CreateVariationPage() {
  const router = useRouter();
  const { createVariation, isCreating } = useVariations();

  const handleSubmit = async (values: VariationFormInput) => {
    const created = await createVariation(values);
    router.push(`/variations/${created.id}`);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission="create_variation">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Create Variation</h1>
            <p className="text-gray-600 mt-1">Register a new variation order request.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Variation Details</CardTitle>
            </CardHeader>
            <CardContent>
              <VariationForm
                onSubmit={handleSubmit}
                onCancel={() => router.push('/variations')}
                submitText="Create Variation"
                isSubmitting={isCreating}
              />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
