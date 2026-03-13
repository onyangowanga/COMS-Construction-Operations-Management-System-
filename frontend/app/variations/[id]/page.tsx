'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import {
  VariationFinancialSummary,
  VariationStatusBadge,
  VariationStatusTimeline,
} from '@/components/variations';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, LoadingSpinner, Modal, Textarea } from '@/components/ui';
import { usePermissions, useVariation, useVariations } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function VariationDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasPermission } = usePermissions();
  const { variation, isLoading } = useVariation(params?.id);
  const { submitVariation, approveVariation, rejectVariation, isSubmitting, isApproving, isRejecting } = useVariations();

  const [approveOpen, setApproveOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [approvedValue, setApprovedValue] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  if (isLoading || !variation) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canSubmit = hasPermission('create_variation') && variation.status === 'DRAFT';
  const canApprove = hasPermission('approve_variation');
  const canReject = hasPermission('reject_variation');

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_variation', 'view_variations', 'create_variation', 'approve_variation', 'reject_variation']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{variation.reference_number || variation.title}</h1>
              <p className="text-gray-600 mt-1">Variation order details and workflow</p>
            </div>
            <VariationStatusBadge status={variation.status} />
          </div>

          <div className="flex items-center gap-2">
            {canSubmit ? (
              <Button onClick={() => submitVariation(variation.id)} isLoading={isSubmitting}>
                Submit Variation
              </Button>
            ) : null}
            {canApprove ? (
              <Button variant="primary" onClick={() => setApproveOpen(true)}>
                Approve
              </Button>
            ) : null}
            {canReject ? (
              <Button variant="destructive" onClick={() => setRejectOpen(true)}>
                Reject
              </Button>
            ) : null}
            <Button variant="outline" onClick={() => router.push('/variations')}>
              Back to List
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Variation Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Project</p>
                <p className="font-medium text-gray-900">
                  {variation.project_name || (typeof variation.project === 'object' ? variation.project.name : variation.project)}
                </p>
              </div>
              <div>
                <p className="text-gray-500">Estimated Value</p>
                <p className="font-medium text-gray-900">{formatCurrency(variation.estimated_value || 0)}</p>
              </div>
              <div>
                <p className="text-gray-500">Created Date</p>
                <p className="font-medium text-gray-900">{formatDate(variation.created_at)}</p>
              </div>
              <div>
                <p className="text-gray-500">Priority</p>
                <p className="font-medium text-gray-900">{variation.priority_display || variation.priority}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Description</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{variation.description}</p>
              </div>
            </CardContent>
          </Card>

          <VariationFinancialSummary variation={variation} />

          <Card>
            <CardHeader>
              <CardTitle>Status Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <VariationStatusTimeline variation={variation} />
            </CardContent>
          </Card>
        </div>

        <Modal
          isOpen={approveOpen}
          onClose={() => setApproveOpen(false)}
          title="Approve Variation"
          footer={
            <>
              <Button variant="outline" onClick={() => setApproveOpen(false)} disabled={isApproving}>
                Cancel
              </Button>
              <Button
                onClick={async () => {
                  await approveVariation({
                    id: variation.id,
                    approved_value: approvedValue || String(variation.estimated_value || 0),
                  });
                  setApproveOpen(false);
                }}
                isLoading={isApproving}
              >
                Approve
              </Button>
            </>
          }
        >
          <Input
            label="Approved Value"
            type="number"
            step="0.01"
            value={approvedValue}
            onChange={(event) => setApprovedValue(event.target.value)}
            placeholder={String(variation.estimated_value || 0)}
          />
        </Modal>

        <Modal
          isOpen={rejectOpen}
          onClose={() => setRejectOpen(false)}
          title="Reject Variation"
          footer={
            <>
              <Button variant="outline" onClick={() => setRejectOpen(false)} disabled={isRejecting}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={async () => {
                  await rejectVariation({ id: variation.id, reason: rejectionReason || 'Rejected' });
                  setRejectOpen(false);
                }}
                isLoading={isRejecting}
              >
                Reject
              </Button>
            </>
          }
        >
          <Textarea
            label="Rejection Reason"
            rows={4}
            value={rejectionReason}
            onChange={(event) => setRejectionReason(event.target.value)}
            placeholder="Enter reason for rejection"
          />
        </Modal>
      </PermissionGuard>
    </DashboardLayout>
  );
}
