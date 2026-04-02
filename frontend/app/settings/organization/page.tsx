'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Building2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface OrganizationSettings {
  name: string;
  code: string;
  logo?: string;
  default_currency: string;
  fiscal_year_start: string;
}

export default function OrganizationPage() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  const { data: settings, isLoading } = useQuery<OrganizationSettings>({
    queryKey: ['org-settings'],
    queryFn: async () => {
      const res = await fetch('/api/auth/organization-settings/', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch settings');
      return res.json();
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (data: Partial<OrganizationSettings>) => {
      const res = await fetch('/api/auth/organization-settings/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to update settings');
      return res.json();
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['org-settings'], data);
      setIsEditing(false);
    },
  });

  if (isLoading) return <LoadingSpinner />;

  if (!settings) {
    return (
      <DashboardLayout>
        <Card className="p-6">
          <p className="text-gray-600">Organization settings are currently unavailable.</p>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-3xl font-bold">Organization Settings</h1>
          <p className="text-gray-600">Manage your organization's information and preferences</p>
        </div>

        <Card className="p-6">
          <div className="flex justify-between items-center mb-6">
            <h2 className="text-xl font-semibold flex items-center gap-2">
              <Building2 className="h-5 w-5" /> Organization Info
            </h2>
            <Button
              variant="outline"
              onClick={() => setIsEditing(!isEditing)}
            >
              {isEditing ? 'Cancel' : 'Edit'}
            </Button>
          </div>

          {isEditing ? (
            <OrgSettingsForm
              settings={settings}
              onSubmit={(data) => updateMutation.mutateAsync(data)}
              isLoading={updateMutation.isPending}
            />
          ) : (
            <OrgSettingsDisplay settings={settings} />
          )}
        </Card>
      </div>
    </DashboardLayout>
  );
}

function OrgSettingsDisplay({ settings }: { settings: OrganizationSettings }) {
  return (
    <div className="space-y-4">
      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">Organization Name</p>
        <p className="font-semibold text-lg">{settings.name}</p>
      </div>

      <div className="grid grid-cols-2 gap-6">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Organization Code</p>
          <p className="font-semibold">{settings.code}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Default Currency</p>
          <p className="font-semibold">{settings.default_currency}</p>
        </div>
      </div>

      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">Fiscal Year Start</p>
        <p className="font-semibold">{settings.fiscal_year_start}</p>
      </div>
    </div>
  );
}

function OrgSettingsForm({
  settings,
  onSubmit,
  isLoading,
}: {
  settings: OrganizationSettings;
  onSubmit: (data: Partial<OrganizationSettings>) => Promise<void>;
  isLoading?: boolean;
}) {
  const [formData, setFormData] = useState({
    name: settings.name,
    default_currency: settings.default_currency,
    fiscal_year_start: settings.fiscal_year_start,
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <Input
        label="Organization Name"
        value={formData.name}
        onChange={(e) => setFormData({ ...formData, name: e.target.value })}
      />

      <Input
        label="Default Currency"
        value={formData.default_currency}
        onChange={(e) => setFormData({ ...formData, default_currency: e.target.value })}
        placeholder="KES"
      />

      <Input
        label="Fiscal Year Start"
        value={formData.fiscal_year_start}
        onChange={(e) => setFormData({ ...formData, fiscal_year_start: e.target.value })}
        placeholder="January 1"
      />

      <Button type="submit" disabled={isLoading}>
        {isLoading ? 'Saving...' : 'Save Changes'}
      </Button>
    </form>
  );
}
