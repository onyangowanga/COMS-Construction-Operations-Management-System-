'use client';

import React from 'react';
import { useParams, useRouter } from 'next/navigation';
import { Download, Trash2 } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { DocumentPreview, DocumentStatusBadge, FileTypeBadge } from '@/components/documents';
import { Badge, Button, Card, CardContent, CardHeader, CardTitle, ConfirmDialog, LoadingSpinner } from '@/components/ui';
import { useDocument, useDocuments, usePermissions } from '@/hooks';
import { documentService } from '@/services';
import { formatDate, formatFileSize } from '@/utils/formatters';

export default function DocumentDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { hasPermission } = usePermissions();
  const { document, isLoading } = useDocument(params?.id);
  const { deleteDocument, isDeleting } = useDocuments();
  const [deleteOpen, setDeleteOpen] = React.useState(false);

  const canDelete = hasPermission('delete_document');

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_document', 'view_documents', 'upload_document', 'approve_document', 'delete_document']}>
        {isLoading || !document ? (
          <div className="py-20 flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div>
                <h1 className="text-3xl font-bold text-gray-900">{document.title}</h1>
                <p className="text-gray-600 mt-1">Document details and preview</p>
              </div>
              <div className="flex items-center gap-2">
                <Button
                  variant="outline"
                  leftIcon={<Download className="h-4 w-4" />}
                  onClick={() =>
                    documentService.downloadDocument(document.id, document.file_name || `${document.title}.file`)
                  }
                >
                  Download
                </Button>
                {canDelete ? (
                  <Button variant="destructive" leftIcon={<Trash2 className="h-4 w-4" />} onClick={() => setDeleteOpen(true)}>
                    Delete
                  </Button>
                ) : null}
              </div>
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <Card className="xl:col-span-2">
                <CardHeader>
                  <CardTitle>Preview</CardTitle>
                </CardHeader>
                <CardContent>
                  <DocumentPreview document={document} />
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Metadata</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3 text-sm">
                  <div>
                    <p className="text-gray-500">Document Type</p>
                    <p className="text-gray-900">{document.document_type_display || document.document_type || 'N/A'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">File Type</p>
                    <FileTypeBadge fileName={document.file_name || document.title} fileType={document.file_type} fileExtension={document.file_extension} />
                  </div>
                  <div>
                    <p className="text-gray-500">Project</p>
                    <p className="text-gray-900">{document.project_name || 'General'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Uploaded By</p>
                    <p className="text-gray-900">{document.uploaded_by_name || 'System'}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Upload Date</p>
                    <p className="text-gray-900">{formatDate(document.uploaded_at)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Size</p>
                    <p className="text-gray-900">{formatFileSize(Number(document.file_size || 0))}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Status</p>
                    <DocumentStatusBadge status={document.status} isApproved={document.is_approved} />
                  </div>
                  {document.tags ? (
                    <div>
                      <p className="text-gray-500 mb-1">Tags</p>
                      <div className="flex flex-wrap gap-1">
                        {(Array.isArray(document.tags) ? document.tags : String(document.tags).split(',')).map((tag) => (
                          <Badge key={tag} variant="secondary">
                            {String(tag).trim()}
                          </Badge>
                        ))}
                      </div>
                    </div>
                  ) : null}
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Description</CardTitle>
              </CardHeader>
              <CardContent>
                <p className="text-gray-700">{document.description || 'No description provided.'}</p>
              </CardContent>
            </Card>
          </div>
        )}

        <ConfirmDialog
          isOpen={deleteOpen}
          onClose={() => setDeleteOpen(false)}
          onConfirm={async () => {
            if (!document) return;
            await deleteDocument(document.id);
            router.push('/documents');
          }}
          title="Delete Document"
          message="Are you sure you want to delete this document?"
          confirmText="Delete"
          variant="destructive"
          isLoading={isDeleting}
        />
      </PermissionGuard>
    </DashboardLayout>
  );
}
