'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Bell, Mail, MessageSquare } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface NotificationPreferences {
  email_enabled: boolean;
  sms_enabled: boolean;
  quiet_hours_start?: string;
  quiet_hours_end?: string;
  digest_frequency: 'immediate' | 'daily' | 'weekly' | 'never';
}

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const [preferences, setPreferences] = useState<NotificationPreferences | null>(null);

  const { data: savedPrefs, isLoading } = useQuery<NotificationPreferences>({
    queryKey: ['notification-preferences'],
    queryFn: async () => {
      const res = await fetch('/api/auth/notification-preferences/', {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch preferences');
      return res.json();
    },
  });

  const saveMutation = useMutation({
    mutationFn: async (data: NotificationPreferences) => {
      const res = await fetch('/api/auth/notification-preferences/', {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save preferences');
      return res.json();
    },
    onSuccess: (data) => {
      setPreferences(null);
      queryClient.setQueryData(['notification-preferences'], data);
    },
  });

  const handleChange = (field: keyof NotificationPreferences, value: any) => {
    if (!preferences && savedPrefs) {
      setPreferences({ ...savedPrefs, [field]: value });
    } else if (preferences) {
      setPreferences({ ...preferences, [field]: value });
    }
  };

  const prefs = preferences || savedPrefs;

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6 max-w-2xl">
        <div>
          <h1 className="text-3xl font-bold">Notifications</h1>
          <p className="text-gray-600">Manage how and when you receive notifications</p>
        </div>

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4 flex items-center gap-2">
            <Bell className="h-5 w-5" /> Notification Channels
          </h2>
          <div className="space-y-3">
            <label className="flex items-center">
              <input
                type="checkbox"
                checked={prefs?.email_enabled || false}
                onChange={(e) => handleChange('email_enabled', e.target.checked)}
                className="rounded"
              />
              <span className="ml-3 flex items-center gap-2">
                <Mail className="h-4 w-4 text-blue-600" /> Email Notifications
              </span>
            </label>

            <label className="flex items-center">
              <input
                type="checkbox"
                checked={prefs?.sms_enabled || false}
                onChange={(e) => handleChange('sms_enabled', e.target.checked)}
                className="rounded"
              />
              <span className="ml-3 flex items-center gap-2">
                <MessageSquare className="h-4 w-4 text-green-600" /> SMS Notifications
              </span>
            </label>
          </div>
        </Card>

        {(prefs?.email_enabled || prefs?.sms_enabled) && (
          <Card className="p-6">
            <h2 className="text-lg font-semibold mb-4">Quiet Hours</h2>
            <p className="text-sm text-gray-600 mb-4">Don't send notifications during these times</p>
            <div className="grid grid-cols-2 gap-4">
              <Input
                label="Start Time"
                type="time"
                value={prefs?.quiet_hours_start || ''}
                onChange={(e) => handleChange('quiet_hours_start', e.target.value)}
              />
              <Input
                label="End Time"
                type="time"
                value={prefs?.quiet_hours_end || ''}
                onChange={(e) => handleChange('quiet_hours_end', e.target.value)}
              />
            </div>
          </Card>
        )}

        <Card className="p-6">
          <h2 className="text-lg font-semibold mb-4">Digest Frequency</h2>
          <select
            value={prefs?.digest_frequency || 'immediate'}
            onChange={(e) => handleChange('digest_frequency', e.target.value as NotificationPreferences['digest_frequency'])}
            className="w-full px-3 py-2 border border-gray-300 rounded-md"
          >
            <option value="immediate">Immediate</option>
            <option value="daily">Daily Digest</option>
            <option value="weekly">Weekly Digest</option>
            <option value="never">Never</option>
          </select>
        </Card>

        {preferences && (
          <div className="flex gap-2 pt-4 border-t">
            <Button onClick={() => saveMutation.mutateAsync(preferences)} disabled={saveMutation.isPending}>
              {saveMutation.isPending ? 'Saving...' : 'Save Preferences'}
            </Button>
            <Button variant="outline" onClick={() => setPreferences(null)}>
              Cancel
            </Button>
          </div>
        )}
      </div>
    </DashboardLayout>
  );
}
