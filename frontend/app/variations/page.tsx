'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { VariationTable } from '@/components/variations';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';
import { useDrilldownFilter, usePermissions, useVariations } from '@/hooks';

export default function VariationsPage() {
  const router = useRouter();
  const drilldown = useDrilldownFilter();
  const { hasPermission } = usePermissions();
  const [search, setSearch] = useState(drilldown.search);
  const [status, setStatus] = useState(drilldown.status);
  const [showDrilldownBanner, setShowDrilldownBanner] = useState(drilldown.isDrilldown);
  const [ordering, setOrdering] = useState('-created_at');
  const [page, setPage] = useState(1);

  const { variations, totalCount, isLoading } = useVariations({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering,
  });

  const canCreate = hasPermission('create_variation');
  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_variation', 'view_variations', 'create_variation', 'approve_variation', 'reject_variation']}>
        <div className="space-y-6">
          {showDrilldownBanner && drilldown.reportId && (
            <div className="flex items-center justify-between rounded-lg border border-blue-200 bg-blue-50 px-4 py-3 text-sm text-blue-800">
              <span>
                <strong>Filtered view</strong> — showing results from a dashboard report.{' '}
                <a href={`/reports/${drilldown.reportId}`} className="underline hover:text-blue-600">View report</a>
              </span>
              <button type="button" className="ml-4 text-blue-600 hover:text-blue-800" onClick={() => setShowDrilldownBanner(false)} aria-label="Dismiss">×</button>
            </div>
          )}

          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Variation Orders</h1>
              <p className="text-gray-600 mt-1">Create and track project variation orders.</p>
            </div>
            {canCreate ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/variations/create')}>
                New Variation
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Variation Register</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search variations"
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
                    { value: 'SUBMITTED', label: 'Submitted' },
                    { value: 'APPROVED', label: 'Approved' },
                    { value: 'REJECTED', label: 'Rejected' },
                    { value: 'INVOICED', label: 'Invoiced' },
                    { value: 'PAID', label: 'Paid' },
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
                    { value: '-estimated_value', label: 'Value high-low' },
                    { value: 'estimated_value', label: 'Value low-high' },
                  ]}
                />
              </div>

              <VariationTable
                variations={variations}
                isLoading={isLoading}
                onView={(variation) => router.push(`/variations/${variation.id}`)}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total variations)
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
