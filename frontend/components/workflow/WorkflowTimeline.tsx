'use client';

import React from 'react';
import { Card, CardContent, CardHeader, CardTitle, Badge } from '@/components/ui';
import type { WorkflowHistoryItem } from '@/types/workflow';
import { formatDate } from '@/utils/formatters';

interface WorkflowTimelineProps {
  history: WorkflowHistoryItem[];
}

export function WorkflowTimeline({ history }: WorkflowTimelineProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Workflow Timeline</CardTitle>
      </CardHeader>
      <CardContent>
        {history.length === 0 ? (
          <p className="text-sm text-gray-500">No transition history yet.</p>
        ) : (
          <div className="space-y-4">
            {history.map((item) => (
              <div key={item.id} className="border-l-2 border-gray-200 pl-4">
                <div className="flex flex-wrap items-center gap-2">
                  <Badge variant="outline">{item.action}</Badge>
                  <span className="text-sm text-gray-700">
                    {item.from_state || 'N/A'} → {item.to_state || 'N/A'}
                  </span>
                </div>
                <p className="text-xs text-gray-500 mt-1">
                  {item.performed_by || 'System'} • {formatDate(item.timestamp)}
                </p>
                {item.comment ? <p className="text-sm text-gray-700 mt-2">{item.comment}</p> : null}
              </div>
            ))}
          </div>
        )}
      </CardContent>
    </Card>
  );
}
