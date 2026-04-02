'use client';

import { useRouter } from 'next/navigation';
import { useEffect } from 'react';

export default function SystemAdminPage() {
  const router = useRouter();

  useEffect(() => {
    router.push('/system-admin/users');
  }, [router]);

  return null;
}
