'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Trash2, Shield } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';
import { Modal } from '@/components/ui/Modal';

interface Role {
  id: string;
  name: string;
  description: string;
  is_system_role: boolean;
  is_active: boolean;
  permissions?: Permission[];
  user_count?: number;
}

interface Permission {
  id: string;
  code: string;
  name: string;
  description: string;
}

export default function RolesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingRole, setEditingRole] = useState<Role | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  // Fetch roles
  const { data: roles = [], isLoading } = useQuery<Role[]>({
    queryKey: ['admin-roles', searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const res = await fetch(`/api/roles/?${params}`, {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch roles');
      const data = await res.json();
      return Array.isArray(data) ? data : data.results || [];
    },
  });

  // Fetch permissions
  const { data: permissions = [] } = useQuery<Permission[]>({
    queryKey: ['permissions'],
    queryFn: async () => {
      const res = await fetch('/api/permissions/', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch permissions');
      return res.json();
    },
  });

  // Create/update role mutation
  const saveRoleMutation = useMutation({
    mutationFn: async (data: Partial<Role>) => {
      const method = editingRole ? 'PATCH' : 'POST';
      const url = editingRole ? `/api/roles/${editingRole.id}/` : '/api/roles/';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save role');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
      setShowModal(false);
      setEditingRole(null);
    },
  });

  // Delete role mutation
  const deleteRoleMutation = useMutation({
    mutationFn: async (roleId: string) => {
      const res = await fetch(`/api/roles/${roleId}/`, {
        method: 'DELETE',
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to delete role');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-roles'] });
    },
  });

  const handleCreateNew = () => {
    setEditingRole(null);
    setShowModal(true);
  };

  const handleEdit = (role: Role) => {
    setEditingRole(role);
    setShowModal(true);
  };

  const handleSave = async (formData: any) => {
    await saveRoleMutation.mutateAsync(formData);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Header */}
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Role Management</h1>
            <p className="text-gray-600">Create and manage user roles with permissions</p>
          </div>
          <Button onClick={handleCreateNew} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> New Role
          </Button>
        </div>

        {/* Search */}
        <Card className="p-4">
          <Input
            placeholder="Search roles..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Card>

        {/* Roles Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {roles.length === 0 ? (
            <div className="col-span-full text-center py-12">
              <Shield className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No roles found</p>
            </div>
          ) : (
            roles.map((role: Role) => (
              <Card key={role.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{role.name}</h3>
                    <p className="text-sm text-gray-600">{role.description}</p>
                  </div>
                  {role.is_system_role && (
                    <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
                      System
                    </span>
                  )}
                </div>

                <div className="mb-4">
                  <p className="text-xs text-gray-500 mb-2">
                    {role.user_count || 0} users assigned
                  </p>
                  {role.permissions && role.permissions.length > 0 && (
                    <div className="flex flex-wrap gap-1">
                      {role.permissions.slice(0, 3).map((perm: Permission) => (
                        <span
                          key={perm.id}
                          className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded"
                        >
                          {perm.code}
                        </span>
                      ))}
                      {role.permissions.length > 3 && (
                        <span className="px-2 py-1 bg-gray-100 text-gray-700 text-xs rounded">
                          +{role.permissions.length - 3} more
                        </span>
                      )}
                    </div>
                  )}
                </div>

                <div className="flex gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    onClick={() => handleEdit(role)}
                    className="flex-1"
                  >
                    <Edit2 className="h-4 w-4 mr-2" /> Edit
                  </Button>
                  {!role.is_system_role && (
                    <Button
                      variant="outline"
                      size="sm"
                      className="text-red-600 hover:text-red-700"
                      onClick={() => {
                        if (confirm(`Delete role "${role.name}"?`)) {
                          deleteRoleMutation.mutate(role.id);
                        }
                      }}
                    >
                      <Trash2 className="h-4 w-4" />
                    </Button>
                  )}
                </div>
              </Card>
            ))
          )}
        </div>

        {/* Role Modal */}
        {showModal && (
          <RoleFormModal
            role={editingRole}
            permissions={permissions}
            onSave={handleSave}
            onClose={() => {
              setShowModal(false);
              setEditingRole(null);
            }}
            isLoading={saveRoleMutation.isPending}
          />
        )}
      </div>
    </DashboardLayout>
  );
}

function RoleFormModal({
  role,
  permissions,
  onSave,
  onClose,
  isLoading,
}: {
  role: Role | null;
  permissions: Permission[];
  onSave: (data: any) => Promise<void>;
  onClose: () => void;
  isLoading?: boolean;
}) {
  const [formData, setFormData] = useState({
    name: role?.name || '',
    description: role?.description || '',
    permissions: role?.permissions?.map((p: Permission) => p.id) || [],
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(formData);
  };

  const togglePermission = (permissionId: string) => {
    setFormData((prev) => ({
      ...prev,
      permissions: prev.permissions.includes(permissionId)
        ? prev.permissions.filter((id) => id !== permissionId)
        : [...prev.permissions, permissionId],
    }));
  };

  return (
    <Modal isOpen={true} onClose={onClose} title={role ? 'Edit Role' : 'Create New Role'}>
      <form onSubmit={handleSubmit} className="space-y-4">
        <Input
          label="Role Name"
          value={formData.name}
          onChange={(e) => setFormData({ ...formData, name: e.target.value })}
          required
        />

        <Input
          label="Description"
          value={formData.description}
          onChange={(e) => setFormData({ ...formData, description: e.target.value })}
          placeholder="What is this role for?"
        />

        <div>
          <label className="block text-sm font-semibold mb-3">Permissions</label>
          <div className="border border-gray-300 rounded-md p-4 max-h-48 overflow-y-auto space-y-2">
            {permissions.length === 0 ? (
              <p className="text-sm text-gray-500">No permissions available</p>
            ) : (
              permissions.map((perm: Permission) => (
                <label key={perm.id} className="flex items-center">
                  <input
                    type="checkbox"
                    checked={formData.permissions.includes(perm.id)}
                    onChange={() => togglePermission(perm.id)}
                    className="rounded"
                  />
                  <span className="ml-3 text-sm">
                    <strong>{perm.code}</strong> - {perm.name}
                  </span>
                </label>
              ))
            )}
          </div>
        </div>

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
