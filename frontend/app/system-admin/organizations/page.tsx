'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Building2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';
import { Modal } from '@/components/ui/Modal';

interface Organization {
  id: string;
  name: string;
  code: string;
  logo?: string;
  default_currency: string;
  fiscal_year_start: string;
  is_active: boolean;
  user_count?: number;
}

export default function OrganizationsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch organizations
  const { data: organizations = [], isLoading } = useQuery<Organization[]>({
    queryKey: ['admin-organizations', searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const res = await fetch(`/api/organizations/?${params}`, {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch organizations');
      const data = await res.json();
      return Array.isArray(data) ? data : data.results || [];
    },
  });

  // Create/update organization mutation
  const saveOrgMutation = useMutation({
    mutationFn: async (data: Partial<Organization>) => {
      const method = editingOrg ? 'PATCH' : 'POST';
      const url = editingOrg ? `/api/organizations/${editingOrg.id}/` : '/api/organizations/';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save organization');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-organizations'] });
      setShowModal(false);
      setEditingOrg(null);
    },
  });

  const handleCreateNew = () => {
    setEditingOrg(null);
    setShowModal(true);
  };

  const handleEdit = (org: Organization) => {
    setEditingOrg(org);
    setShowModal(true);
  };

  const handleSave = async (formData: any) => {
    await saveOrgMutation.mutateAsync(formData);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Organization Management</h1>
            <p className="text-gray-600">Manage tenant organizations and settings</p>
          </div>
          <Button onClick={handleCreateNew} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> New Organization
          </Button>
        </div>

        <Card className="p-4">
          <Input
            placeholder="Search organizations..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Card>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {organizations.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <Building2 className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No organizations found</p>
            </div>
          ) : (
            organizations.map((org: Organization) => (
              <Card key={org.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{org.name}</h3>
                    <p className="text-sm text-gray-600">Code: {org.code}</p>
                  </div>
                  {!org.is_active && (
                    <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
                      Inactive
                    </span>
                  )}
                </div>

                <div className="space-y-2 mb-4 text-sm">
                  <p><strong>Currency:</strong> {org.default_currency}</p>
                  <p><strong>Fiscal Year Start:</strong> {org.fiscal_year_start}</p>
                  <p><strong>Users:</strong> {org.user_count || 0}</p>
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEdit(org)}
                >
                  <Edit2 className="h-4 w-4 mr-2" /> Edit
                </Button>
              </Card>
            ))
          )}
        </div>

        {showModal && (
          <OrgFormModal
            org={editingOrg}
            onSave={handleSave}
            onClose={() => {
              setShowModal(false);
              setEditingOrg(null);
            }}
            isLoading={saveOrgMutation.isPending}
          />
        )}
      </div>
    </DashboardLayout>
  );
}

function OrgFormModal({
  org,
  onSave,
  onClose,
  isLoading,
}: {
  org: Organization | null;
  onSave: (data: any) => Promise<void>;
  onClose: () => void;
  isLoading?: boolean;
}) {
  const [formData, setFormData] = useState({
    name: org?.name || '',
    code: org?.code || '',
    default_currency: org?.default_currency || 'KES',
    fiscal_year_start: org?.fiscal_year_start || 'January 1',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(formData);
  };

  return (
    <Modal isOpen={true} onClose={onClose} title={org ? 'Edit Organization' : 'Create Organization'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Organization Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Input
          label="Code"
          value={formData.code}
          onChange={(e) => setFormData({ ...formData, code: e.target.value })}
          required
          disabled={!!org}
        />

        <Input
          label="Default Currency"
          value={formData.default_currency}
          onChange={(e) => setFormData({ ...formData, default_currency: e.target.value })}
        />

        <Input
          label="Fiscal Year Start"
          value={formData.fiscal_year_start}
          onChange={(e) => setFormData({ ...formData, fiscal_year_start: e.target.value })}
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
