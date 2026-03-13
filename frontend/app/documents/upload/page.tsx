'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { DocumentUploadForm } from '@/components/documents';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { useDocuments } from '@/hooks';
import type { DocumentUploadInput } from '@/types';

export default function UploadDocumentPage() {
  const router = useRouter();
  const { uploadDocument, isUploading } = useDocuments();

  const handleUpload = async (values: DocumentUploadInput) => {
    await uploadDocument({ payload: values });
    router.push('/documents');
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission="upload_document">
        <div className="space-y-6">
          <div>
            <h1 className="text-3xl font-bold text-gray-900">Upload Document</h1>
            <p className="text-gray-600 mt-1">Upload and classify project documents.</p>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Document Upload</CardTitle>
            </CardHeader>
            <CardContent>
              <DocumentUploadForm onSubmit={handleUpload} onCancel={() => router.push('/documents')} isSubmitting={isUploading} />
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
