import React from 'react';
import { Card, CardContent } from '@/components/ui';

interface ProjectMetricsCardProps {
  title: string;
  value: string;
  subtitle?: string;
  icon?: React.ReactNode;
}

export function ProjectMetricsCard({ title, value, subtitle, icon }: ProjectMetricsCardProps) {
  return (
    <Card>
      <CardContent className="pt-6">
        <div className="flex items-start justify-between">
          <div>
            <p className="text-sm text-gray-600">{title}</p>
            <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
            {subtitle ? <p className="text-xs text-gray-500 mt-2">{subtitle}</p> : null}
          </div>
          {icon ? <div className="text-primary-600">{icon}</div> : null}
        </div>
      </CardContent>
    </Card>
  );
}
