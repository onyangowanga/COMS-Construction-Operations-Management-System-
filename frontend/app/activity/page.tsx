'use client';

import React, { useMemo, useState } from 'react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ActivityFeed, ActivityFilters, type ActivityFilterValues } from '@/components/activity';
import { Button } from '@/components/ui';
import { useActivity } from '@/hooks';

const initialFilters: ActivityFilterValues = {
  module: '',
  event_type: '',
  start_date: '',
  end_date: '',
};

export default function ActivityPage() {
  const [filters, setFilters] = useState<ActivityFilterValues>(initialFilters);
  const [page, setPage] = useState(1);

  const queryParams = useMemo(
    () => ({
      page,
      page_size: 15,
      ordering: '-timestamp',
      module: filters.module || undefined,
      event_type: filters.event_type || undefined,
      start_date: filters.start_date || undefined,
      end_date: filters.end_date || undefined,
    }),
    [filters, page]
  );

  const { activities, totalCount, isLoading } = useActivity(queryParams);

  const totalPages = Math.max(1, Math.ceil((totalCount || 0) / 15));

  const handleFilterChange = (nextValues: ActivityFilterValues) => {
    setPage(1);
    setFilters(nextValues);
  };

  const handleReset = () => {
    setPage(1);
    setFilters(initialFilters);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['activity.view', 'view_activity']}>
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Activity Timeline</h1>
            <p className="text-gray-600 mt-1">Track system-wide actions across contracts, projects, and operations modules.</p>
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-4 gap-6">
            <div className="lg:col-span-1">
              <ActivityFilters values={filters} onChange={handleFilterChange} onReset={handleReset} />
            </div>

            <div className="lg:col-span-3 space-y-4">
              <ActivityFeed activities={activities} isLoading={isLoading} />

              <div className="flex items-center justify-between">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total events)
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
            </div>
          </div>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
