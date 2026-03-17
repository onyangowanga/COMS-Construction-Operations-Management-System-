'use client';

import React, { useMemo, useState } from 'react';
import { useParams, useRouter } from 'next/navigation';
import { PlayCircle } from 'lucide-react';
import { DashboardLayout } from '@/components/layout';
import { PermissionGuard } from '@/components/auth/PermissionGuard';
import { ReportExecutionTable } from '@/components/reports';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select, Textarea } from '@/components/ui';
import { useReport, useReportExecutions, useReportSchedules, useToast } from '@/hooks';
import { reportService } from '@/services';

export default function ReportDetailPage() {
  const params = useParams<{ id: string }>();
  const router = useRouter();
  const { success, error } = useToast();

  const reportId = useMemo(() => String(params?.id || ''), [params]);
  const [isExecuting, setIsExecuting] = useState(false);

  const [scheduleName, setScheduleName] = useState('');
  const [frequency, setFrequency] = useState('DAILY');
  const [exportFormat, setExportFormat] = useState('PDF');
  const [deliveryMethod, setDeliveryMethod] = useState('EMAIL');
  const [recipients, setRecipients] = useState('');
  const [parametersText, setParametersText] = useState('{}');

  const { report, isLoading } = useReport(reportId);
  const { executions, isLoading: executionsLoading } = useReportExecutions(reportId);
  const {
    schedules,
    isLoading: schedulesLoading,
    createSchedule,
    deleteSchedule,
    isCreating: isCreatingSchedule,
  } = useReportSchedules({ report: reportId, ordering: '-created_at' });

  const handleExecute = async () => {
    if (!reportId) {
      return;
    }

    setIsExecuting(true);
    try {
      const parameters = JSON.parse(parametersText || '{}');
      await reportService.executeReport(reportId, parameters);
      success('Report Executed', 'Execution has started successfully.');
    } catch (executionError: any) {
      error('Execution Failed', executionError?.message || 'Unable to execute report');
    } finally {
      setIsExecuting(false);
    }
  };

  const handleCreateSchedule = async () => {
    if (!reportId || !scheduleName.trim()) {
      return;
    }

    try {
      await createSchedule({
        report_id: reportId,
        name: scheduleName.trim(),
        frequency: frequency as 'DAILY' | 'WEEKLY' | 'MONTHLY' | 'QUARTERLY' | 'CUSTOM',
        export_format: exportFormat as 'PDF' | 'EXCEL' | 'CSV' | 'JSON',
        delivery_method: deliveryMethod as 'EMAIL' | 'DASHBOARD' | 'STORAGE' | 'ALL',
        recipients: recipients
          .split(',')
          .map((item) => item.trim())
          .filter(Boolean),
        parameters: JSON.parse(parametersText || '{}'),
      });

      setScheduleName('');
      setRecipients('');
      success('Schedule Created', 'Scheduled report created successfully.');
    } catch (scheduleError: any) {
      error('Schedule Failed', scheduleError?.message || 'Unable to create schedule');
    }
  };

  return (
    <DashboardLayout>
      <PermissionGuard permission={['view_report', 'report.view']}>
        <div className="space-y-6">
          <div className="flex items-center justify-between">
            <div>
              <h1 className="text-3xl font-bold text-gray-900">{report?.name || 'Report Details'}</h1>
              <p className="text-gray-600 mt-1">
                {report ? `${report.code} • ${report.module} • ${report.report_type}` : 'Loading report metadata...'}
              </p>
            </div>
            <div className="flex items-center gap-3">
              <Button variant="outline" onClick={() => router.push('/reports')}>
                Back
              </Button>
              <Button leftIcon={<PlayCircle className="h-5 w-5" />} isLoading={isExecuting} onClick={handleExecute}>
                Execute Report
              </Button>
            </div>
          </div>

          <Card>
            <CardHeader>
              <CardTitle>Execution Parameters</CardTitle>
            </CardHeader>
            <CardContent>
              <Textarea
                label="Runtime Parameters (JSON)"
                rows={5}
                value={parametersText}
                onChange={(event) => setParametersText(event.target.value)}
                helperText="JSON payload passed into the report execution engine"
              />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Execution History</CardTitle>
            </CardHeader>
            <CardContent>
              <ReportExecutionTable executions={executions} isLoading={isLoading || executionsLoading} />
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle>Scheduled Reports</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="grid grid-cols-1 md:grid-cols-5 gap-3 mb-4">
                <Input label="Name" value={scheduleName} onChange={(event) => setScheduleName(event.target.value)} />
                <Select
                  label="Frequency"
                  value={frequency}
                  onChange={(event) => setFrequency(event.target.value)}
                  options={[
                    { value: 'DAILY', label: 'Daily' },
                    { value: 'WEEKLY', label: 'Weekly' },
                    { value: 'MONTHLY', label: 'Monthly' },
                    { value: 'QUARTERLY', label: 'Quarterly' },
                    { value: 'CUSTOM', label: 'Custom' },
                  ]}
                />
                <Select
                  label="Format"
                  value={exportFormat}
                  onChange={(event) => setExportFormat(event.target.value)}
                  options={[
                    { value: 'PDF', label: 'PDF' },
                    { value: 'EXCEL', label: 'Excel' },
                    { value: 'CSV', label: 'CSV' },
                    { value: 'JSON', label: 'JSON' },
                  ]}
                />
                <Select
                  label="Delivery"
                  value={deliveryMethod}
                  onChange={(event) => setDeliveryMethod(event.target.value)}
                  options={[
                    { value: 'EMAIL', label: 'Email' },
                    { value: 'DASHBOARD', label: 'Dashboard' },
                    { value: 'STORAGE', label: 'Storage' },
                    { value: 'ALL', label: 'All' },
                  ]}
                />
                <div className="flex items-end">
                  <Button className="w-full" isLoading={isCreatingSchedule} onClick={handleCreateSchedule}>
                    Add Schedule
                  </Button>
                </div>
              </div>

              <Input
                label="Recipients"
                placeholder="finance@example.com, ops@example.com"
                value={recipients}
                onChange={(event) => setRecipients(event.target.value)}
                helperText="Comma-separated email list"
              />

              <div className="mt-4 space-y-2">
                {schedulesLoading ? <p className="text-sm text-gray-500">Loading schedules...</p> : null}
                {!schedulesLoading && schedules.length === 0 ? (
                  <p className="text-sm text-gray-500">No schedules configured yet.</p>
                ) : null}
                {schedules.map((schedule) => (
                  <div key={schedule.id} className="flex items-center justify-between rounded-md border border-gray-200 px-3 py-2">
                    <div>
                      <p className="font-medium text-gray-900">{schedule.name}</p>
                      <p className="text-sm text-gray-600">
                        {schedule.frequency} • {schedule.export_format} • {schedule.delivery_method}
                      </p>
                    </div>
                    <Button
                      variant="destructive"
                      size="sm"
                      onClick={async () => {
                        if (!window.confirm(`Delete schedule \"${schedule.name}\"?`)) {
                          return;
                        }
                        await deleteSchedule(schedule.id);
                      }}
                    >
                      Delete
                    </Button>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      </PermissionGuard>
    </DashboardLayout>
  );
}
