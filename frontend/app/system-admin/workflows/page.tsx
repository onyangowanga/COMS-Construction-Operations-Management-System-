'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, GitBranch } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';
import { Modal } from '@/components/ui/Modal';

interface Workflow {
  id: string;
  name: string;
  module: string;
  description: string;
  is_active: boolean;
  states?: State[];
  transitions?: Transition[];
}

interface State {
  id: string;
  name: string;
  is_initial: boolean;
  is_final: boolean;
}

interface Transition {
  id: string;
  from_state: string;
  to_state: string;
  allowed_roles: string[];
}

export default function WorkflowsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingWorkflow, setEditingWorkflow] = useState<Workflow | null>(null);
  const [selectedWorkflow, setSelectedWorkflow] = useState<Workflow | null>(null);
  const [showTransitions, setShowTransitions] = useState(false);

  // Fetch workflows
  const { data: workflows = [], isLoading } = useQuery<Workflow[]>({
    queryKey: ['admin-workflows'],
    queryFn: async () => {
      const res = await fetch('/api/workflows/?is_active=true', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch workflows');
      const data = await res.json();
      return Array.isArray(data) ? data : data.results || [];
    },
  });

  // Save workflow mutation
  const saveWorkflowMutation = useMutation({
    mutationFn: async (data: Partial<Workflow>) => {
      const method = editingWorkflow ? 'PATCH' : 'POST';
      const url = editingWorkflow ? `/api/workflows/${editingWorkflow.id}/` : '/api/workflows/';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save workflow');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-workflows'] });
      setShowModal(false);
      setEditingWorkflow(null);
    },
  });

  const handleCreateNew = () => {
    setEditingWorkflow(null);
    setShowModal(true);
  };

  const handleViewDetails = (workflow: Workflow) => {
    setSelectedWorkflow(workflow);
    setShowTransitions(true);
  };

  const handleSave = async (formData: any) => {
    await saveWorkflowMutation.mutateAsync(formData);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Workflow Configuration</h1>
            <p className="text-gray-600">Configure application workflows and transitions</p>
          </div>
          <Button onClick={handleCreateNew} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> New Workflow
          </Button>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {workflows.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <GitBranch className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No workflows configured</p>
            </div>
          ) : (
            workflows.map((workflow: Workflow) => (
              <Card key={workflow.id} className="p-6">
                <h3 className="text-lg font-semibold mb-2">{workflow.name}</h3>
                <p className="text-sm text-gray-600 mb-4">{workflow.description}</p>

                <div className="space-y-2 mb-4 text-sm">
                  <p><strong>Module:</strong> {workflow.module}</p>
                  <p><strong>States:</strong> {workflow.states?.length || 0}</p>
                  <p><strong>Transitions:</strong> {workflow.transitions?.length || 0}</p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleViewDetails(workflow)}
                >
                  <GitBranch className="h-4 w-4 mr-2" /> View Details
                </Button>
              </Card>
            ))
          )}
        </div>

        {showModal && (
          <WorkflowFormModal
            workflow={editingWorkflow}
            onSave={handleSave}
            onClose={() => {
              setShowModal(false);
              setEditingWorkflow(null);
            }}
            isLoading={saveWorkflowMutation.isPending}
          />
        )}

        {showTransitions && selectedWorkflow && (
          <WorkflowDetailsModal
            workflow={selectedWorkflow}
            onClose={() => setShowTransitions(false)}
          />
        )}
      </div>
    </DashboardLayout>
  );
}

function WorkflowFormModal({
  workflow,
  onSave,
  onClose,
  isLoading,
}: {
  workflow: Workflow | null;
  onSave: (data: any) => Promise<void>;
  onClose: () => void;
  isLoading?: boolean;
}) {
  const [formData, setFormData] = useState({
    name: workflow?.name || '',
    module: workflow?.module || '',
    description: workflow?.description || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(formData);
  };

  return (
    <Modal isOpen={true} onClose={onClose} title={workflow ? 'Edit Workflow' : 'Create Workflow'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Workflow Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Input
          label="Module"
          value={formData.module}
          onChange={(e) => setFormData({ ...formData, module: e.target.value })}
          required
        />

        <Input
          label="Description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
        />

        <div className="grid grid-cols-2 gap-4">
          <Button type="submit" disabled={isLoading} className="w-full">
            {isLoading ? 'Saving...' : 'Save'}
          </Button>
          <Button variant="outline" onClick={onClose} className="w-full">
            Cancel
          </Button>
        </div>
      </form>
    </Modal>
  );
}

function WorkflowDetailsModal({
  workflow,
  onClose,
}: {
  workflow: Workflow;
  onClose: () => void;
}) {
  return (
    <Modal isOpen={true} onClose={onClose} title={`${workflow.name} - Transitions`}>
      <div className="space-y-4">
        <div>
          <h4 className="font-semibold mb-2">States</h4>
          <div className="space-y-1">
            {workflow.states?.map((state: State) => (
              <div key={state.id} className="text-sm p-2 bg-gray-50 rounded">
                {state.name}
                {state.is_initial && <span className="ml-2 text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">Initial</span>}
                {state.is_final && <span className="ml-2 text-xs bg-green-100 text-green-800 px-2 py-1 rounded">Final</span>}
              </div>
            ))}
          </div>
        </div>

        <div>
          <h4 className="font-semibold mb-2">Transitions</h4>
          <div className="space-y-1">
            {workflow.transitions?.map((transition: Transition) => (
              <div key={transition.id} className="text-sm p-2 bg-gray-50 rounded">
                <p>{transition.from_state} → {transition.to_state}</p>
                {transition.allowed_roles && (
                  <p className="text-xs text-gray-600">Roles: {transition.allowed_roles.join(', ')}</p>
                )}
              </div>
            ))}
          </div>
        </div>

        <Button variant="outline" onClick={onClose} className="w-full">
          Close
        </Button>
      </div>
    </Modal>
  );
}
