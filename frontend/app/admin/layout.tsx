import React from 'react';
import { DashboardLayout } from '@/components/layout';

export default function AdminLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return <DashboardLayout>{children}</DashboardLayout>;
}