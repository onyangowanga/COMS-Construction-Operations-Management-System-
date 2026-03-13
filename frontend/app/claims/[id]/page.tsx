'use client';

import React, { useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ClaimFinancialSummary, ClaimStatusBadge, ClaimTimeline } from '@/components/claims';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, LoadingSpinner, Modal, Textarea } from '@/components/ui';
import { useClaim, useClaims, usePermissions } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

export default function ClaimDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasPermission } = usePermissions();
  const { claim, isLoading } = useClaim(params?.id);
  const { submitClaim, certifyClaim, rejectClaim, isSubmitting, isCertifying, isRejecting } = useClaims();

  const [certifyOpen, setCertifyOpen] = useState(false);
  const [rejectOpen, setRejectOpen] = useState(false);
  const [certifiedAmount, setCertifiedAmount] = useState('');
  const [rejectionReason, setRejectionReason] = useState('');

  if (isLoading || !claim) {
    return (
      <DashboardLayout>
        <div className="py-20 flex justify-center">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
    );
  }

  const canSubmit = hasPermission('create_claim') && claim.status === 'DRAFT';
  const canCertify = hasPermission('certify_claim');
  const canReject = hasPermission('approve_claim') || hasPermission('certify_claim');

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_claim', 'view_claims', 'create_claim', 'certify_claim', 'approve_claim']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{claim.claim_number}</h1>
              <p className="text-gray-600 mt-1">Claim details and certification workflow</p>
            </div>
            <ClaimStatusBadge status={claim.status} />
          </div>

          <div className="flex items-center gap-2">
            {canSubmit ? (
              <Button onClick={() => submitClaim(claim.id)} isLoading={isSubmitting}>
                Submit Claim
              </Button>
            ) : null}
            {canCertify ? (
              <Button variant="primary" onClick={() => setCertifyOpen(true)}>
                Certify
              </Button>
            ) : null}
            {canReject ? (
              <Button variant="destructive" onClick={() => setRejectOpen(true)}>
                Reject
              </Button>
            ) : null}
            <Button variant="outline" onClick={() => router.push('/claims')}>
              Back to List
            </Button>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Claim Information</CardTitle>
            </CardHeader>
            <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
              <div>
                <p className="text-gray-500">Project</p>
                <p className="font-medium text-gray-900">{claim.project_name || claim.project}</p>
              </div>
              <div>
                <p className="text-gray-500">Claim Amount</p>
                <p className="font-medium text-gray-900">{formatCurrency(claim.claim_amount || claim.gross_amount || 0)}</p>
              </div>
              <div>
                <p className="text-gray-500">Certified Amount</p>
                <p className="font-medium text-gray-900">{formatCurrency(claim.certified_amount || 0)}</p>
              </div>
              <div>
                <p className="text-gray-500">Submission Date</p>
                <p className="font-medium text-gray-900">{formatDate(claim.submitted_date || claim.created_at)}</p>
              </div>
              <div className="md:col-span-2">
                <p className="text-gray-500">Description</p>
                <p className="font-medium text-gray-900 whitespace-pre-line">{claim.description || claim.notes || '-'}</p>
              </div>
            </CardContent>
          </Card>

          <ClaimFinancialSummary claim={claim} />

          <Card>
            <CardHeader>
              <CardTitle>Claim Timeline</CardTitle>
            </CardHeader>
            <CardContent>
              <ClaimTimeline claim={claim} />
            </CardContent>
          </Card>
        </div>

        <Modal
          isOpen={certifyOpen}
          onClose={() => setCertifyOpen(false)}
          title="Certify Claim"
          footer={
            <>
              <Button variant="outline" onClick={() => setCertifyOpen(false)} disabled={isCertifying}>
                Cancel
              </Button>
              <Button
                onClick={async () => {
                  await certifyClaim({
                    id: claim.id,
                    certified_amount: certifiedAmount || String(claim.claim_amount || claim.gross_amount || 0),
                  });
                  setCertifyOpen(false);
                }}
                isLoading={isCertifying}
              >
                Certify
              </Button>
            </>
          }
        >
          <Input
            label="Certified Amount"
            type="number"
            step="0.01"
            value={certifiedAmount}
            onChange={(event) => setCertifiedAmount(event.target.value)}
            placeholder={String(claim.claim_amount || claim.gross_amount || 0)}
          />
        </Modal>

        <Modal
          isOpen={rejectOpen}
          onClose={() => setRejectOpen(false)}
          title="Reject Claim"
          footer={
            <>
              <Button variant="outline" onClick={() => setRejectOpen(false)} disabled={isRejecting}>
                Cancel
              </Button>
              <Button
                variant="destructive"
                onClick={async () => {
                  await rejectClaim({ id: claim.id, reason: rejectionReason || 'Rejected' });
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
