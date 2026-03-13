'use client';

import React from 'react';
import { FileText, Image as ImageIcon } from 'lucide-react';
import type { Document } from '@/types';

interface DocumentPreviewProps {
  document: Document;
}

export function DocumentPreview({ document }: DocumentPreviewProps) {
  const fileUrl = document.file_url || document.file;
  const ext = (document.file_extension || document.file_name?.split('.').pop() || '').toLowerCase();

  if (!fileUrl) {
    return (
      <div className="h-72 border border-dashed border-gray-300 rounded-lg flex items-center justify-center text-gray-500">
        No preview available
      </div>
    );
  }

  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-200">
        {/* Using img for direct file previews from API URLs */}
        <img src={fileUrl} alt={document.title} className="w-full max-h-[30rem] object-contain bg-gray-50" />
      </div>
    );
  }

  if (ext === 'pdf') {
    return (
      <div className="rounded-lg overflow-hidden border border-gray-200 h-[34rem]">
        <iframe title={document.title} src={fileUrl} className="w-full h-full" />
      </div>
    );
  }

  return (
    <div className="h-72 border border-gray-200 rounded-lg flex flex-col items-center justify-center text-gray-500 gap-3">
      {['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext) ? (
        <ImageIcon className="h-10 w-10" />
      ) : (
        <FileText className="h-10 w-10" />
      )}
      <p className="text-sm">Preview not supported for this file type</p>
    </div>
  );
}
