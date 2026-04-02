'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Plus, Edit2, Bell, Mail, MessageSquare, X } from 'lucide-react';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Card } from '@/components/ui/Card';
import { LoadingSpinner } from '@/components/ui/Loading';
import { DashboardLayout } from '@/components/layout';

interface NotificationTemplate {
  id: string;
  name: string;
  email_subject?: string;
  email_body?: string;
  sms_body?: string;
  channels: string[];
  is_active: boolean;
  trigger_event: string;
}

export default function NotificationsPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);
  const [searchTerm, setSearchTerm] = useState('');

  const { data: templates = [], isLoading } = useQuery<NotificationTemplate[]>({
    queryKey: ['admin-notifications', searchTerm],
    queryFn: async () => {
      const params = new URLSearchParams();
      if (searchTerm) params.append('search', searchTerm);

      const res = await fetch(`/api/notification-templates/?${params}`, {
        credentials: 'include',
      });
      if (!res.ok) throw new Error('Failed to fetch templates');
      const data = await res.json();
      return Array.isArray(data) ? data : data.results || [];
    },
  });

  const saveTemplateMutation = useMutation({
    mutationFn: async (data: Partial<NotificationTemplate>) => {
      const method = editingTemplate ? 'PATCH' : 'POST';
      const url = editingTemplate ? `/api/notification-templates/${editingTemplate.id}/` : '/api/notification-templates/';

      const res = await fetch(url, {
        method,
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to save template');
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-notifications'] });
      setShowModal(false);
      setEditingTemplate(null);
    },
  });

  const handleCreateNew = () => {
    setEditingTemplate(null);
    setShowModal(true);
  };

  const handleEdit = (template: NotificationTemplate) => {
    setEditingTemplate(template);
    setShowModal(true);
  };

  const handleSave = async (formData: any) => {
    await saveTemplateMutation.mutateAsync(formData);
  };

  if (isLoading) return <LoadingSpinner />;

  return (
    <DashboardLayout>
      <div className="space-y-6">
        <div className="flex justify-between items-center">
          <div>
            <h1 className="text-3xl font-bold">Notification Templates</h1>
            <p className="text-gray-600">Manage email and SMS notification templates</p>
          </div>
          <Button onClick={handleCreateNew} className="flex items-center gap-2">
            <Plus className="h-4 w-4" /> New Template
          </Button>
        </div>

        <Card className="p-4">
          <Input
            placeholder="Search templates..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </Card>

        <div className="space-y-4">
          {templates.length === 0 ? (
            <div className="text-center py-12">
              <Bell className="h-12 w-12 mx-auto text-gray-400 mb-4" />
              <p className="text-gray-500">No notification templates found</p>
            </div>
          ) : (
            templates.map((template: NotificationTemplate) => (
              <Card key={template.id} className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <div>
                    <h3 className="text-lg font-semibold">{template.name}</h3>
                    <p className="text-sm text-gray-600">{template.trigger_event}</p>
                  </div>
                  <div className="flex gap-2">
                    {template.channels.includes('email') && (
                      <Mail className="h-5 w-5 text-blue-600" />
                    )}
                    {template.channels.includes('sms') && (
                      <MessageSquare className="h-5 w-5 text-green-600" />
                    )}
                    {!template.is_active && (
                      <span className="px-2 py-1 bg-red-100 text-red-800 text-xs font-semibold rounded">
                        Inactive
                      </span>
                    )}
                  </div>
                </div>

                <div className="mb-4">
                  {template.email_subject && (
                    <p className="text-sm text-gray-700 mb-2">
                      <strong>Email Subject:</strong> {template.email_subject}
                    </p>
                  )}
                  {template.sms_body && (
                    <p className="text-sm text-gray-700 line-clamp-2">
                      <strong>SMS:</strong> {template.sms_body}
                    </p>
                  )}
                </div>

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => handleEdit(template)}
                >
                  <Edit2 className="h-4 w-4 mr-2" /> Edit
                </Button>
              </Card>
            ))
          )}
        </div>

        {showModal && (
          <NotificationFormModal
            template={editingTemplate}
            onSave={handleSave}
            onClose={() => {
              setShowModal(false);
              setEditingTemplate(null);
            }}
            isLoading={saveTemplateMutation.isPending}
          />
        )}
      </div>
    </DashboardLayout>
  );
}

function NotificationFormModal({
  template,
  onSave,
  onClose,
  isLoading,
}: {
  template: NotificationTemplate | null;
  onSave: (data: any) => Promise<void>;
  onClose: () => void;
  isLoading?: boolean;
}) {
  const [formData, setFormData] = useState({
    name: template?.name || '',
    trigger_event: template?.trigger_event || '',
    channels: template?.channels || ['email'],
    email_subject: template?.email_subject || '',
    email_body: template?.email_body || '',
    sms_body: template?.sms_body || '',
  });

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    await onSave(formData);
  };

  const toggleChannel = (channel: string) => {
    setFormData((prev) => ({
      ...prev,
      channels: prev.channels.includes(channel)
        ? prev.channels.filter((c) => c !== channel)
        : [...prev.channels, channel],
    }));
  };

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
      <div className="bg-white rounded-lg max-w-md w-full mx-4 p-6 max-h-[90vh] overflow-y-auto">
        <div className="flex justify-between items-center mb-4">
          <h2 className="text-lg font-semibold">
            {template ? 'Edit Template' : 'Create Template'}
          </h2>
          <button
            onClick={onClose}
            className="text-gray-500 hover:text-gray-700"
          >
            <X className="h-5 w-5" />
          </button>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <Input
            label="Template Name"
            value={formData.name}
            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
            required
          />

          <Input
            label="Trigger Event"
            value={formData.trigger_event}
            onChange={(e) => setFormData({ ...formData, trigger_event: e.target.value })}
            required
            placeholder="e.g., approval_submitted, user_invited"
          />

          <div>
            <label className="block text-sm font-semibold mb-2">Notification Channels</label>
            <div className="space-y-2">
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.channels.includes('email')}
                  onChange={() => toggleChannel('email')}
                  className="rounded"
                />
                <span className="ml-3">Email</span>
              </label>
              <label className="flex items-center">
                <input
                  type="checkbox"
                  checked={formData.channels.includes('sms')}
                  onChange={() => toggleChannel('sms')}
                  className="rounded"
                />
                <span className="ml-3">SMS</span>
              </label>
            </div>
          </div>

          {formData.channels.includes('email') && (
            <>
              <Input
                label="Email Subject"
                value={formData.email_subject}
                onChange={(e) => setFormData({ ...formData, email_subject: e.target.value })}
              />

              <div>
                <label className="block text-sm font-semibold mb-2">Email Body</label>
                <textarea
                  value={formData.email_body}
                  onChange={(e) => setFormData({ ...formData, email_body: e.target.value })}
                  className="w-full px-3 py-2 border border-gray-300 rounded-md"
                  rows={6}
                />
              </div>
            </>
          )}

          {formData.channels.includes('sms') && (
            <div>
              <label className="block text-sm font-semibold mb-2">SMS Message</label>
              <textarea
                value={formData.sms_body}
                onChange={(e) => setFormData({ ...formData, sms_body: e.target.value })}
                className="w-full px-3 py-2 border border-gray-300 rounded-md"
                rows={4}
                placeholder="Keep under 160 characters"
              />
              <p className="text-xs text-gray-500 mt-1">Characters: {formData.sms_body.length}</p>
            </div>
          )}

          <div className="grid grid-cols-2 gap-4">
            <Button type="submit" disabled={isLoading} className="w-full">
              {isLoading ? 'Saving...' : 'Save'}
            </Button>
            <Button variant="outline" onClick={onClose} className="w-full">
              Cancel
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
