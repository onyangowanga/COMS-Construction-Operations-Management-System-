import React from 'react';
import type { Subcontractor } from '@/types';

interface SubcontractorProjectsListProps {
  subcontractor: Subcontractor;
}

export function SubcontractorProjectsList({ subcontractor }: SubcontractorProjectsListProps) {
  const projects = subcontractor.assigned_projects || [];

  if (projects.length === 0) {
    return <p className="text-sm text-gray-500">No assigned projects yet.</p>;
  }

  return (
    <div className="space-y-2">
      {projects.map((project) => (
        <div key={project.id} className="p-3 border border-gray-200 rounded-lg">
          <p className="font-medium text-gray-900">{project.name}</p>
          <p className="text-xs text-gray-500 mt-1">{project.project_code || 'No code'}</p>
        </div>
      ))}
    </div>
  );
}
