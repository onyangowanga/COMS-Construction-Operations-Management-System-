'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import type { DashboardWidgetData } from '@/types';

interface DashboardWidgetGridProps {
  widgets: DashboardWidgetData[];
  isLoading?: boolean;
}

function renderValue(value: unknown) {
  if (value == null) {
    return '-';
  }

  if (typeof value === 'object') {
    return JSON.stringify(value);
  }

  return String(value);
}

export function DashboardWidgetGrid({ widgets, isLoading = false }: DashboardWidgetGridProps) {
  const router = useRouter();

  const handleDrilldown = (item: DashboardWidgetData) => {
    const drilldown = item.data?.drilldown;
    if (!drilldown?.route) {
      return;
    }

    const searchParams = new URLSearchParams();
    if (drilldown.report_id) {
      searchParams.set('report_id', drilldown.report_id);
    }

    if (drilldown.filters && typeof drilldown.filters === 'object') {
      Object.entries(drilldown.filters).forEach(([key, value]) => {
        if (value != null) {
          searchParams.set(key, String(value));
        }
      });
    }

    const queryString = searchParams.toString();
    router.push(queryString ? `${drilldown.route}?${queryString}` : drilldown.route);
  };

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {Array.from({ length: 4 }).map((_, index) => (
          <Card key={index}>
            <CardContent>
              <div className="animate-pulse h-20 bg-gray-100 rounded" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      {widgets.map((item) => (
        <Card
          key={item.widget.id}
          className={item.data?.drilldown?.route ? 'cursor-pointer transition-shadow hover:shadow-md' : undefined}
          onClick={() => handleDrilldown(item)}
        >
          <CardHeader className="pb-2">
            <CardTitle className="text-base">{item.widget.name}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-semibold text-gray-900">{renderValue(item.data?.value)}</div>
            <p className="text-xs text-gray-500 mt-1">
              {item.widget.widget_type} / {item.widget.data_source}
            </p>
            {item.data?.source_report_name ? (
              <p className="text-xs text-primary-600 mt-2">Open {item.data.source_report_name}</p>
            ) : null}
          </CardContent>
        </Card>
      ))}

      {widgets.length === 0 ? (
        <Card className="md:col-span-2 xl:col-span-4">
          <CardContent>
            <p className="text-gray-600">No dashboard widgets configured yet.</p>
          </CardContent>
        </Card>
      ) : null}
    </div>
  );
}
