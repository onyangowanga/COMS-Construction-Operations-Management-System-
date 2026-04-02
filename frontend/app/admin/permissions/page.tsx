'use client';

import { useQuery } from '@tanstack/react-query';
import { DataTable } from '@/components/ui/DataTable';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';
import { DashboardLayout } from '@/components/layout';

interface Permission {
  id: string;
  name: string;
  code: string;
  category: string;
  description: string;
  is_system?: boolean;
}

export default function PermissionsPage() {
  const { data: permissions, isLoading } = useQuery<Permission[]>({
    queryKey: ['all-permissions'],
    queryFn: async () => {
      const res = await fetch('/api/permissions/', { credentials: 'include' });
      if (!res.ok) throw new Error('Failed to fetch permissions');
      const data = await res.json();
      return Array.isArray(data) ? data : data.results || [];
    },
  });

  const columns = [
    {
      key: 'category',
      title: 'Category',
      render: (perm: Permission) => (
        <Badge variant="primary">{perm.category}</Badge>
      ),
    },
    { key: 'name', title: 'Permission Name' },
    {
      key: 'code',
      title: 'Code',
      render: (perm: Permission) => (
        <code className="text-sm bg-gray-100 px-2 py-1 rounded">{perm.code}</code>
      ),
    },
    { key: 'description', title: 'Description' },
    {
      key: 'is_system',
      title: 'Type',
      render: (perm: Permission) => (
        <span className="text-sm text-gray-600">{perm.is_system ? 'System' : 'Custom'}</span>
      ),
    },
  ];

  // Group permissions by category
  const groupedPermissions = permissions?.reduce((acc, perm) => {
    if (!acc[perm.category]) acc[perm.category] = [];
    acc[perm.category].push(perm);
    return acc;
  }, {} as Record<string, Permission[]>);

  if (isLoading) return (
      <DashboardLayout>
        <div className="flex items-center justify-center h-64">
          <LoadingSpinner size="lg" />
        </div>
      </DashboardLayout>
  );

  return (
    <DashboardLayout>
      <div>
        <div className="mb-6">
          <h1 className="text-2xl font-bold">Permissions</h1>
          <p className="text-gray-600">View all available permissions in the system</p>
        </div>

        <div className="grid grid-cols-4 gap-4 mb-6">
          {groupedPermissions && Object.entries(groupedPermissions).map(([category, perms]) => (
            <div key={category} className="bg-white p-4 rounded-lg border">
              <div className="text-2xl font-bold text-blue-600">{perms.length}</div>
              <div className="text-sm text-gray-600">{category}</div>
            </div>
          ))}
        </div>

        <div className="bg-white rounded-lg border">
          <DataTable columns={columns} data={permissions || []} />
        </div>

        <div className="mt-6 space-y-6">
          <h2 className="text-xl font-semibold">Permissions by Category</h2>
          {groupedPermissions && Object.entries(groupedPermissions).map(([category, perms]) => (
            <div key={category} className="bg-white rounded-lg border p-6">
              <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                <Badge variant="primary">{category}</Badge>
                <span className="text-sm text-gray-500">({perms.length} permissions)</span>
              </h3>
              <div className="grid grid-cols-2 gap-4">
                {perms.map((perm) => (
                  <div key={perm.id} className="border rounded-lg p-3 hover:bg-gray-50">
                    <div className="font-medium">{perm.name}</div>
                    <code className="text-xs text-gray-500">{perm.code}</code>
                    {perm.description && (
                      <p className="text-sm text-gray-600 mt-1">{perm.description}</p>
                    )}
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>
    </DashboardLayout>
  );
}
