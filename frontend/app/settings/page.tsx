'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function SettingsPage() {
  const router = useRouter();

  useEffect(() => {
    // Redirect to profile page by default
    router.push('/settings/profile');
  }, [router]);

  return null;
}
