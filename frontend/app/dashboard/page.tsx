// ============================================================================
// DASHBOARD PAGE
// Main dashboard with KPIs, charts, and activity feed
// ============================================================================

'use client';

import React, { useMemo } from 'react';
import Link from 'next/link';
import { DashboardLayout } from '@/components/layout';
import { ActivityItem } from '@/components/activity';
import { NotificationItem } from '@/components/notifications';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { useActivity, useAuth, usePermissions, useProjects, useNotifications } from '@/hooks';
import { 
  FolderKanban, 
  DollarSign, 
  FileText, 
  AlertTriangle,
  TrendingUp,
  TrendingDown,
  FileStack,
  GitBranch,
  Receipt,
  Users,
} from 'lucide-react';
import { formatCompactNumber } from '@/utils/formatters';

export default function DashboardPage() {
  const { user } = useAuth();
  const { hasAnyPermission } = usePermissions();
  const { projects, isLoading: isProjectsLoading } = useProjects({
    page: 1,
    page_size: 10,
    ordering: '-created_at',
  });

  const canViewActivity = hasAnyPermission(['activity.view', 'view_activity']);
  const { activities: recentActivity, isLoading: isActivityLoading } = useActivity(
    {
      page: 1,
      page_size: 5,
      ordering: '-timestamp',
    },
    {
      enabled: canViewActivity,
    }
  );

  const canViewNotifications = hasAnyPermission(['notification.view', 'view_notification']);
  const { notifications: recentNotifications, unreadCount, isLoading: isNotificationsLoading, markAsRead } =
    useNotifications(
      { page: 1, page_size: 5 },
      { enabled: canViewNotifications }
    );

  const recentProjects = useMemo(
    () =>
      (projects || []).map((project) => {
        const rawStatus = String((project as any).status || 'DESIGN').toUpperCase();
        const completion = Number((project as any).progress_percentage ?? project.completion_percentage ?? 0);
        const statusLabel = rawStatus.toLowerCase().replace('_', ' ');

        return {
          id: project.id,
          name: project.name,
          status: rawStatus,
          statusLabel,
          completion,
          isActive: ['DESIGN', 'APPROVAL', 'IMPLEMENTATION', 'ON_HOLD'].includes(rawStatus),
          contractValue: Number((project as any).project_value ?? project.contract_value ?? 0),
        };
      }),
    [projects]
  );

  const stats = useMemo(() => {
    const activeProjects = recentProjects.filter((project) => project.isActive).length;
    const totalBudget = recentProjects.reduce((sum, project) => sum + (project.contractValue || 0), 0);
    const pendingApprovals = recentProjects.filter((project) => project.status === 'APPROVAL').length;

    return {
      activeProjects,
      totalBudget,
      pendingApprovals,
      criticalIssues: 0,
    };
  }, [recentProjects]);

  const shortcuts = [
    {
      name: 'Contracts',
      href: '/contracts',
      description: 'Track main legal agreements and linked module records',
      icon: FileText,
      visible: true,
    },
    {
      name: 'Documents',
      href: '/documents',
      description: 'Upload, review, and manage project files',
      icon: FileStack,
      visible: true,
    },
    {
      name: 'Variations',
      href: '/variations',
      description: 'Track variation requests and approvals',
      icon: GitBranch,
      visible: true,
    },
    {
      name: 'Claims',
      href: '/claims',
      description: 'Manage claims, certification, and payment state',
      icon: Receipt,
      visible: true,
    },
    {
      name: 'Subcontractors',
      href: '/subcontractors',
      description: 'Register subcontractors and track assignments',
      icon: Users,
      visible: true,
    },
    {
      name: 'Suppliers',
      href: '/suppliers',
      description: 'Manage supplier records for procurement orders',
      icon: Users,
      visible: true,
    },
  ].filter((item) => item.visible);

  return (
    <DashboardLayout>
      <div className="space-y-6">
        {/* Welcome */}
        <div>
          <h1 className="text-3xl font-bold text-gray-900">
            Welcome back, {user?.full_name || user?.username}!
          </h1>
          <p className="text-gray-600 mt-1">
            Here's what's happening with your projects today.
          </p>
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card hover>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Active Projects</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.activeProjects}
                  </p>
                  <div className="flex items-center gap-1 mt-2 text-success-600 text-sm">
                    <TrendingUp className="h-4 w-4" />
                    <span>+12% from last month</span>
                  </div>
                </div>
                <div className="h-12 w-12 bg-primary-100 rounded-lg flex items-center justify-center">
                  <FolderKanban className="h-6 w-6 text-primary-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Total Budget</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {formatCompactNumber(stats.totalBudget)}
                  </p>
                  <div className="flex items-center gap-1 mt-2 text-success-600 text-sm">
                    <TrendingUp className="h-4 w-4" />
                    <span>+8% this quarter</span>
                  </div>
                </div>
                <div className="h-12 w-12 bg-success-100 rounded-lg flex items-center justify-center">
                  <DollarSign className="h-6 w-6 text-success-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Pending Approvals</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.pendingApprovals}
                  </p>
                  <div className="flex items-center gap-1 mt-2 text-warning-600 text-sm">
                    <span>Requires attention</span>
                  </div>
                </div>
                <div className="h-12 w-12 bg-warning-100 rounded-lg flex items-center justify-center">
                  <FileText className="h-6 w-6 text-warning-600" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card hover>
            <CardContent className="pt-6">
              <div className="flex items-center justify-between">
                <div>
                  <p className="text-sm text-gray-600">Critical Issues</p>
                  <p className="text-3xl font-bold text-gray-900 mt-2">
                    {stats.criticalIssues}
                  </p>
                  <div className="flex items-center gap-1 mt-2 text-destructive-600 text-sm">
                    <TrendingDown className="h-4 w-4" />
                    <span>-2 from yesterday</span>
                  </div>
                </div>
                <div className="h-12 w-12 bg-destructive-100 rounded-lg flex items-center justify-center">
                  <AlertTriangle className="h-6 w-6 text-destructive-600" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>

        {shortcuts.length > 0 ? (
          <Card>
            <CardHeader>
              <CardTitle>Module Shortcuts</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {shortcuts.map((item) => {
                  const Icon = item.icon;

                  return (
                    <Link
                      key={item.href}
                      href={item.href}
                      className="group border border-gray-200 rounded-lg p-4 hover:border-primary-300 hover:bg-primary-50/30 transition-colors"
                    >
                      <div className="flex items-start gap-3">
                        <div className="h-10 w-10 rounded-lg bg-primary-100 text-primary-700 flex items-center justify-center">
                          <Icon className="h-5 w-5" />
                        </div>
                        <div>
                          <h3 className="font-semibold text-gray-900 group-hover:text-primary-700">{item.name}</h3>
                          <p className="text-sm text-gray-600 mt-1">{item.description}</p>
                        </div>
                      </div>
                    </Link>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        ) : null}

        {canViewActivity ? (
          <Card>
            <CardHeader>
              <CardTitle>Recent Activity</CardTitle>
            </CardHeader>
            <CardContent>
              {isActivityLoading ? (
                <p className="text-sm text-gray-500">Loading activity...</p>
              ) : recentActivity.length === 0 ? (
                <p className="text-sm text-gray-500">No recent activity found.</p>
              ) : (
                <div className="space-y-3">
                  {recentActivity.map((activity) => (
                    <ActivityItem key={activity.id} activity={activity} />
                  ))}
                  <Link href="/activity" className="inline-flex text-sm font-medium text-primary-700 hover:text-primary-900">
                    View full activity timeline
                  </Link>
                </div>
              )}
            </CardContent>
          </Card>
        ) : null}

        {canViewNotifications ? (
          <Card>
            <CardHeader>
              <div className="flex items-center justify-between">
                <CardTitle>Recent Notifications</CardTitle>
                {unreadCount > 0 && (
                  <Badge variant="destructive" size="sm">{unreadCount} unread</Badge>
                )}
              </div>
            </CardHeader>
            <CardContent className="p-0">
              {isNotificationsLoading ? (
                <p className="text-sm text-gray-500 px-6 py-4">Loading notifications...</p>
              ) : recentNotifications.length === 0 ? (
                <p className="text-sm text-gray-500 px-6 py-4">No notifications yet.</p>
              ) : (
                <div>
                  {recentNotifications.map((n) => (
                    <NotificationItem key={n.id} notification={n} onMarkAsRead={(id) => markAsRead(id)} compact />
                  ))}
                  <div className="px-4 py-3 border-t border-gray-100">
                    <Link href="/notifications" className="text-sm font-medium text-primary-700 hover:text-primary-900">
                      View all notifications
                    </Link>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        ) : null}

        {/* Recent Projects */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {isProjectsLoading ? (
                <p className="text-sm text-gray-500">Loading projects...</p>
              ) : recentProjects.length === 0 ? (
                <p className="text-sm text-gray-500">No projects found yet.</p>
              ) : (
                recentProjects.map((project) => (
                  <div
                    key={project.id}
                    className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                  >
                    <div className="flex-1">
                      <h3 className="font-semibold text-gray-900">{project.name}</h3>
                      <div className="flex items-center gap-2 mt-2">
                        <Badge
                          variant={project.status === 'COMPLETED' ? 'success' : project.status === 'CANCELLED' ? 'destructive' : 'warning'}
                          size="sm"
                        >
                          {project.statusLabel}
                        </Badge>
                        <span className="text-sm text-gray-600">{project.completion}% Complete</span>
                      </div>
                    </div>
                    <div className="w-32">
                      <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                        <div className="h-full bg-primary-600 transition-all" style={{ width: `${project.completion}%` }} />
                      </div>
                    </div>
                  </div>
                ))
              )}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
