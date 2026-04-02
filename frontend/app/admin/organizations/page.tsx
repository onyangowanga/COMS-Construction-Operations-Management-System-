'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';

interface Organization {
  id: string;
  name: string;
  code: string;
  default_currency: string;
  fiscal_year_start: string;
  users_count: number;
  projects_count: number;
  is_active: boolean;
  created_at: string;
}

export default function OrganizationsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingOrg, setEditingOrg] = useState<Organization | null>(null);

  const { data: organizations, isLoading } = useQuery<Organization[]>({
    queryKey: ['organizations'],
    queryFn: async () => {
      const res = await fetch('/api/organizations/', { credentials: 'include' });
      return res.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: Partial<Organization>) => {
      const res = await fetch('/api/organizations/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setShowModal(false);
      setEditingOrg(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Organization> }) => {
      const res = await fetch(`/api/organizations/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
      setShowModal(false);
      setEditingOrg(null);
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async (org: Organization) => {
      const res = await fetch(`/api/organizations/${org.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ is_active: !org.is_active }),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organizations'] });
    },
  });

  const columns = [
    {
      key: 'name',
      title: 'Organization',
      render: (org: Organization) => (
        <div>
          <div className="font-medium">{org.name}</div>
          <div className="text-sm text-gray-500">{org.code}</div>
        </div>
      ),
    },
    {
      key: 'default_currency',
      title: 'Currency',
      render: (org: Organization) => (
        <Badge variant="primary">{org.default_currency}</Badge>
      ),
    },
    {
      key: 'fiscal_year_start',
      title: 'Fiscal Year',
    },
    {
      key: 'users_count',
      title: 'Users',
      render: (org: Organization) => (
        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
          {org.users_count} users
        </span>
      ),
    },
    {
      key: 'projects_count',
      title: 'Projects',
      render: (org: Organization) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
          {org.projects_count} projects
        </span>
      ),
    },
    {
      key: 'is_active',
      title: 'Status',
      render: (org: Organization) => (
        <Badge variant={org.is_active ? 'success' : 'destructive'}>
          {org.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (org: Organization) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setEditingOrg(org);
              setShowModal(true);
            }}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => toggleActiveMutation.mutate(org)}
          >
            {org.is_active ? 'Deactivate' : 'Activate'}
          </Button>
        </div>
      ),
    },
  ];

  if (isLoading) return (
    <div className="flex items-center justify-center h-64">
      <LoadingSpinner size="lg" />
    </div>
  );

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-2xl font-bold">Organizations</h1>
          <p className="text-gray-600">Manage organizations and their settings</p>
        </div>
        <Button onClick={() => { setEditingOrg(null); setShowModal(true); }}>
          Create Organization
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-blue-600">{organizations?.length || 0}</div>
          <div className="text-sm text-gray-600">Total Organizations</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-green-600">
            {organizations?.filter(o => o.is_active).length || 0}
          </div>
          <div className="text-sm text-gray-600">Active</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-purple-600">
            {organizations?.reduce((acc, o) => acc + o.users_count, 0) || 0}
          </div>
          <div className="text-sm text-gray-600">Total Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-orange-600">
            {organizations?.reduce((acc, o) => acc + o.projects_count, 0) || 0}
          </div>
          <div className="text-sm text-gray-600">Total Projects</div>
        </div>
      </div>

      <DataTable columns={columns} data={organizations || []} />

      {/* Create/Edit Modal */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editingOrg ? 'Edit Organization' : 'Create Organization'}
          onClose={() => { setShowModal(false); setEditingOrg(null); }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const data = {
                name: formData.get('name') as string,
                code: formData.get('code') as string,
                default_currency: formData.get('default_currency') as string,
                fiscal_year_start: formData.get('fiscal_year_start') as string,
              };

              if (editingOrg) {
                updateMutation.mutate({ id: editingOrg.id, data });
              } else {
                createMutation.mutate(data);
              }
            }}
          >
            <div className="space-y-4">
              <Input
                label="Organization Name"
                name="name"
                defaultValue={editingOrg?.name}
                required
                placeholder="e.g., Main Office"
              />
              <Input
                label="Organization Code"
                name="code"
                defaultValue={editingOrg?.code}
                required
                placeholder="e.g., MAIN"
              />
              <Input
                label="Default Currency"
                name="default_currency"
                defaultValue={editingOrg?.default_currency || 'KES'}
                required
                placeholder="e.g., KES"
              />
              <Input
                label="Fiscal Year Start (MM-DD)"
                name="fiscal_year_start"
                defaultValue={editingOrg?.fiscal_year_start || '01-01'}
                required
                placeholder="e.g., 01-01"
              />
              <div className="flex gap-3">
                <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {editingOrg ? 'Update' : 'Create'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => { setShowModal(false); setEditingOrg(null); }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
