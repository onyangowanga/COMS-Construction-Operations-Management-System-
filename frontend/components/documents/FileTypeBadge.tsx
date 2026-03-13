import React from 'react';
import { Badge } from '@/components/ui';

interface FileTypeBadgeProps {
  fileName?: string;
  fileType?: string;
  fileExtension?: string;
}

function getExtension({ fileName, fileType, fileExtension }: FileTypeBadgeProps): string {
  if (fileExtension) {
    return fileExtension.replace('.', '').toLowerCase();
  }

  if (fileName?.includes('.')) {
    return fileName.split('.').pop()?.toLowerCase() || 'file';
  }

  if (fileType?.includes('/')) {
    return fileType.split('/').pop()?.toLowerCase() || 'file';
  }

  return 'file';
}

function getVariant(ext: string): 'default' | 'primary' | 'success' | 'warning' | 'destructive' | 'secondary' {
  if (['pdf'].includes(ext)) return 'destructive';
  if (['doc', 'docx'].includes(ext)) return 'primary';
  if (['xls', 'xlsx', 'csv'].includes(ext)) return 'success';
  if (['png', 'jpg', 'jpeg', 'gif', 'webp'].includes(ext)) return 'warning';
  return 'default';
}

export function FileTypeBadge(props: FileTypeBadgeProps) {
  const ext = getExtension(props);

  return <Badge variant={getVariant(ext)}>{ext.toUpperCase()}</Badge>;
}
