'use client';

import React from 'react';
import { useParams } from 'next/navigation';
import {
  Area,
  AreaChart,
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  Line,
  LineChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from 'recharts';
import { Activity, Briefcase, FileText, Receipt } from 'lucide-react';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ProjectMetricsCard, ProjectStatusBadge } from '@/components/projects';
import { DashboardLayout } from '@/components/layout';
import { Card, CardContent, CardHeader, CardTitle, LoadingSpinner } from '@/components/ui';
import { useProject, useProjectDashboard, useProjectMetrics } from '@/hooks';
import { formatCurrency, formatDate, formatPercentage } from '@/utils/formatters';

export default function ProjectDashboardPage() {
  const params = useParams<{ id: string }>();
  const projectId = params?.id;

  const { project, isLoading: projectLoading } = useProject(projectId);
  const { metrics, isLoading: metricsLoading } = useProjectMetrics(projectId);
  const { dashboard, isLoading: dashboardLoading } = useProjectDashboard(projectId);

  const isLoading = projectLoading || metricsLoading || dashboardLoading;

  const budgetChartData = dashboard?.budget_vs_actual || [];
  const variationTrendData = dashboard?.variation_trend || [];
  const claimProgressData = dashboard?.claim_progress || [];

  return (
    <DashboardLayout>
      <PermissionGuard
        permission="project.view"
        fallback={
          <Card>
            <CardContent>
              <p className="text-gray-600">You do not have permission to view project dashboards.</p>
            </CardContent>
          </Card>
        }
      >
        {isLoading || !project ? (
          <div className="py-20 flex justify-center">
            <LoadingSpinner size="lg" />
          </div>
        ) : (
          <div className="space-y-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{project.name} Dashboard</h1>
              <p className="text-gray-600 mt-1">Project metrics, budget trends and activity.</p>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
              <ProjectMetricsCard
                title="Contract Value"
                value={formatCurrency(dashboard?.kpis.contract_value ?? Number(project.contract_value || 0))}
                icon={<Briefcase className="h-5 w-5" />}
              />
              <ProjectMetricsCard
                title="Total Variations"
                value={formatCurrency(dashboard?.kpis.total_variations ?? Number(project.variation_value || 0))}
                icon={<FileText className="h-5 w-5" />}
              />
              <ProjectMetricsCard
                title="Approved Claims"
                value={formatCurrency(dashboard?.kpis.approved_claims ?? Number(project.claim_value || 0))}
                icon={<Receipt className="h-5 w-5" />}
              />
              <ProjectMetricsCard
                title="Completion"
                value={formatPercentage(dashboard?.kpis.completion_percentage ?? project.completion_percentage ?? 0, 0)}
                icon={<Activity className="h-5 w-5" />}
              />
            </div>

            <div className="grid grid-cols-1 xl:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Budget vs Actual Spending</CardTitle>
                </CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={budgetChartData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Bar dataKey="budget" fill="#3b82f6" name="Budget" />
                      <Bar dataKey="actual" fill="#10b981" name="Actual" />
                    </BarChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Variation Trend</CardTitle>
                </CardHeader>
                <CardContent className="h-72">
                  <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={variationTrendData}>
                      <CartesianGrid strokeDasharray="3 3" />
                      <XAxis dataKey="period" />
                      <YAxis />
                      <Tooltip />
                      <Legend />
                      <Line type="monotone" dataKey="value" stroke="#f59e0b" strokeWidth={2} name="Variation Value" />
                    </LineChart>
                  </ResponsiveContainer>
                </CardContent>
              </Card>
            </div>

            <Card>
              <CardHeader>
                <CardTitle>Claim Certification Progress</CardTitle>
              </CardHeader>
              <CardContent className="h-72">
                <ResponsiveContainer width="100%" height="100%">
                  <AreaChart data={claimProgressData}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="period" />
                    <YAxis />
                    <Tooltip />
                    <Legend />
                    <Area type="monotone" dataKey="submitted" stroke="#6366f1" fill="#c7d2fe" name="Submitted" />
                    <Area type="monotone" dataKey="certified" stroke="#059669" fill="#a7f3d0" name="Certified" />
                  </AreaChart>
                </ResponsiveContainer>
              </CardContent>
            </Card>

            <div className="grid grid-cols-1 xl:grid-cols-3 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Recent Documents</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(dashboard?.recent_documents || []).map((document) => (
                    <div key={document.id} className="border-b border-gray-100 pb-2 last:border-0">
                      <p className="text-sm font-medium text-gray-900">{document.title}</p>
                      <p className="text-xs text-gray-500">{formatDate(document.created_at)}</p>
                    </div>
                  ))}
                  {!dashboard?.recent_documents?.length ? <p className="text-sm text-gray-500">No recent documents.</p> : null}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Variations</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(dashboard?.recent_variations || []).map((variation) => (
                    <div key={variation.id} className="border-b border-gray-100 pb-2 last:border-0">
                      <p className="text-sm font-medium text-gray-900">{variation.title}</p>
                      <div className="flex items-center justify-between mt-1">
                        <ProjectStatusBadge status={variation.status} />
                        <span className="text-xs text-gray-500">{formatDate(variation.created_at)}</span>
                      </div>
                    </div>
                  ))}
                  {!dashboard?.recent_variations?.length ? <p className="text-sm text-gray-500">No recent variations.</p> : null}
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Recent Activity</CardTitle>
                </CardHeader>
                <CardContent className="space-y-3">
                  {(dashboard?.recent_activity || []).map((activity) => (
                    <div key={activity.id} className="border-b border-gray-100 pb-2 last:border-0">
                      <p className="text-sm text-gray-900">{activity.action}</p>
                      <p className="text-xs text-gray-500">{activity.actor_name || 'System'} - {formatDate(activity.created_at)}</p>
                    </div>
                  ))}
                  {!dashboard?.recent_activity?.length ? <p className="text-sm text-gray-500">No recent activity.</p> : null}
                </CardContent>
              </Card>
            </div>

            {metrics ? (
              <Card>
                <CardHeader>
                  <CardTitle>Metrics Snapshot</CardTitle>
                </CardHeader>
                <CardContent className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-gray-500">Budget Utilization</p>
                    <p className="font-medium text-gray-900">{formatPercentage(metrics.budget_utilization, 1)}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Schedule Variance</p>
                    <p className="font-medium text-gray-900">{metrics.schedule_variance}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Cost Variance</p>
                    <p className="font-medium text-gray-900">{metrics.cost_variance}</p>
                  </div>
                  <div>
                    <p className="text-gray-500">Earned Value</p>
                    <p className="font-medium text-gray-900">{formatCurrency(metrics.earned_value)}</p>
                  </div>
                </CardContent>
              </Card>
            ) : null}
          </div>
        )}
      </PermissionGuard>
    </DashboardLayout>
  );
}
