'use client';

import React from 'react';
import { cn } from '@/utils/helpers';

export type ProjectDetailTab =
  | 'overview'
  | 'documents'
  | 'variations'
  | 'claims'
  | 'procurement'
  | 'reports'
  | 'activity';

interface ProjectTabsProps {
  activeTab: ProjectDetailTab;
  onChange: (tab: ProjectDetailTab) => void;
}

const tabs: Array<{ key: ProjectDetailTab; label: string }> = [
  { key: 'overview', label: 'Overview' },
  { key: 'documents', label: 'Documents' },
  { key: 'variations', label: 'Variations' },
  { key: 'claims', label: 'Claims' },
  { key: 'procurement', label: 'Procurement' },
  { key: 'reports', label: 'Reports' },
  { key: 'activity', label: 'Activity' },
];

export function ProjectTabs({ activeTab, onChange }: ProjectTabsProps) {
  return (
    <div className="border-b border-gray-200 overflow-x-auto">
      <div className="flex gap-1 min-w-max">
        {tabs.map((tab) => (
          <button
            key={tab.key}
            type="button"
            onClick={() => onChange(tab.key)}
            className={cn(
              'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors',
              activeTab === tab.key
                ? 'text-primary-700 border-primary-600'
                : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
            )}
          >
            {tab.label}
          </button>
        ))}
      </div>
    </div>
  );
}
