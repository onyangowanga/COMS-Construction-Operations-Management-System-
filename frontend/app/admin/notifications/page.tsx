'use client';

import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { LoadingSpinner } from '@/components/ui/Loading';
import { Badge } from '@/components/ui/Badge';

interface NotificationTemplate {
  id: string;
  name: string;
  code: string;
  channel: 'email' | 'sms' | 'in_app';
  subject?: string;
  body_template: string;
  trigger: string;
  is_active: boolean;
  variables: string[];
}

export default function NotificationTemplatesPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingTemplate, setEditingTemplate] = useState<NotificationTemplate | null>(null);
  const [previewTemplate, setPreviewTemplate] = useState<NotificationTemplate | null>(null);

  const { data: templates, isLoading } = useQuery<NotificationTemplate[]>({
    queryKey: ['notification-templates'],
    queryFn: async () => {
      const res = await fetch('/api/notifications/templates/', { credentials: 'include' });
      return res.json();
    },
  });

  const updateMutation = useMutation({
    mutationFn: async ({ id, data }: { id: string; data: Partial<NotificationTemplate> }) => {
      const res = await fetch(`/api/notifications/templates/${id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-templates'] });
      setShowModal(false);
      setEditingTemplate(null);
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async (template: NotificationTemplate) => {
      const res = await fetch(`/api/notifications/templates/${template.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ is_active: !template.is_active }),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['notification-templates'] });
    },
  });

  const columns = [
    {
      key: 'name',
      title: 'Template Name',
      render: (tmpl: NotificationTemplate) => (
        <div>
          <div className="font-medium">{tmpl.name}</div>
          <code className="text-xs text-gray-500">{tmpl.code}</code>
        </div>
      ),
    },
    {
      key: 'channel',
      title: 'Channel',
      render: (tmpl: NotificationTemplate) => {
        const channelColors = {
          email: 'primary',
          sms: 'success',
          in_app: 'secondary',
        };
        return (
          <Badge variant={channelColors[tmpl.channel] as any}>
            {tmpl.channel.toUpperCase()}
          </Badge>
        );
      },
    },
    {
      key: 'trigger',
      title: 'Trigger Event',
      render: (tmpl: NotificationTemplate) => (
        <span className="text-sm">{tmpl.trigger}</span>
      ),
    },
    {
      key: 'variables',
      title: 'Variables',
      render: (tmpl: NotificationTemplate) => (
        <div className="flex gap-1 flex-wrap">
          {tmpl.variables.slice(0, 3).map((v) => (
            <code key={v} className="text-xs bg-gray-100 px-1 py-0.5 rounded">
              {v}
            </code>
          ))}
          {tmpl.variables.length > 3 && (
            <span className="text-xs text-gray-500">+{tmpl.variables.length - 3}</span>
          )}
        </div>
      ),
    },
    {
      key: 'is_active',
      title: 'Status',
      render: (tmpl: NotificationTemplate) => (
        <Badge variant={tmpl.is_active ? 'success' : 'default'}>
          {tmpl.is_active ? 'Active' : 'Inactive'}
        </Badge>
      ),
    },
    {
      key: 'actions',
      title: 'Actions',
      render: (tmpl: NotificationTemplate) => (
        <div className="flex gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={() => setPreviewTemplate(tmpl)}
          >
            Preview
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => {
              setEditingTemplate(tmpl);
              setShowModal(true);
            }}
          >
            Edit
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={() => toggleActiveMutation.mutate(tmpl)}
          >
            {tmpl.is_active ? 'Disable' : 'Enable'}
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
      <div className="mb-6">
        <h1 className="text-2xl font-bold">Notification Templates</h1>
        <p className="text-gray-600">Manage email, SMS, and in-app notification templates</p>
      </div>

      {/* Channel Stats */}
      <div className="grid grid-cols-3 gap-4 mb-6">
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-blue-600">
            {templates?.filter(t => t.channel === 'email').length || 0}
          </div>
          <div className="text-sm text-gray-600">Email Templates</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-green-600">
            {templates?.filter(t => t.channel === 'sms').length || 0}
          </div>
          <div className="text-sm text-gray-600">SMS Templates</div>
        </div>
        <div className="bg-white p-4 rounded-lg border">
          <div className="text-2xl font-bold text-purple-600">
            {templates?.filter(t => t.channel === 'in_app').length || 0}
          </div>
          <div className="text-sm text-gray-600">In-App Templates</div>
        </div>
      </div>

      <DataTable columns={columns} data={templates || []} />

      {/* Edit Template Modal */}
      {showModal && editingTemplate && (
        <Modal
          isOpen={showModal}
          title={`Edit Template: ${editingTemplate.name}`}
          onClose={() => {
            setShowModal(false);
            setEditingTemplate(null);
          }}
        >
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              updateMutation.mutate({
                id: editingTemplate.id,
                data: {
                  subject: formData.get('subject') as string,
                  body_template: formData.get('body_template') as string,
                },
              });
            }}
          >
            <div className="space-y-4">
              <div>
                <label className="block text-sm font-medium mb-1">Trigger Event</label>
                <Input value={editingTemplate.trigger} disabled />
              </div>

              <div>
                <label className="block text-sm font-medium mb-1">Channel</label>
                <Badge variant="primary">{editingTemplate.channel.toUpperCase()}</Badge>
              </div>

              {editingTemplate.channel === 'email' && (
                <Input
                  label="Subject Line"
                  name="subject"
                  defaultValue={editingTemplate.subject}
                  required
                  placeholder="e.g., Project Update: {{project_name}}"
                />
              )}

              <div>
                <label className="block text-sm font-medium mb-2">Template Body</label>
                <textarea
                  name="body_template"
                  defaultValue={editingTemplate.body_template}
                  className="w-full px-3 py-2 border rounded-lg font-mono text-sm"
                  rows={10}
                  required
                  placeholder="Use {{variable_name}} for dynamic content"
                />
              </div>

              <div>
                <label className="block text-sm font-medium mb-2">Available Variables</label>
                <div className="flex gap-2 flex-wrap">
                  {editingTemplate.variables.map((v) => (
                    <code
                      key={v}
                      className="text-xs bg-gray-100 px-2 py-1 rounded cursor-pointer hover:bg-gray-200"
                      onClick={() => {
                        navigator.clipboard.writeText(`{{${v}}}`);
                      }}
                    >
                      {`{{${v}}}`}
                    </code>
                  ))}
                </div>
                <p className="text-xs text-gray-500 mt-1">Click to copy variable</p>
              </div>

              <div className="flex gap-3 pt-4 border-t">
                <Button type="submit" disabled={updateMutation.isPending}>
                  Save Template
                </Button>
                <Button
                  type="button"
                  variant="outline"
                  onClick={() => {
                    setShowModal(false);
                    setEditingTemplate(null);
                  }}
                >
                  Cancel
                </Button>
              </div>
            </div>
          </form>
        </Modal>
      )}

      {/* Preview Template Modal */}
      {previewTemplate && (
        <Modal
          isOpen={!!previewTemplate}
          title={`Preview: ${previewTemplate.name}`}
          onClose={() => setPreviewTemplate(null)}
        >
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-500">Channel</label>
              <Badge variant="primary">{previewTemplate.channel.toUpperCase()}</Badge>
            </div>

            {previewTemplate.subject && (
              <div>
                <label className="block text-sm font-medium text-gray-500">Subject</label>
                <p className="font-medium">{previewTemplate.subject}</p>
              </div>
            )}

            <div>
              <label className="block text-sm font-medium text-gray-500">Body</label>
              <div className="bg-gray-50 p-4 rounded-lg border">
                <pre className="whitespace-pre-wrap text-sm">{previewTemplate.body_template}</pre>
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-500">Variables Used</label>
              <div className="flex gap-2 flex-wrap">
                {previewTemplate.variables.map((v) => (
                  <code key={v} className="text-xs bg-blue-100 text-blue-800 px-2 py-1 rounded">
                    {`{{${v}}}`}
                  </code>
                ))}
              </div>
            </div>
          </div>
        </Modal>
      )}
    </div>
  );
}
