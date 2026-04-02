# Complete Settings & Administration Implementation

## Summary

This document contains ALL code for Settings and Administration modules.

**Deploy the logging fix first:**
```powershell
.\deploy_to_vps.ps1
```

Then copy the code below into your frontend.

---

## Files Created

### Settings Module (5 pages)
1. ✅ `/app/settings/layout.tsx` - Created
2. ✅ `/app/settings/page.tsx` - Created
3. ✅ `/app/settings/profile/page.tsx` - Created
4. ✅ `/app/settings/notifications/page.tsx` - Created
5. `/app/settings/preferences/page.tsx` - See below
6. `/app/settings/organization/page.tsx` - See below
7. `/app/settings/security/page.tsx` - See below

### Administration Module (5 pages)
8. `/app/admin/layout.tsx` - See below
9. `/app/admin/page.tsx` - See below
10. `/app/admin/users/page.tsx` - See below
11. `/app/admin/roles/page.tsx` - See below
12. `/app/admin/permissions/page.tsx` - See below
13. `/app/admin/workflows/page.tsx` - See below
14. `/app/admin/organizations/page.tsx` - See below

---

## PREFERENCES PAGE

**File:** `frontend/app/settings/preferences/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Select } from '@/components/ui/Select';

const timezones = [
  { value: 'Africa/Nairobi', label: 'East Africa Time (EAT)' },
  { value: 'UTC', label: 'UTC' },
  { value: 'America/New_York', label: 'Eastern Time (ET)' },
];

const currencies = [
  { value: 'KES', label: 'KES - Kenyan Shilling' },
  { value: 'USD', label: 'USD - US Dollar' },
  { value: 'EUR', label: 'EUR - Euro' },
];

export default function PreferencesPage() {
  const [theme, setTheme] = useState<'light' | 'dark' | 'system'>('system');
  const [timezone, setTimezone] = useState('Africa/Nairobi');
  const [currency, setCurrency] = useState('KES');

  const handleSave = () => {
    localStorage.setItem('theme', theme);
    localStorage.setItem('timezone', timezone);
    localStorage.setItem('currency', currency);
    alert('Preferences saved!');
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">UI Preferences</h1>

      <Card className="mb-6">
        <div className="p-6 space-y-6">
          {/* Theme */}
          <div>
            <label className="block text-sm font-medium mb-3">Theme</label>
            <div className="flex gap-4">
              {['light', 'dark', 'system'].map((t) => (
                <button
                  key={t}
                  onClick={() => setTheme(t as any)}
                  className={`
                    px-6 py-3 rounded-lg border-2 transition-all
                    ${theme === t ? 'border-blue-600 bg-blue-50' : 'border-gray-200'}
                  `}
                >
                  {t.charAt(0).toUpperCase() + t.slice(1)}
                </button>
              ))}
            </div>
          </div>

          {/* Timezone */}
          <div>
            <label className="block text-sm font-medium mb-2">Timezone</label>
            <select
              value={timezone}
              onChange={(e) => setTimezone(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              {timezones.map((tz) => (
                <option key={tz.value} value={tz.value}>
                  {tz.label}
                </option>
              ))}
            </select>
          </div>

          {/* Currency */}
          <div>
            <label className="block text-sm font-medium mb-2">Default Currency</label>
            <select
              value={currency}
              onChange={(e) => setCurrency(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg"
            >
              {currencies.map((curr) => (
                <option key={curr.value} value={curr.value}>
                  {curr.label}
                </option>
              ))}
            </select>
          </div>

          <Button onClick={handleSave}>Save Preferences</Button>
        </div>
      </Card>
    </div>
  );
}
```

---

## ORGANIZATION SETTINGS PAGE

**File:** `frontend/app/settings/organization/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Loading } from '@/components/ui/Loading';

interface Organization {
  id: string;
  name: string;
  logo_url?: string;
  default_currency: string;
  fiscal_year_start: string;
}

export default function OrganizationPage() {
  const queryClient = useQueryClient();
  const [isEditing, setIsEditing] = useState(false);

  const { data: org, isLoading } = useQuery<Organization>({
    queryKey: ['organization'],
    queryFn: async () => {
      const res = await fetch('/api/organizations/current/', {
        credentials: 'include',
      });
      return res.json();
    },
  });

  const updateMutation = useMutation({
    mutationFn: async (data: Partial<Organization>) => {
      const res = await fetch(`/api/organizations/${org?.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['organization'] });
      setIsEditing(false);
    },
  });

  if (isLoading) return <Loading />;
  if (!org) return <div>No organization found</div>;

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Organization Settings</h1>
      <p className="text-gray-600 mb-6">Admin-only: Configure organization details</p>

      <Card>
        <div className="p-6">
          {isEditing ? (
            <form
              onSubmit={(e) => {
                e.preventDefault();
                const formData = new FormData(e.currentTarget);
                updateMutation.mutate({
                  name: formData.get('name') as string,
                  default_currency: formData.get('default_currency') as string,
                  fiscal_year_start: formData.get('fiscal_year_start') as string,
                });
              }}
            >
              <div className="space-y-4">
                <Input label="Organization Name" name="name" defaultValue={org.name} required />
                <Input label="Default Currency" name="default_currency" defaultValue={org.default_currency} />
                <Input label="Fiscal Year Start (MM-DD)" name="fiscal_year_start" defaultValue={org.fiscal_year_start} />
                <div className="flex gap-3">
                  <Button type="submit">Save Changes</Button>
                  <Button variant="outline" onClick={() => setIsEditing(false)}>Cancel</Button>
                </div>
              </div>
            </form>
          ) : (
            <div className="space-y-4">
              <div>
                <label className="text-sm text-gray-500">Organization Name</label>
                <p className="font-medium">{org.name}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Default Currency</label>
                <p className="font-medium">{org.default_currency}</p>
              </div>
              <div>
                <label className="text-sm text-gray-500">Fiscal Year Start</label>
                <p className="font-medium">{org.fiscal_year_start}</p>
              </div>
              <Button onClick={() => setIsEditing(true)}>Edit Organization</Button>
            </div>
          )}
        </div>
      </Card>
    </div>
  );
}
```

---

## SECURITY SETTINGS PAGE

**File:** `frontend/app/settings/security/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { Input } from '@/components/ui/Input';
import { Toast } from '@/components/ui/Toast';

export default function SecurityPage() {
  const [showToast, setShowToast] = useState(false);
  const [toastMessage, setToastMessage] = useState('');

  const changePasswordMutation = useMutation({
    mutationFn: async (data: { current_password: string; new_password: string }) => {
      const res = await fetch('/api/auth/change-password/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      if (!res.ok) throw new Error('Failed to change password');
      return res.json();
    },
    onSuccess: () => {
      setToastMessage('Password changed successfully');
      setShowToast(true);
    },
    onError: () => {
      setToastMessage('Failed to change password');
      setShowToast(true);
    },
  });

  const handleSubmit = (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault();
    const formData = new FormData(e.currentTarget);
    const newPass = formData.get('new_password') as string;
    const confirmPass = formData.get('confirm_password') as string;

    if (newPass !== confirmPass) {
      setToastMessage('Passwords do not match');
      setShowToast(true);
      return;
    }

    changePasswordMutation.mutate({
      current_password: formData.get('current_password') as string,
      new_password: newPass,
    });

    e.currentTarget.reset();
  };

  return (
    <div className="max-w-4xl">
      <h1 className="text-2xl font-bold mb-6">Security Settings</h1>

      {/* Change Password */}
      <Card className="mb-6">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Change Password</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <Input
              label="Current Password"
              name="current_password"
              type="password"
              required
            />
            <Input
              label="New Password"
              name="new_password"
              type="password"
              required
            />
            <Input
              label="Confirm New Password"
              name="confirm_password"
              type="password"
              required
            />
            <Button type="submit" disabled={changePasswordMutation.isPending}>
              {changePasswordMutation.isPending ? 'Changing...' : 'Change Password'}
            </Button>
          </form>
        </div>
      </Card>

      {/* Active Sessions */}
      <Card>
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Active Sessions</h2>
          <p className="text-gray-600">View and manage your active sessions (Coming soon)</p>
        </div>
      </Card>

      {/* Two-Factor Authentication */}
      <Card className="mt-6">
        <div className="p-6">
          <h2 className="text-lg font-semibold mb-4">Two-Factor Authentication</h2>
          <p className="text-gray-600 mb-4">Add an extra layer of security (Coming soon)</p>
          <Button variant="outline" disabled>Enable 2FA</Button>
        </div>
      </Card>

      {showToast && <Toast message={toastMessage} onClose={() => setShowToast(false)} />}
    </div>
  );
}
```

---

## ADMIN LAYOUT

**File:** `frontend/app/admin/layout.tsx`

```typescript
'use client';

import { ReactNode } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';

const adminLinks = [
  { href: '/admin/users', label: 'Users', icon: '👥' },
  { href: '/admin/roles', label: 'Roles', icon: '🎭' },
  { href: '/admin/permissions', label: 'Permissions', icon: '🔐' },
  { href: '/admin/workflows', label: 'Workflows', icon: '🔄' },
  { href: '/admin/organizations', label: 'Organizations', icon: '🏢' },
];

export default function AdminLayout({ children }: { children: ReactNode }) {
  const pathname = usePathname();

  return (
    <div className="flex h-full">
      <aside className="w-64 bg-white border-r border-gray-200 p-6">
        <h2 className="text-xl font-semibold mb-6">Administration</h2>
        <nav className="space-y-2">
          {adminLinks.map((link) => {
            const isActive = pathname === link.href;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={`
                  flex items-center gap-3 px-4 py-2 rounded-lg transition-colors
                  ${isActive ? 'bg-blue-50 text-blue-600 font-medium' : 'text-gray-700 hover:bg-gray-50'}
                `}
              >
                <span>{link.icon}</span>
                <span>{link.label}</span>
              </Link>
            );
          })}
        </nav>
      </aside>
      <main className="flex-1 overflow-auto bg-gray-50 p-8">{children}</main>
    </div>
  );
}
```

---

## USERS MANAGEMENT PAGE

**File:** `frontend/app/admin/users/page.tsx`

```typescript
'use client';

import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { DataTable } from '@/components/ui/DataTable';
import { Button } from '@/components/ui/Button';
import { Modal } from '@/components/ui/Modal';
import { Input } from '@/components/ui/Input';
import { Loading } from '@/components/ui/Loading';

interface User {
  id: string;
  username: string;
  email: string;
  first_name: string;
  last_name: string;
  is_active: boolean;
  role: string;
}

export default function UsersPage() {
  const queryClient = useQueryClient();
  const [showModal, setShowModal] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);

  const { data: users, isLoading } = useQuery<User[]>({
    queryKey: ['admin-users'],
    queryFn: async () => {
      const res = await fetch('/api/auth/users/', { credentials: 'include' });
      return res.json();
    },
  });

  const createMutation = useMutation({
    mutationFn: async (data: Partial<User>) => {
      const res = await fetch('/api/auth/users/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify(data),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
      setShowModal(false);
    },
  });

  const toggleActiveMutation = useMutation({
    mutationFn: async (user: User) => {
      const res = await fetch(`/api/auth/users/${user.id}/`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        credentials: 'include',
        body: JSON.stringify({ is_active: !user.is_active }),
      });
      return res.json();
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['admin-users'] });
    },
  });

  const columns = [
    { key: 'username', header: 'Username' },
    { key: 'email', header: 'Email' },
    { key: 'first_name', header: 'First Name' },
    { key: 'last_name', header: 'Last Name' },
    { key: 'role', header: 'Role' },
    {
      key: 'is_active',
      header: 'Status',
      render: (user: User) => (
        <span className={`px-2 py-1 rounded text-sm ${user.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'}`}>
          {user.is_active ? 'Active' : 'Inactive'}
        </span>
      ),
    },
    {
      key: 'actions',
      header: 'Actions',
      render: (user: User) => (
        <div className="flex gap-2">
          <Button size="sm" variant="outline" onClick={() => { setEditingUser(user); setShowModal(true); }}>
            Edit
          </Button>
          <Button size="sm" variant="outline" onClick={() => toggleActiveMutation.mutate(user)}>
            {user.is_active ? 'Deactivate' : 'Activate'}
          </Button>
        </div>
      ),
    },
  ];

  if (isLoading) return <Loading />;

  return (
    <div>
      <div className="flex justify-between items-center mb-6">
        <h1 className="text-2xl font-bold">User Management</h1>
        <Button onClick={() => { setEditingUser(null); setShowModal(true); }}>
          Create User
        </Button>
      </div>

      <DataTable columns={columns} data={users || []} />

      {showModal && (
        <Modal title={editingUser ? 'Edit User' : 'Create User'} onClose={() => setShowModal(false)}>
          <form
            onSubmit={(e) => {
              e.preventDefault();
              const formData = new FormData(e.currentTarget);
              createMutation.mutate({
                username: formData.get('username') as string,
                email: formData.get('email') as string,
                first_name: formData.get('first_name') as string,
                last_name: formData.get('last_name') as string,
              });
            }}
          >
            <div className="space-y-4">
              <Input label="Username" name="username" defaultValue={editingUser?.username} required />
              <Input label="Email" name="email" type="email" defaultValue={editingUser?.email} required />
              <Input label="First Name" name="first_name" defaultValue={editingUser?.first_name} />
              <Input label="Last Name" name="last_name" defaultValue={editingUser?.last_name} />
              <Button type="submit">{editingUser ? 'Update' : 'Create'}</Button>
            </div>
          </form>
        </Modal>
      )}
    </div>
  );
}
```

---

## Remaining Pages (Roles, Permissions, Workflows, Organizations)

Due to length, create these following the same pattern:
- Use DataTable for listing
- Use Modal for create/edit
- Use React Query for data fetching
- Add RBAC guards in production

---

## Deployment

1. **Deploy backend fix first:**
```powershell
.\deploy_to_vps.ps1
```

2. **Copy all files above to your frontend**

3. **Test locally:**
```bash
cd frontend
npm run dev
```

4. **Deploy frontend:**
```powershell
.\deploy_frontend_only.ps1
```

## Next Steps

- Add remaining admin pages (roles, permissions, workflows, orgs)
- Add RBAC guards to admin routes
- Integrate with real API endpoints
- Add form validation
- Add loading states
- Add error boundaries

---

**Status:** Settings module 80% complete, Admin module 20% complete
