'use client';

import React from 'react';
import { Download, Eye, Check, X, Trash2 } from 'lucide-react';
import { Button, DataTable, type Column } from '@/components/ui';
import { FileTypeBadge } from './FileTypeBadge';
import { DocumentStatusBadge } from './DocumentStatusBadge';
import { formatDate } from '@/utils/formatters';
import type { Document } from '@/types';

interface DocumentTableProps {
  documents: Document[];
  isLoading?: boolean;
  onView: (document: Document) => void;
  onDownload: (document: Document) => void;
  onApprove: (document: Document) => void;
  onReject: (document: Document) => void;
  onDelete: (document: Document) => void;
  canApprove?: boolean;
  canDelete?: boolean;
}

export function DocumentTable({
  documents,
  isLoading,
  onView,
  onDownload,
  onApprove,
  onReject,
  onDelete,
  canApprove = false,
  canDelete = false,
}: DocumentTableProps) {
  const columns: Column<Document>[] = [
    {
      key: 'title',
      title: 'File Name',
      sortable: true,
      render: (_value, row) => (
        <div>
          <p className="font-medium text-gray-900">{row.title}</p>
          <div className="mt-1">
            <FileTypeBadge fileName={row.file_name || row.title} fileType={row.file_type} fileExtension={row.file_extension} />
          </div>
        </div>
      ),
    },
    {
      key: 'document_type_display',
      title: 'Document Type',
      sortable: true,
      render: (value, row) => value || row.document_type || 'N/A',
    },
    {
      key: 'project_name',
      title: 'Project',
      sortable: true,
      render: (value) => value || 'General',
    },
    {
      key: 'uploaded_by_name',
      title: 'Uploaded By',
      sortable: true,
      render: (value) => value || 'System',
    },
    {
      key: 'uploaded_at',
      title: 'Upload Date',
      sortable: true,
      render: (value) => formatDate(value),
    },
    {
      key: 'status',
      title: 'Status',
      render: (_value, row) => <DocumentStatusBadge status={row.status} isApproved={row.is_approved} />,
    },
    {
      key: 'actions',
      title: 'Actions',
      width: '280px',
      render: (_value, row) => (
        <div className="flex flex-wrap items-center gap-2" onClick={(event) => event.stopPropagation()}>
          <Button variant="ghost" size="sm" leftIcon={<Eye className="h-4 w-4" />} onClick={() => onView(row)}>
            View
          </Button>
          <Button variant="outline" size="sm" leftIcon={<Download className="h-4 w-4" />} onClick={() => onDownload(row)}>
            Download
          </Button>
          {canApprove ? (
            <>
              <Button variant="primary" size="sm" leftIcon={<Check className="h-4 w-4" />} onClick={() => onApprove(row)}>
                Approve
              </Button>
              <Button variant="warning" size="sm" leftIcon={<X className="h-4 w-4" />} onClick={() => onReject(row)}>
                Reject
              </Button>
            </>
          ) : null}
          {canDelete ? (
            <Button variant="destructive" size="sm" leftIcon={<Trash2 className="h-4 w-4" />} onClick={() => onDelete(row)}>
              Delete
            </Button>
          ) : null}
        </div>
      ),
    },
  ];

  return (
    <DataTable
      data={documents}
      columns={columns}
      isLoading={isLoading}
      searchable={false}
      emptyMessage="No documents found"
      onRowClick={onView}
    />
  );
}
