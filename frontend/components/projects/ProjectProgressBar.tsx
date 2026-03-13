import React from 'react';
import { formatPercentage } from '@/utils/formatters';

interface ProjectProgressBarProps {
  value: number;
}

export function ProjectProgressBar({ value }: ProjectProgressBarProps) {
  const safeValue = Math.max(0, Math.min(100, value || 0));

  return (
    <div className="flex items-center gap-2 min-w-[160px]">
      <div className="h-2 w-full rounded-full bg-gray-200 overflow-hidden">
        <div className="h-full bg-primary-600" style={{ width: `${safeValue}%` }} />
      </div>
      <span className="text-sm text-gray-600 w-12 text-right">{formatPercentage(safeValue, 0)}</span>
    </div>
  );
}
