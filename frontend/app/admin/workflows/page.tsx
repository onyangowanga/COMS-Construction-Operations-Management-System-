'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { DashboardLayout } from '@/components/layout';

interface Workflow {
  id: string;
  name: string;
  module: string;
  states: WorkflowState[];
}

interface WorkflowState {
  id: string;
  name: string;
  is_initial: boolean;
  is_final: boolean;
  transitions: Transition[];
}

interface Transition {
  id: string;
  from_state: string;
  to_state: string;
  name: string;
  allowed_roles: string[];
}

export default function WorkflowsPage() {
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [showModal, setShowModal] = useState(false);

  const { data: workflows, isLoading } = useQuery<Workflow[]>({
    queryKey: ['workflows'],
    queryFn: async () => {
      const res = await fetch('/api/workflows/', { credentials: 'include' });
      return res.json();
    },
  });

  const modules = [...new Set(workflows?.map(w => w.module) || [])];

  if (isLoading) return (
      <DashboardLayout>
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" />
    </div>
      </DashboardLayout>
  );

  return (
    <div>
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Workflow Configuration</h1>
        <p className="text-gray-600">Manage workflow states and transitions for each module</p>
      </div>

      {/* Workflows by Module */}
      <div className="space-y-6">
        {modules.map((module) => {
          const moduleWorkflows = workflows?.filter(w => w.module === module) || [];

          return (
            <div key={module} className="bg-white rounded-lg border p-6">
              <div className="flex items-center justify-between mb-4">
                <h2 className="text-xl font-semibold capitalize">{module} Workflows</h2>
                <Badge variant="primary">{moduleWorkflows.length} workflows</Badge>
              </div>

              <div className="grid grid-cols-1 gap-4">
                {moduleWorkflows.map((workflow) => (
                  <Card key={workflow.id} className="hover:shadow-md transition-shadow cursor-pointer">
                    <div className="p-4" onClick={() => { setSelectedWorkflow(workflow); setShowModal(true); }}>
                      <div className="flex items-center justify-between mb-3">
                        <h3 className="font-semibold text-lg">{workflow.name}</h3>
                        <Button size="sm" variant="outline">View Details</Button>
                      </div>

                      {/* States Preview */}
                      <div className="flex gap-2 flex-wrap">
                        {workflow.states.map((state) => (
                          <div
                            key={state.id}
                            className={`
                              px-3 py-1 rounded text-sm
                              ${state.is_initial ? 'bg-green-100 text-green-800' : ''}
                              ${state.is_final ? 'bg-red-100 text-red-800' : ''}
                              ${!state.is_initial && !state.is_final ? 'bg-gray-100 text-gray-800' : ''}
                            `}
                          >
                            {state.name}
                            {state.is_initial && ' (Initial)'}
                            {state.is_final && ' (Final)'}
                          </div>
                        ))}
                      </div>

                      <div className="text-sm text-gray-500 mt-2">
                        {workflow.states.reduce((acc, s) => acc + s.transitions.length, 0)} transitions defined
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </div>
          );
        })}
      </div>

      {/* Workflow Detail Modal */}
      {showModal && selectedWorkflow && (
        <Modal
          isOpen={showModal && !!selectedWorkflow}
          title={selectedWorkflow.name}
          onClose={() => { setShowModal(false); setSelectedWorkflow(null); }}
        >
          <div className="space-y-6">
            <div>
              <h3 className="font-semibold mb-2">Module</h3>
              <Badge variant="primary">{selectedWorkflow.module}</Badge>
            </div>

            {/* States */}
            <div>
              <h3 className="font-semibold mb-3">States</h3>
              <div className="space-y-3">
                {selectedWorkflow.states.map((state) => (
                  <div key={state.id} className="border rounded-lg p-4">
                    <div className="flex items-center justify-between mb-2">
                      <div className="font-medium">{state.name}</div>
                      <div className="flex gap-2">
                        {state.is_initial && <Badge variant="success">Initial</Badge>}
                        {state.is_final && <Badge variant="destructive">Final</Badge>}
                      </div>
                    </div>

                    {/* Transitions from this state */}
                    {state.transitions.length > 0 && (
                      <div className="mt-3 pl-4 border-l-2 border-blue-200">
                        <div className="text-sm text-gray-600 mb-2">Transitions:</div>
                        {state.transitions.map((trans) => (
                          <div key={trans.id} className="text-sm mb-2 bg-gray-50 p-2 rounded">
                            <div className="font-medium">{trans.name}</div>
                            <div className="text-gray-600">
                              → {selectedWorkflow.states.find(s => s.id === trans.to_state)?.name}
                            </div>
                            <div className="text-xs text-gray-500 mt-1">
                              Allowed roles: {trans.allowed_roles.join(', ') || 'All'}
                            </div>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                ))}
              </div>
            </div>

            {/* Visual Flow */}
            <div>
              <h3 className="font-semibold mb-3">Workflow Flow</h3>
              <div className="bg-gray-50 p-4 rounded-lg">
                <div className="flex items-center gap-2 flex-wrap">
                  {selectedWorkflow.states
                    .sort((a, b) => (a.is_initial ? -1 : b.is_initial ? 1 : 0))
                    .map((state, idx) => (
                      <div key={state.id} className="flex items-center gap-2">
                        <div className={`
                          px-4 py-2 rounded font-medium
                          ${state.is_initial ? 'bg-green-500 text-white' : ''}
                          ${state.is_final ? 'bg-red-500 text-white' : ''}
                          ${!state.is_initial && !state.is_final ? 'bg-blue-500 text-white' : ''}
                        `}>
                          {state.name}
                        </div>
                        {idx < selectedWorkflow.states.length - 1 && (
                          <span className="text-gray-400">→</span>
                        )}
                      </div>
                    ))}
                </div>
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
