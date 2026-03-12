// ============================================================================
// DASHBOARD PAGE
// Main dashboard with KPIs, charts, and activity feed
// ============================================================================

'use client';

import React from 'react';
import { DashboardLayout } from '@/components/layout';
import { Card, CardHeader, CardTitle, CardContent, Badge } from '@/components/ui';
import { useAuth } from '@/hooks';
import { 
  FolderKanban, 
  DollarSign, 
  FileText, 
  AlertTriangle,
  TrendingUp,
  TrendingDown
} from 'lucide-react';
import { formatCurrency, formatCompactNumber } from '@/utils/formatters';

export default function DashboardPage() {
  const { user } = useAuth();

  // Mock data - would come from API
  const stats = {
    activeProjects: 12,
    totalBudget: 45000000,
    pendingApprovals: 8,
    criticalIssues: 3,
  };

  const recentProjects = [
    { id: 1, name: 'Highway Expansion Project', status: 'active', completion: 65 },
    { id: 2, name: 'Shopping Mall Construction', status: 'active', completion: 42 },
    { id: 3, name: 'Residential Complex Phase 2', status: 'on-hold', completion: 28 },
  ];

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

        {/* Recent Projects */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Projects</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {recentProjects.map((project) => (
                <div
                  key={project.id}
                  className="flex items-center justify-between p-4 border border-gray-200 rounded-lg hover:bg-gray-50 transition-colors"
                >
                  <div className="flex-1">
                    <h3 className="font-semibold text-gray-900">{project.name}</h3>
                    <div className="flex items-center gap-2 mt-2">
                      <Badge
                        variant={project.status === 'active' ? 'success' : 'warning'}
                        size="sm"
                      >
                        {project.status}
                      </Badge>
                      <span className="text-sm text-gray-600">
                        {project.completion}% Complete
                      </span>
                    </div>
                  </div>
                  <div className="w-32">
                    <div className="h-2 bg-gray-200 rounded-full overflow-hidden">
                      <div
                        className="h-full bg-primary-600 transition-all"
                        style={{ width: `${project.completion}%` }}
                      />
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>
    </DashboardLayout>
  );
}
