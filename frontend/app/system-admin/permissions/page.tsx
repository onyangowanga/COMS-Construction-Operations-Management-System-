'use client';

import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Shield, Lock } from 'lucide-react';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface Permission {
  id: string;
  code: string;
  name: string;
  description: string;
  category: string;
  is_system: boolean;
}

interface PermissionListResponse {
  results?: Permission[];
}

export default function PermissionsPage() {
  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);

  // Fetch permissions
  const { data: permissions = [], isLoading } = useQuery<Permission[]>({
    queryKey: ['permissions', searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const res = await fetch(`/api/permissions/?${params}`, {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch permissions');
      const data: Permission[] | PermissionListResponse = await res.json();
      if (Array.isArray(data)) return data;
      return data.results || [];
    },
  });

  const categories: string[] = [...new Set(permissions.map((p) => p.category))].sort();

  const filteredPermissions = permissions.filter((p) =>
    !selectedCategory || p.category === selectedCategory
  );

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">Permission Management</h1>
          <p className="text-gray-600">View and manage system permissions</p>
        </div>

        <Card className="p-4">
          <Input
            placeholder="Search permissions..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Card>

        {/* Categories */}
        <div className="flex flex-wrap gap-2">
          <button
            onClick={() => setSelectedCategory(null)}
            className={`px-4 py-2 rounded-md text-sm font-medium ${
              selectedCategory === null
                ? 'bg-blue-600 text-white'
                : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
            }`}
          >
            All
          </button>
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelectedCategory(cat)}
              className={`px-4 py-2 rounded-md text-sm font-medium ${
                selectedCategory === cat
                  ? 'bg-blue-600 text-white'
                  : 'bg-gray-200 text-gray-800 hover:bg-gray-300'
              }`}
            >
              {cat}
            </button>
          ))}
        </div>

        {/* Permissions List */}
        <div className="space-y-4">
          {filteredPermissions.length === 0 ? (
            <div className="text-center py-12">
              <Lock className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No permissions found</p>
            </div>
          ) : (
            filteredPermissions.map((perm: Permission) => (
              <Card key={perm.id} className="p-4">
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      <h3 className="font-semibold">{perm.name}</h3>
                      {perm.is_system && (
                        <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs font-semibold rounded">
                          System
                        </span>
                      )}
                    </div>
                    <p className="text-sm text-gray-600 mt-1">{perm.description}</p>
                    <p className="text-xs text-gray-500 mt-2">Code: <code className="bg-gray-100 px-2 py-1 rounded">{perm.code}</code></p>
                  </div>
                  <span className="text-xs bg-gray-100 text-gray-700 px-3 py-1 rounded">
                    {perm.category}
                  </span>
                </div>
              </Card>
            ))
          )}
        </div>
      </div>
    </DashboardLayout>
  );
}
