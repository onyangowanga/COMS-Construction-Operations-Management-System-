'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import type { Activity } from '@/types';
import { ActivityItem } from './ActivityItem';

interface ActivityFeedProps {
  activities: Activity[];
  isLoading?: boolean;
  title?: string;
  emptyMessage?: string;
}

function ActivitySkeleton() {
  return (
    <div className="space-y-3">
      {Array.from({ length: 5 }).map((_, index) => (
        <div key={index} className="rounded-lg border border-gray-200 p-3 animate-pulse">
          <div className="flex items-start gap-3">
            <div className="h-9 w-9 rounded-full bg-gray-200 shrink-0" />
            <div className="flex-1 space-y-2">
              <div className="h-4 w-4/5 bg-gray-200 rounded" />
              <div className="h-3 w-2/5 bg-gray-100 rounded" />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}

export function ActivityFeed({
  activities,
  isLoading = false,
  title = 'Global Activity Timeline',
  emptyMessage = 'No activity found for the selected filters.',
}: ActivityFeedProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>{title}</CardTitle>
      </CardHeader>
      <CardContent>
        {isLoading ? <ActivitySkeleton /> : null}

        {!isLoading && activities.length === 0 ? (
          <div className="rounded-lg border border-dashed border-gray-300 bg-gray-50 p-8 text-center">
            <p className="text-sm text-gray-600">{emptyMessage}</p>
          </div>
        ) : null}

        {!isLoading && activities.length > 0 ? (
          <div className="space-y-3">
            {activities.map((activity) => (
              <ActivityItem key={activity.id} activity={activity} />
            ))}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
