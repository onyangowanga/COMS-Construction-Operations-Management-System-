'use client';

import React from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { Project, ProjectStatus, ProjectFormInput } from '@/types';

const projectFormSchema = z
  .object({
    name: z.string().min(1, 'Project name is required'),
    client: z.string().min(1, 'Client is required'),
    contract_value: z
      .string()
      .min(1, 'Contract value is required')
      .refine((value) => Number(value) > 0, 'Contract value must be a positive number'),
    project_manager: z.string().optional(),
    start_date: z.string().min(1, 'Start date is required'),
    end_date: z.string().min(1, 'End date is required'),
    status: z.nativeEnum(ProjectStatus),
    description: z.string().optional(),
  })
  .refine((data) => new Date(data.end_date) > new Date(data.start_date), {
    message: 'End date must be after start date',
    path: ['end_date'],
  });

export type ProjectFormValues = z.infer<typeof projectFormSchema>;

interface ProjectFormProps {
  initialValues?: Partial<Project>;
  onSubmit: (values: ProjectFormInput) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

const statusOptions = [
  { value: ProjectStatus.PLANNING, label: 'Planning' },
  { value: ProjectStatus.ACTIVE, label: 'Active' },
  { value: ProjectStatus.ON_HOLD, label: 'On Hold' },
  { value: ProjectStatus.COMPLETED, label: 'Completed' },
  { value: ProjectStatus.CANCELLED, label: 'Cancelled' },
];

export function ProjectForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Project',
  isSubmitting = false,
}: ProjectFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<ProjectFormValues>({
    resolver: zodResolver(projectFormSchema),
    defaultValues: {
      name: initialValues?.name || '',
      client: initialValues?.client || '',
      contract_value: initialValues?.contract_value || '',
      project_manager: initialValues?.project_manager || '',
      start_date: initialValues?.start_date?.split('T')[0] || '',
      end_date: initialValues?.end_date?.split('T')[0] || '',
      status: (initialValues?.status || ProjectStatus.PLANNING) as ProjectStatus,
      description: initialValues?.description || '',
    },
  });

  return (
    <form className="space-y-6" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input
          label="Project Name"
          placeholder="e.g. Nairobi Bypass Expansion"
          error={errors.name?.message}
          required
          {...register('name')}
        />

        <Input
          label="Client"
          placeholder="Client name or ID"
          error={errors.client?.message}
          required
          {...register('client')}
        />

        <Input
          label="Contract Value"
          type="number"
          min="0"
          step="0.01"
          placeholder="0.00"
          error={errors.contract_value?.message}
          required
          {...register('contract_value')}
        />

        <Input
          label="Project Manager"
          placeholder="Project manager"
          error={errors.project_manager?.message}
          {...register('project_manager')}
        />

        <Input
          label="Start Date"
          type="date"
          error={errors.start_date?.message}
          required
          {...register('start_date')}
        />

        <Input
          label="End Date"
          type="date"
          error={errors.end_date?.message}
          required
          {...register('end_date')}
        />
      </div>

      <Select
        label="Status"
        options={statusOptions}
        error={errors.status?.message}
        required
        {...register('status')}
      />

      <Textarea
        label="Description"
        placeholder="Project description"
        rows={5}
        error={errors.description?.message}
        {...register('description')}
      />

      <div className="flex items-center justify-end gap-3">
        <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          {submitText}
        </Button>
      </div>
    </form>
  );
}
