# 🚀 COMS Frontend - Quick Start Guide

Get the COMS frontend up and running in 5 minutes!

---

## Prerequisites

Before you begin, ensure you have:

- ✅ **Node.js 18+** installed ([Download](https://nodejs.org/))
- ✅ **npm** or **yarn** package manager
- ✅ **Django backend** running at `http://localhost:8000`
- ✅ Backend user account with credentials

---

## Installation Steps

### Step 1: Navigate to Frontend Directory

```bash
cd "c:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS\frontend"
```

### Step 2: Install Dependencies

```bash
npm install
```

This will install all required packages (~300MB):
- Next.js 14
- React 18
- TypeScript
- Tailwind CSS
- Zustand
- Axios
- React Query
- And more...

**Expected time:** 2-3 minutes

### Step 3: Configure Environment

```bash
# Copy the example environment file
copy .env.local.example .env.local
```

Edit `.env.local` and update with your settings:

```env
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws

# Token Configuration (optional - using defaults)
NEXT_PUBLIC_ACCESS_TOKEN_EXPIRE=86400
NEXT_PUBLIC_REFRESH_TOKEN_EXPIRE=604800
```

### Step 4: Start Development Server

```bash
npm run dev
```

You should see:
```
ready - started server on 0.0.0.0:3000, url: http://localhost:3000
event - compiled client and server successfully
```

### Step 5: Access the Application

Open your browser and navigate to:

**🌐 http://localhost:3000**

You will be automatically redirected to the login page.

---

## First Login

### Default Test Credentials

Use your Django backend user credentials. If you don't have any, create one in Django admin or use:

```
Username: admin
Password: [your admin password]
```

### What Happens After Login

1. **JWT Token Generated**: Backend creates access + refresh tokens
2. **Tokens Stored**: Saved securely in cookies
3. **User Data Cached**: User profile stored in localStorage
4. **Redirect to Dashboard**: Automatically navigated to `/dashboard`
5. **Permissions Loaded**: User roles and permissions fetched

---

## Navigating the Application

### Main Sections

| Section | Route | Description |
|---------|-------|-------------|
| Dashboard | `/dashboard` | Overview with KPIs and stats |
| Projects | `/projects` | Project list and management |
| Variations | `/variations` | Variation orders (coming soon) |
| Claims | `/claims` | Claims/valuations (coming soon) |
| Documents | `/documents` | Document library (coming soon) |
| Procurement | `/procurement` | Purchase orders (coming soon) |
| Reports | `/reports` | Report generation (coming soon) |

### Testing Features

#### 1. Test Authentication
- Login with valid credentials ✅
- Verify automatic redirect to dashboard ✅
- Check user menu in topbar ✅
- Logout and verify redirect to login ✅

#### 2. Test Dashboard
- View KPI cards (projects, budget, approvals, issues) ✅
- Check recent projects list ✅
- Verify progress bars display correctly ✅

#### 3. Test Projects
- Navigate to Projects page ✅
- Search for projects using search bar ✅
- Sort by clicking column headers ✅
- Click on a project row ✅

#### 4. Test Permissions
- Login with different user roles ✅
- Verify menu items appear based on permissions ✅
- Check that unauthorized features are hidden ✅

---

## Common Issues & Solutions

### Issue: Port 3000 already in use

**Solution:**
```bash
# Use a different port
npm run dev -- -p 3001
```

Then access: http://localhost:3001

---

### Issue: API connection errors

**Symptoms:** "Network Error" or "Failed to fetch"

**Solution:**

1. Verify Django backend is running:
```bash
# In backend directory
python manage.py runserver
```

2. Check API URL in `.env.local`:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
```

3. Test API manually:
```bash
curl http://localhost:8000/api/auth/me/
```

---

### Issue: Login fails with "Invalid credentials"

**Solutions:**

1. **Create a Django user:**
```bash
# In Django backend
python manage.py createsuperuser
```

2. **Verify credentials** in Django admin:
http://localhost:8000/admin

3. **Check backend logs** for authentication errors

---

### Issue: Blank page after login

**Solutions:**

1. Open browser DevTools (F12)
2. Check Console for errors
3. Verify tokens were stored:
   - Application → Cookies → Check for `access_token`
   - Application → Local Storage → Check for `auth-storage`

4. Clear browser cache and cookies:
```javascript
// In DevTools Console
localStorage.clear();
document.cookie.split(";").forEach(c => {
  document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
});
location.reload();
```

---

### Issue: Styles not loading / Page looks broken

**Solutions:**

1. Ensure Tailwind CSS is compiling:
```bash
# Should see "compiled successfully" in terminal
```

2. Clear Next.js cache:
```bash
rm -rf .next
npm run dev
```

3. Verify `globals.css` is imported in `app/layout.tsx`

---

## Development Workflow

### File Structure Overview

```
frontend/
├── app/                    # Pages (Next.js App Router)
│   ├── layout.tsx         # Root layout
│   ├── page.tsx           # Home (redirects)
│   ├── login/             # Login page
│   ├── dashboard/         # Dashboard page
│   └── projects/          # Projects page
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── layout/           # Sidebar, Topbar, Layout
├── services/             # API services (11 services)
├── hooks/                # Custom hooks (6 hooks)
├── store/                # Zustand stores (4 stores)
├── utils/                # Utilities (formatters, helpers)
└── types/                # TypeScript types
```

### Making Changes

#### Adding a New Page

1. Create page file:
```bash
# Create new page
mkdir app/my-page
touch app/my-page/page.tsx
```

2. Add page content:
```typescript
'use client';

import { DashboardLayout } from '@/components/layout';

export default function MyPage() {
  return (
    <DashboardLayout>
      <h1>My New Page</h1>
    </DashboardLayout>
  );
}
```

3. Add to sidebar navigation (in `utils/constants.ts`):
```typescript
{
  label: 'My Page',
  path: '/my-page',
  icon: FolderIcon,
  permission: 'MY_PERMISSION',
}
```

#### Creating a New Component

```typescript
// components/ui/MyComponent.tsx
import React from 'react';

export interface MyComponentProps {
  title: string;
}

export const MyComponent: React.FC<MyComponentProps> = ({ title }) => {
  return <div>{title}</div>;
};
```

#### Adding a New Service

```typescript
// services/myService.ts
import { api } from './apiClient';
import type { MyType } from '@/types';

export const myService = {
  async getItems(): Promise<MyType[]> {
    return await api.get('/my-endpoint/');
  },
};
```

---

## Testing Checklist

Before considering the setup complete, verify:

- [ ] Login page loads without errors
- [ ] Can login with valid credentials
- [ ] Dashboard displays with KPI cards
- [ ] Sidebar navigation is visible
- [ ] User menu works (top-right)
- [ ] Can navigate to different pages
- [ ] Logout redirects to login
- [ ] Token refresh works (check DevTools Network)
- [ ] Search in Projects page works
- [ ] Table sorting works
- [ ] Responsive design works (resize browser)
- [ ] Toast notifications appear
- [ ] Loading states display correctly

---

## Production Build

When ready for production:

### Build the Application

```bash
npm run build
```

This creates an optimized production build in `.next/` directory.

### Start Production Server

```bash
npm start
```

Production server runs on http://localhost:3000

### Deploy Options

- **Vercel** (Recommended for Next.js): One-click deployment
- **Docker**: Use provided Dockerfile
- **Traditional Server**: Build and serve `.next` directory

---

## Getting Help

### Documentation

- **Frontend README**: `frontend/README.md`
- **Implementation Summary**: `frontend/IMPLEMENTATION_SUMMARY.md`
- **This Quick Start**: `frontend/QUICK_START.md`

### Debugging

Enable detailed logging in `.env.local`:
```env
NEXT_PUBLIC_DEBUG=true
```

Check browser DevTools:
- **Console**: JavaScript errors
- **Network**: API requests/responses
- **Application**: Cookies and localStorage

---

## Next Steps

After successful setup:

1. **Explore the codebase** - Familiarize yourself with the structure
2. **Test all features** - Login, navigation, permissions
3. **Customize the UI** - Update colors, logos, branding
4. **Add more pages** - Variations, Claims, Documents
5. **Connect real data** - Integrate with backend APIs
6. **Deploy** - Push to production when ready

---

## Quick Reference

### Useful Commands

```bash
# Development
npm run dev              # Start dev server
npm run build            # Build for production
npm run start            # Start production server
npm run lint             # Run ESLint

# Maintenance
rm -rf node_modules      # Remove dependencies
npm install              # Reinstall dependencies
rm -rf .next             # Clear build cache
```

### Default Ports

- Frontend: `http://localhost:3000`
- Backend API: `http://localhost:8000`
- Backend Admin: `http://localhost:8000/admin`

### Important Files

- **Configuration**: `package.json`, `tsconfig.json`, `tailwind.config.ts`
- **Environment**: `.env.local`
- **Entry Point**: `app/layout.tsx`, `app/page.tsx`
- **API Client**: `services/apiClient.ts`
- **Auth Logic**: `services/authService.ts`, `hooks/useAuth.ts`

---

## Success! 🎉

You now have a fully functional COMS frontend running!

**What you have:**
- ✅ Modern Next.js 14 application
- ✅ Complete TypeScript type safety
- ✅ JWT authentication with auto-refresh
- ✅ RBAC permission system
- ✅ Professional UI component library
- ✅ Responsive layout system
- ✅ Real-time notifications
- ✅ Production-ready architecture

**Ready for:**
- 🚀 Adding more features
- 🎨 Customizing the design
- 📊 Connecting to backend
- 🌐 Deploying to production

---

**Happy coding! 💻**

For questions or issues, refer to the documentation or check the implementation summary for detailed technical information.
