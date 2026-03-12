# COMS Frontend

Professional Next.js frontend for the COMS (Construction Management System) platform.

## Tech Stack

- **Framework**: Next.js 14 (App Router)
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **State Management**: Zustand
- **API Client**: Axios
- **Data Fetching**: TanStack Query (React Query)
- **Forms**: React Hook Form + Zod
- **Charts**: Recharts
- **Icons**: Lucide React

## Project Structure

```
frontend/
├── app/                    # Next.js App Router pages
│   ├── layout.tsx         # Root layout with providers
│   ├── page.tsx           # Home page
│   ├── login/             # Authentication pages
│   ├── dashboard/         # Dashboard page
│   └── projects/          # Project management pages
├── components/            # React components
│   ├── ui/               # Reusable UI components
│   └── layout/           # Layout components (Sidebar, Topbar)
├── services/             # API services
├── hooks/                # Custom React hooks
├── store/                # Zustand state stores
├── utils/                # Utility functions
└── types/                # TypeScript type definitions
```

## Getting Started

### Prerequisites

- Node.js 18+ and npm/yarn
- Backend API running at http://localhost:8000

### Installation

1. Install dependencies:
```bash
npm install
```

2. Copy environment file:
```bash
cp .env.local.example .env.local
```

3. Update `.env.local` with your configuration:
```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
```

### Development

Run the development server:
```bash
npm run dev
```

Open [http://localhost:3000](http://localhost:3000) in your browser.

### Build

Build for production:
```bash
npm run build
```

Start production server:
```bash
npm start
```

## Features

### Authentication
- JWT-based authentication with automatic token refresh
- Secure cookie storage for tokens
- Role-based access control (RBAC)

### Dashboard
- Real-time project statistics
- Activity feed
- Notification system
- Responsive design

### Project Management
- Project CRUD operations
- Progress tracking
- Document management
- Budget monitoring

### Variations & Claims
- Variation order workflow
- Claim/valuation processing
- Approval workflows
- Status tracking

### Procurement
- Purchase order management
- Supplier tracking
- Budget allocation

### Reports
- Report generation
- Custom parameters
- Export functionality
- Scheduled reports

## State Management

### Zustand Stores

- **authStore**: User authentication and session
- **uiStore**: UI state (sidebar, theme, toasts, modals)
- **projectStore**: Project data and operations
- **notificationStore**: Notifications and alerts

## API Integration

All API calls are centralized in the `services/` directory:

- **apiClient**: Axios instance with interceptors
- **authService**: Authentication endpoints
- **permissionService**: RBAC permission checks
- **projectService**: Project management
- **variationService**: Variation orders
- **claimService**: Claims/valuations
- **documentService**: Document operations
- **reportService**: Report generation

## Components

### UI Components

- Button, Input, Select, Textarea
- Card, Badge, Modal
- DataTable with sorting and search
- Loading skeletons
- Toast notifications

### Layout Components

- **Sidebar**: Navigation with permission-based menu
- **Topbar**: User menu and notifications
- **DashboardLayout**: Main layout wrapper

## Custom Hooks

- **useAuth**: Authentication operations
- **usePermissions**: Permission checking
- **useToast**: Toast notifications
- **useApi**: React Query wrapper
- **useProjects**: Project data management
- **useNotifications**: Notification handling

## Type Safety

Complete TypeScript coverage with types for:
- API responses
- User and auth data
- Projects, variations, claims
- Documents, reports
- Permissions and roles

## Styling

Tailwind CSS with custom configuration:
- Custom color palette
- Responsive breakpoints
- Dark mode support
- Custom animations

## Security

- JWT tokens in HTTP-only cookies
- CSRF protection
- XSS prevention
- Permission-based UI rendering
- Secure API communication

## Contributing

1. Follow TypeScript best practices
2. Use existing UI components
3. Implement error handling
4. Add loading states
5. Test with different user roles

## License

Copyright © 2024 COMS. All rights reserved.
