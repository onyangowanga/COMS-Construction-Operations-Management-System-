import React from 'react';
import { DashboardLayout } from '@/components/layout';

export default function SettingsLayout({
  children,
}: {
  children: React.ReactNode;
}): JSX.Element {
  return <DashboardLayout>{children}</DashboardLayout>;
}