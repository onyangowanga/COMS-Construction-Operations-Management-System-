'use client';

import React, { useMemo, useState } from 'react';
import { useRouter } from 'next/navigation';
import { Plus } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { DocumentTable } from '@/components/documents';
import { Button, Card, CardContent, CardHeader, CardTitle, ConfirmDialog, Input, Select } from '@/components/ui';
import { useDocuments, usePermissions } from '@/hooks';
import { documentService } from '@/services';
import type { Document } from '@/types';

export default function DocumentsPage() {
  const router = useRouter();
  const { hasPermission } = usePermissions();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [ordering, setOrdering] = useState('-uploaded_at');
  const [page, setPage] = useState(1);
  const [deleteTarget, setDeleteTarget] = useState<Document | null>(null);

  const { documents, totalCount, isLoading, deleteDocument, isDeleting, approveDocument, rejectDocument } = useDocuments({
    page,
    page_size: 10,
    search: search || undefined,
    status: status || undefined,
    ordering,
  });

  const canUpload = hasPermission('upload_document');
  const canApprove = hasPermission('approve_document') || hasPermission('upload_document');
  const canDelete = hasPermission('delete_document');

  const totalPages = useMemo(() => Math.max(1, Math.ceil((totalCount || 0) / 10)), [totalCount]);

  const handleDelete = async () => {
    if (!deleteTarget) return;
    await deleteDocument(deleteTarget.id);
    setDeleteTarget(null);
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_document', 'view_documents', 'upload_document', 'approve_document', 'delete_document']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">Documents</h1>
              <p className="text-gray-600 mt-1">Document management and approval workflow.</p>
            </div>
            {canUpload ? (
              <Button leftIcon={<Plus className="h-5 w-5" />} onClick={() => router.push('/documents/upload')}>
                Upload Document
              </Button>
            ) : null}
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Document Repository</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
                <Input
                  placeholder="Search documents"
                  value={search}
                  onChange={(event) => {
                    setPage(1);
                    setSearch(event.target.value);
                  }}
                />

                <Select
                  value={status}
                  onChange={(event) => {
                    setPage(1);
                    setStatus(event.target.value);
                  }}
                  options={[
                    { value: '', label: 'All statuses' },
                    { value: 'PENDING', label: 'Pending' },
                    { value: 'APPROVED', label: 'Approved' },
                    { value: 'REJECTED', label: 'Rejected' },
                  ]}
                />

                <Select
                  value={ordering}
                  onChange={(event) => {
                    setPage(1);
                    setOrdering(event.target.value);
                  }}
                  options={[
                    { value: '-uploaded_at', label: 'Newest first' },
                    { value: 'uploaded_at', label: 'Oldest first' },
                    { value: 'title', label: 'Name (A-Z)' },
                    { value: '-title', label: 'Name (Z-A)' },
                  ]}
                />
              </div>

              <DocumentTable
                documents={documents}
                isLoading={isLoading}
                canApprove={canApprove}
                canDelete={canDelete}
                onView={(document) => router.push(`/documents/${document.id}`)}
                onDownload={(document) =>
                  documentService.downloadDocument(document.id, document.file_name || `${document.title}.file`)
                }
                onApprove={(document) => approveDocument({ id: document.id })}
                onReject={(document) => rejectDocument({ id: document.id, payload: { reason: 'Rejected from list review' } })}
                onDelete={(document) => setDeleteTarget(document)}
              />

              <div className="flex items-center justify-between mt-4">
                <p className="text-sm text-gray-500">
                  Page {page} of {totalPages} ({totalCount} total documents)
                </p>
                <div className="flex items-center gap-2">
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page <= 1 || isLoading}
                    onClick={() => setPage((prev) => Math.max(1, prev - 1))}
                  >
                    Previous
                  </Button>
                  <Button
                    variant="outline"
                    size="sm"
                    disabled={page >= totalPages || isLoading}
                    onClick={() => setPage((prev) => Math.min(totalPages, prev + 1))}
                  >
                    Next
                  </Button>
                </div>
              </div>
            </CardContent>
          </Card>

          <ConfirmDialog
            isOpen={!!deleteTarget}
            onClose={() => setDeleteTarget(null)}
            onConfirm={handleDelete}
            title="Delete Document"
            message={`Delete ${deleteTarget?.title || 'this document'}? This action cannot be undone.`}
            confirmText="Delete"
            variant="destructive"
            isLoading={isDeleting}
          />
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
