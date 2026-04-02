'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DashboardLayout } from '@/components/layout';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';

interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  role?: string;
  system_role?: string;
  roles?: string[];
  organization: string;
  is_active: boolean;
  last_login?: string;
  date_joined: string;
}

const SYSTEM_ROLE_OPTIONS = [
  { value: 'super_admin', label: 'Super Admin' },
  { value: 'contractor', label: 'Contractor' },
  { value: 'site_manager', label: 'Site Manager' },
  { value: 'qs', label: 'Quantity Surveyor' },
  { value: 'architect', label: 'Architect' },
  { value: 'client', label: 'Client' },
  { value: 'staff', label: 'Staff Member' },
];

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const res = await fetch('/api/auth/users/', { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch users');
      return res.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: Partial<User> & { password: string }) => {
      const payload = {
        ...data,
        system_role: data.system_role || data.role || 'client',
      };
      const res = await fetch('/api/auth/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setShowModal(false);
      setEditingUser(null);
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<User> }) => {
      const payload = {
        ...data,
        system_role: data.system_role || data.role,
      };
      const res = await fetch(`/api/auth/users/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(payload),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setShowModal(false);
      setEditingUser(null);
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async (user: User) => {
      const res = await fetch(`/api/auth/users/${user.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ is_active: !user.is_active }),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const columns = [
    {
      key: 'username',
      title: 'User',
      render: (user: User) => (
        <div>
          <div className="font-medium">{user.username}</div>
          <div className="text-sm text-gray-500">
            {user.first_name} {user.last_name}
          </div>
        </div>
      ),
    },
    {
      key: 'email',
      title: 'Email',
    },
    {
      key: 'role',
      title: 'Role',
      render: (user: User) => (
        <Badge variant="primary">{user.system_role || user.role || user.roles?.[0] || 'client'}</Badge>
      ),
    },
    {
      key: 'organization',
      title: 'Organization',
    },
    {
      key: 'is_active',
      title: 'Status',
      render: (user: User) => (
        <Badge variant={user.is_active ? 'success' : 'default'}>
          {user.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'last_login',
      title: 'Last Login',
      render: (user: User) => (
        <span className="text-sm text-gray-600">
          {user.last_login ? new Date(user.last_login).toLocaleDateString() : 'Never'}
        </span>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (user: User) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setEditingUser(user);
              setShowModal(true);
            }}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => toggleActiveMutation.mutate(user)}
          >
            {user.is_active ? 'Deactivate' : 'Activate'}
          </Button>
        </div>
      ),
    },
  ];

  if (isLoading) return (
    <DashboardLayout>
      <div className="flex items-center justify-center h-64">
        <LoadingSpinner size="lg" />
      </div>
    </DashboardLayout>
  );

  return (
    <DashboardLayout>
      <div className="flex items-center justify-between mb-6">
        <div>
          <h1 className="text-2xl font-bold">Users</h1>
          <p className="text-gray-600">Manage system users and their roles</p>
        </div>
        <Button
          onClick={() => {
            setEditingUser(null);
            setShowModal(true);
          }}
        >
          Add User
        </Button>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-4 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-blue-600">{users?.length || 0}</div>
          <div className="text-sm text-gray-600">Total Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-green-600">
            {users?.filter((u) => u.is_active).length || 0}
          </div>
          <div className="text-sm text-gray-600">Active Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-red-600">
            {users?.filter((u) => !u.is_active).length || 0}
          </div>
          <div className="text-sm text-gray-600">Inactive Users</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-purple-600">
            {users?.filter((u) => u.last_login).length || 0}
          </div>
          <div className="text-sm text-gray-600">Users Logged In</div>
        </div>
      </div>

      <DataTable columns={columns} data={users || []} />

      {/* Create/Edit User Modal */}
      {showModal && (
        <Modal
          isOpen={showModal}
          title={editingUser ? 'Edit User' : 'Create User'}
          onClose={() => {
            setShowModal(false);
            setEditingUser(null);
          }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              const data = {
                username: formData.get('username') as string,
                email: formData.get('email') as string,
                first_name: formData.get('first_name') as string,
                last_name: formData.get('last_name') as string,
                system_role: formData.get('role') as string,
              };

              if (editingUser) {
                updateMutation.mutate({ id: editingUser.id, data });
              } else {
                createMutation.mutate({
                  ...data,
                  password: formData.get('password') as string,
                });
              }
            }}
          >
            <div className="space-y-4">
              <Input
                label="Username"
                name="username"
                defaultValue={editingUser?.username}
                required
                disabled={!!editingUser}
              />

              <Input
                label="Email"
                name="email"
                type="email"
                defaultValue={editingUser?.email}
                required
              />

              <div className="grid grid-cols-2 gap-4">
                <Input
                  label="First Name"
                  name="first_name"
                  defaultValue={editingUser?.first_name}
                  required
                />
                <Input
                  label="Last Name"
                  name="last_name"
                  defaultValue={editingUser?.last_name}
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Role</label>
                <select
                  name="role"
                  defaultValue={editingUser?.system_role || editingUser?.role || editingUser?.roles?.[0] || 'client'}
                  className="w-full px-3 py-2 border rounded-lg"
                  required
                >
                  {SYSTEM_ROLE_OPTIONS.map((role) => (
                    <option key={role.value} value={role.value}>
                      {role.label}
                    </option>
                  ))}
                </select>
              </div>

              {!editingUser && (
                <Input
                  label="Password"
                  name="password"
                  type="password"
                  required
                  helperText="User will be able to change this after first login"
                />
              )}

              <div className="flex gap-3 pt-4 border-t">
                <Button
                  type="submit"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {editingUser ? 'Update User' : 'Create User'}
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowModal(false);
                    setEditingUser(null);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </form>
        </Modal>
      )}
    </DashboardLayout>
  );
}
