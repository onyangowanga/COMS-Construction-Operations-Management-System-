'use client';

import React, { useEffect } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { reportService } from '@/services';
import { useAuth } from '@/hooks';
import type { Report, ReportCreatePayload } from '@/types';

const schema = z.object({
  code: z.string().optional(),
  name: z.string().min(1, 'Report name is required'),
  description: z.string().optional(),
  module: z.string().min(1, 'Module is required'),
  report_type: z.enum([
    'TABLE',
    'SUMMARY',
    'CHART',
    'PROJECT_FINANCIAL',
    'CASH_FLOW',
    'VARIATION_IMPACT',
    'SUBCONTRACTOR_PAYMENT',
    'DOCUMENT_AUDIT',
    'PROCUREMENT_SUMMARY',
    'CUSTOM',
  ]),
  filters_text: z.string().optional(),
  columns_text: z.string().optional(),
  aggregations_text: z.string().optional(),
  group_by_text: z.string().optional(),
  default_parameters_text: z.string().optional(),
  is_public: z.string().optional(),
  cache_duration: z.string().refine((value: string) => Number(value) >= 0, 'Cache duration must be 0 or greater'),
});

type FormValues = z.infer<typeof schema>;

interface ReportBuilderFormProps {
  initialValues?: Partial<Report>;
  onSubmit: (payload: ReportCreatePayload) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

const reportTypeOptions = [
  { value: 'TABLE', label: 'Table' },
  { value: 'SUMMARY', label: 'Summary' },
  { value: 'CHART', label: 'Chart' },
  { value: 'PROJECT_FINANCIAL', label: 'Project Financial' },
  { value: 'CASH_FLOW', label: 'Cash Flow' },
  { value: 'VARIATION_IMPACT', label: 'Variation Impact' },
  { value: 'SUBCONTRACTOR_PAYMENT', label: 'Subcontractor Payment' },
  { value: 'DOCUMENT_AUDIT', label: 'Document Audit' },
  { value: 'PROCUREMENT_SUMMARY', label: 'Procurement Summary' },
  { value: 'CUSTOM', label: 'Custom' },
];

function parseJson(value: string | undefined, fallback: Record<string, unknown> = {}) {
  const normalized = (value || '').trim();
  if (!normalized) {
    return fallback;
  }

  try {
    return JSON.parse(normalized) as Record<string, unknown>;
  } catch {
    return fallback;
  }
}

function parseList(value: string | undefined) {
  const normalized = (value || '').trim();
  if (!normalized) {
    return [] as string[];
  }

  return normalized
    .split(',')
    .map((item) => item.trim())
    .filter(Boolean);
}

export function ReportBuilderForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Report',
  isSubmitting = false,
}: ReportBuilderFormProps) {
  const { user } = useAuth();
  const canEditCode = Boolean(user?.is_superuser || user?.is_staff);

  const {
    register,
    handleSubmit,
    setValue,
    getValues,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      code: initialValues?.code || '',
      name: initialValues?.name || '',
      description: initialValues?.description || '',
      module: initialValues?.module || 'reporting',
      report_type: (initialValues?.report_type || 'TABLE') as FormValues['report_type'],
      filters_text: initialValues?.filters ? JSON.stringify(initialValues.filters, null, 2) : '{}',
      columns_text: Array.isArray(initialValues?.columns) ? initialValues?.columns.join(', ') : '',
      aggregations_text: initialValues?.aggregations ? JSON.stringify(initialValues.aggregations, null, 2) : '{}',
      group_by_text: Array.isArray(initialValues?.group_by) ? initialValues?.group_by.join(', ') : '',
      default_parameters_text: initialValues?.default_parameters
        ? JSON.stringify(initialValues.default_parameters, null, 2)
        : '{}',
      is_public: initialValues?.is_public ? 'true' : 'false',
      cache_duration: String(initialValues?.cache_duration ?? 300),
    },
  });

  useEffect(() => {
    const loadNextCode = async () => {
      if (initialValues?.id) {
        return;
      }

      try {
        const preview = await reportService.getNextCode();
        if (!canEditCode) {
          setValue('code', preview.code);
          return;
        }

        const existingCode = getValues('code')?.trim();
        if (!existingCode) {
          setValue('code', preview.code);
        }
      } catch {
        if (!canEditCode) {
          setValue('code', '');
        }
      }
    };

    void loadNextCode();
  }, [initialValues?.id, canEditCode, setValue, getValues]);

  return (
    <form
      className="space-y-5"
      onSubmit={handleSubmit((values: FormValues) =>
        onSubmit({
          code: values.code?.trim() || undefined,
          name: values.name.trim(),
          description: values.description?.trim() || '',
          module: values.module.trim(),
          report_type: values.report_type,
          filters: parseJson(values.filters_text, {}),
          columns: parseList(values.columns_text),
          aggregations: parseJson(values.aggregations_text, {}),
          group_by: parseList(values.group_by_text),
          default_parameters: parseJson(values.default_parameters_text, {}),
          is_public: values.is_public === 'true',
          cache_duration: Number(values.cache_duration || 0),
        })
      )}
    >
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Report Code"
          placeholder="Auto-generated"
          helperText={canEditCode ? 'Auto-generated. Admin users may edit.' : 'Auto-generated by system.'}
          readOnly={!canEditCode}
          error={errors.code?.message}
          {...register('code')}
        />
        <Input label="Report Name" error={errors.name?.message} required {...register('name')} />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Module" placeholder="reporting" error={errors.module?.message} required {...register('module')} />
        <Select label="Report Type" options={reportTypeOptions} error={errors.report_type?.message} required {...register('report_type')} />
      </div>

      <Textarea label="Description" rows={3} error={errors.description?.message} {...register('description')} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Textarea
          label="Filters (JSON)"
          rows={6}
          error={errors.filters_text?.message}
          helperText="Valid JSON object input"
          {...register('filters_text')}
        />
        <Textarea
          label="Aggregations (JSON)"
          rows={6}
          error={errors.aggregations_text?.message}
          helperText="Valid JSON object for sums, averages, counts"
          {...register('aggregations_text')}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Columns"
          placeholder="project_name, contract_value, status"
          helperText="Comma-separated fields"
          error={errors.columns_text?.message}
          {...register('columns_text')}
        />
        <Input
          label="Group By"
          placeholder="status, project_manager"
          helperText="Comma-separated fields"
          error={errors.group_by_text?.message}
          {...register('group_by_text')}
        />
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Textarea
          label="Default Parameters (JSON)"
          rows={4}
          error={errors.default_parameters_text?.message}
          {...register('default_parameters_text')}
        />
        <div className="grid grid-cols-1 gap-4">
          <Select
            label="Visibility"
            options={[
              { value: 'false', label: 'Private' },
              { value: 'true', label: 'Public' },
            ]}
            error={errors.is_public?.message}
            {...register('is_public')}
          />
          <Input
            label="Cache Duration (seconds)"
            type="number"
            min="0"
            error={errors.cache_duration?.message}
            {...register('cache_duration')}
          />
        </div>
      </div>

      <div className="flex items-center justify-end gap-3">
        <Button variant="outline" type="button" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {submitText}
        </Button>
      </div>
    </form>
  );
}
