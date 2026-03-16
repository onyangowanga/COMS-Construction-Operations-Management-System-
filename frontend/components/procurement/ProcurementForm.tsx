'use client';

import React, { useMemo } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { useQuery } from '@tanstack/react-query';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { useProjects } from '@/hooks';
import { procurementService } from '@/services';
import { ProcurementOrderStatus, type ProcurementOrder, type ProcurementOrderFormInput } from '@/types';

const LPO_STATUS_OPTIONS = [
  { value: 'DRAFT',               label: 'Draft' },
  { value: 'APPROVED',            label: 'Approved' },
  { value: 'ISSUED',              label: 'Issued' },
  { value: 'PARTIALLY_DELIVERED', label: 'Partially Delivered' },
  { value: 'DELIVERED',           label: 'Delivered' },
  { value: 'INVOICED',            label: 'Invoiced' },
  { value: 'PAID',                label: 'Paid' },
  { value: 'CANCELLED',           label: 'Cancelled' },
];

const schema = z.object({
  reference_number: z.string().min(1, 'LPO number is required'),
  project: z.string().min(1, 'Project is required'),
  supplier: z.string().min(1, 'Supplier is required'),
  order_value: z.string().refine((value) => Number(value) > 0, 'Order value must be positive'),
  description: z.string().optional(),
  issue_date: z.string().optional(),
  delivery_date: z.string().optional(),
  status: z.string().min(1, 'Status is required'),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface ProcurementFormProps {
  initialValues?: Partial<ProcurementOrder>;
  onSubmit: (values: ProcurementOrderFormInput) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

export function ProcurementForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Order',
  isSubmitting = false,
}: ProcurementFormProps) {
  const { projects } = useProjects({ page_size: 200 });
  const projectOptions = useMemo(
    () => projects.map((p) => ({ value: p.id, label: p.name })),
    [projects],
  );

  // Fetch real suppliers for the dropdown (TanStack Query v5 object syntax)
  const { data: suppliersRaw } = useQuery({
    queryKey: ['suppliers-list'],
    queryFn: () => procurementService.getSuppliers(),
    staleTime: 60_000,
  });
  const supplierOptions = useMemo(
    () => (suppliersRaw ?? []).map((s: { id: string; company_name?: string; name?: string }) => ({ value: s.id, label: s.company_name || s.name || 'Unknown Supplier' })),
    [suppliersRaw],
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      reference_number: initialValues?.reference_number || '',
      project: initialValues?.project || '',
      supplier: initialValues?.supplier || '',
      order_value: String(initialValues?.order_value || ''),
      description: initialValues?.description || '',
      issue_date: new Date().toISOString().split('T')[0],
      delivery_date: initialValues?.delivery_date || '',
      status: String(initialValues?.status || 'DRAFT').toUpperCase(),
      notes: initialValues?.notes || '',
    },
  });

  return (
    <form
      className="space-y-5"
      onSubmit={handleSubmit((values) =>
        onSubmit({
          ...values,
          status: values.status as ProcurementOrderStatus,
        })
      )}
    >
      <Input
        label="LPO / Reference Number"
        error={errors.reference_number?.message}
        required
        placeholder="e.g. LPO-2026-001"
        {...register('reference_number')}
      />

      <Select label="Project" options={projectOptions} error={errors.project?.message} required {...register('project')} />

      <Select
        label="Supplier"
        options={supplierOptions.length > 0 ? supplierOptions : [{ value: '', label: 'Loading suppliers…' }]}
        error={errors.supplier?.message}
        required
        {...register('supplier')}
      />

      <Input
        label="Order Value"
        type="number"
        step="0.01"
        error={errors.order_value?.message}
        required
        {...register('order_value')}
      />

      <Textarea
        label="Description / Scope"
        rows={4}
        error={errors.description?.message}
        {...register('description')}
      />

      <div className="grid grid-cols-2 gap-4">
        <Input label="Issue Date" type="date" error={errors.issue_date?.message} {...register('issue_date')} />
        <Input label="Delivery Deadline" type="date" error={errors.delivery_date?.message} {...register('delivery_date')} />
      </div>

      <Select label="Status" options={LPO_STATUS_OPTIONS} error={errors.status?.message} required {...register('status')} />

      <Textarea label="Notes" rows={3} error={errors.notes?.message} {...register('notes')} />

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
