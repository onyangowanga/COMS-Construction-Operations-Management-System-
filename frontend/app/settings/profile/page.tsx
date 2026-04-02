'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { User, Camera } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface UserProfile {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  phone: string;
  profile_picture?: string;
  organization?: string | null;
  organization_name?: string | null;
  role?: string;
  system_role?: string;
}

export default function ProfilePage() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  const { data: profile, isLoading } = useQuery<UserProfile>({
    queryKey: ['profile'],
    queryFn: async () => {
      const res = await fetch('/api/auth/profile/', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch profile');
      return res.json();
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (data: Partial<UserProfile>) => {
      const res = await fetch('/api/auth/profile/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to update profile');
      return res.json();
    },
    onSuccess: (data) => {
      queryClient.setQueryData(['profile'], data);
      setIsEditing(false);
    },
  });

  if (isLoading) return <LoadingSpinner />;

  if (!profile) {
    return (
      <DashboardLayout>
        <Card className="p-6">
          <p className="text-gray-600">Profile data is currently unavailable.</p>
        </Card>
      </DashboardLayout>
    );
  }

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div>
          <h1 className="text-3xl font-bold">My Profile</h1>
          <p className="text-gray-600">Manage your personal information and profile</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          <div className="lg:col-span-1">
            <Card className="p-6 text-center">
              <div className="mb-4 relative inline-block">
                <div className="w-24 h-24 rounded-full bg-gray-200 flex items-center justify-center">
                  {profile?.profile_picture ? (
                    <img src={profile.profile_picture} alt="Profile" className="w-24 h-24 rounded-full" />
                  ) : (
                    <User className="w-12 h-12 text-gray-400" />
                  )}
                </div>
                <button className="absolute bottom-0 right-0 bg-blue-600 text-white p-2 rounded-full hover:bg-blue-700">
                  <Camera className="h-4 w-4" />
                </button>
              </div>
              <h3 className="font-semibold text-lg">
                {profile?.first_name} {profile?.last_name}
              </h3>
              <p className="text-sm text-gray-600">{profile?.role || profile?.system_role || 'user'}</p>
              <p className="text-xs text-gray-500 mt-2">{profile?.organization_name || profile?.organization || 'Unassigned'}</p>
            </Card>
          </div>

          <div className="lg:col-span-2">
            <Card className="p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-xl font-semibold">Personal Information</h2>
                <Button
                  variant="outline"
                  onClick={() => setIsEditing(!isEditing)}
                >
                  {isEditing ? 'Cancel' : 'Edit'}
                </Button>
              </div>

              {isEditing ? (
                <ProfileForm profile={profile} onSubmit={(data) => updateMutation.mutateAsync(data)} />
              ) : (
                <ProfileDisplay profile={profile} />
              )}
            </Card>
          </div>
        </div>
      </div>
    </DashboardLayout>
  );
}

function ProfileDisplay({ profile }: { profile: UserProfile }) {
  return (
    <div className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">First Name</p>
          <p className="font-semibold">{profile.first_name}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Last Name</p>
          <p className="font-semibold">{profile.last_name}</p>
        </div>
      </div>

      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">Email Address</p>
        <p className="font-semibold">{profile.email}</p>
      </div>

      <div>
        <p className="text-xs text-gray-500 uppercase tracking-wide">Phone Number</p>
        <p className="font-semibold">{profile.phone || 'Not provided'}</p>
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Username</p>
          <p className="font-semibold">@{profile.username}</p>
        </div>
        <div>
          <p className="text-xs text-gray-500 uppercase tracking-wide">Organization</p>
          <p className="font-semibold">{profile.organization_name || profile.organization || 'Unassigned'}</p>
        </div>
      </div>
    </div>
  );
}

function ProfileForm({
  profile,
  onSubmit,
}: {
  profile: UserProfile;
  onSubmit: (data: Partial<UserProfile>) => Promise<void>;
}) {
  const [formData, setFormData] = useState({
    first_name: profile.first_name,
    last_name: profile.last_name,
    phone: profile.phone || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-4">
      <div className="grid grid-cols-2 gap-4">
        <Input
          label="First Name"
          value={formData.first_name}
          onChange={(e) => setFormData({ ...formData, first_name: e.target.value })}
        />
        <Input
          label="Last Name"
          value={formData.last_name}
          onChange={(e) => setFormData({ ...formData, last_name: e.target.value })}
        />
      </div>

      <Input
        label="Phone Number"
        type="tel"
        value={formData.phone}
        onChange={(e) => setFormData({ ...formData, phone: e.target.value })}
      />

      <div className="flex gap-2 pt-4 border-t">
        <Button type="submit" className="flex-1">Save Changes</Button>
      </div>
    </form>
  );
}
