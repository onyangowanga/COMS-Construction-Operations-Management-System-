'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';

interface Role {
  id: string;
  name: string;
  description: string;
  permissions_count: number;
  users_count: number;
  is_system_role: boolean;
}

interface Permission {
  id: string;
  name: string;
  codename: string;
  category: string;
}

export default function RolesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [showPermissionsModal, setShowPermissionsModal] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [selectedRole, setSelectedRole] = useState<Role | null>(null);

  const { data: roles, isLoading } = useQuery<Role[]>({
    queryKey: ['admin-roles'],
    queryFn: async () => {
      const res = await fetch('/api/roles/', { credentials: 'include' });
      return res.json();
    },
  });

  const { data: permissions } = useQuery<Permission[]>({
    queryKey: ['permissions'],
    queryFn: async () => {
      const res = await fetch('/api/roles/permissions/', { credentials: 'include' });
      return res.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: { name: string; description: string }) => {
      const res = await fetch('/api/roles/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      setShowModal(false);
      setEditingRole(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<Role> }) => {
      const res = await fetch(`/api/roles/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      setShowModal(false);
      setEditingRole(null);
    },
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      const res = await fetch(`/api/roles/${id}/`, {
        method: 'DELETE',
        credentials: 'include',
      });
      return res.ok;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
    },
  });

  const columns = [
    { key: 'name', title: 'Role Name' },
    { key: 'description', title: 'Description' },
    {
      key: 'permissions_count',
      title: 'Permissions',
      render: (role: Role) => (
        <span className="px-2 py-1 bg-blue-100 text-blue-800 rounded text-sm">
          {role.permissions_count} permissions
        </span>
      ),
    },
    {
      key: 'users_count',
      title: 'Users',
      render: (role: Role) => (
        <span className="px-2 py-1 bg-green-100 text-green-800 rounded text-sm">
          {role.users_count} users
        </span>
      ),
    },
    {
      key: 'is_system_role',
      title: 'Type',
      render: (role: Role) => (
        <span className={`px-2 py-1 rounded text-sm ${role.is_system_role ? 'bg-gray-100 text-gray-800' : 'bg-purple-100 text-purple-800'}`}>
          {role.is_system_role ? 'System' : 'Custom'}
        </span>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (role: Role) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setSelectedRole(role);
              setShowPermissionsModal(true);
            }}
          >
            Permissions
          </Button>
          {!role.is_system_role && (
            <>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  setEditingRole(role);
                  setShowModal(true);
                }}
              >
                Edit
              </Button>
              <Button
                size="sm"
                variant="outline"
                onClick={() => {
                  if (confirm('Are you sure you want to delete this role?')) {
                    deleteMutation.mutate(role.id);
                  }
                }}
              >
                Delete
              </Button>
            </>
          )}
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
          <h1 className="text-2xl font-bold">Roles & Permissions</h1>
          <p className="text-gray-600">Manage user roles and their permissions</p>
        </div>
        <Button onClick={() => { setEditingRole(null); setShowModal(true); }}>
          Create Role
        </Button>
      </div>

      <DataTable columns={columns} data={roles || []} />

      {/* Create/Edit Role Modal */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editingRole ? 'Edit Role' : 'Create Role'}
          onClose={() => { setShowModal(false); setEditingRole(null); }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const data = {
                name: formData.get('name') as string,
                description: formData.get('description') as string,
              };

              if (editingRole) {
                updateMutation.mutate({ id: editingRole.id, data });
              } else {
                createMutation.mutate(data);
              }
            }}
          >
            <div className="space-y-4">
              <Input
                label="Role Name"
                name="name"
                defaultValue={editingRole?.name}
                required
                placeholder="e.g., Project Manager"
              />
              <div>
                <label className="block text-sm font-medium mb-2">Description</label>
                <textarea
                  name="description"
                  defaultValue={editingRole?.description}
                  className="w-full px-3 py-2 border rounded-lg"
                  rows={3}
                  placeholder="Describe the role's responsibilities"
                />
              </div>
              <div className="flex gap-3">
                <Button type="submit" disabled={createMutation.isPending || updateMutation.isPending}>
                  {editingRole ? 'Update Role' : 'Create Role'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => { setShowModal(false); setEditingRole(null); }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </form>
        </Modal>
      )}

      {/* Permissions Modal */}
      {showPermissionsModal && selectedRole && (
        <Modal
          isOpen={showPermissionsModal && !!selectedRole}
          title={`${selectedRole.name} - Permissions`}
          onClose={() => { setShowPermissionsModal(false); setSelectedRole(null); }}
        >
          <div className="space-y-4">
            <p className="text-sm text-gray-600">
              Configure which permissions this role has access to
            </p>

            <div className="max-h-96 overflow-y-auto space-y-2">
              {permissions?.map((perm) => (
                <label key={perm.id} className="flex items-center gap-3 p-3 border rounded hover:bg-gray-50 cursor-pointer">
                  <input type="checkbox" className="w-4 h-4" />
                  <div className="flex-1">
                    <div className="font-medium">{perm.name}</div>
                    <div className="text-sm text-gray-500">{perm.codename}</div>
                  </div>
                  <span className="text-xs bg-gray-100 px-2 py-1 rounded">{perm.category}</span>
                </label>
              ))}
            </div>

            <div className="flex gap-3 pt-4 border-t">
              <Button onClick={() => setShowPermissionsModal(false)}>
                Save Permissions
              </Button>
              <Button variant="outline" onClick={() => setShowPermissionsModal(false)}>
                Cancel
              </Button>
            </div>
          </div>
        </Modal>
      )}
      </div>
  );
}
