'use client';

import React from 'react';
import { usePermissions } from '@/hooks';

interface PermissionGuardProps {
  permission: string | string[];
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

export function PermissionGuard({ permission, fallback, children }: PermissionGuardProps) {
  const { hasPermission, hasAnyPermission } = usePermissions();

  const hasAccess = Array.isArray(permission)
    ? hasAnyPermission(permission)
    : hasPermission(permission);

  const defaultFallback = (
    <div className="p-6">
      <div className="max-w-2xl rounded-lg border border-amber-200 bg-amber-50 p-5">
        <h2 className="text-lg font-semibold text-amber-900">Access Required</h2>
        <p className="mt-2 text-sm text-amber-800">
          You are signed in, but your account does not have permission to view this page yet.
          Contact your administrator to assign the required module permissions.
        </p>
      </div>
    </div>
  );

  if (!hasAccess) {
    return <>{fallback ?? defaultFallback}</>;
  }

  return <>{children}</>;
}
