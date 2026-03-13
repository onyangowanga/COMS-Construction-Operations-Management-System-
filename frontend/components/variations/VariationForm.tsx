'use client';

import React, { useMemo } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { useProjects } from '@/hooks';
import type { VariationFormInput, VariationOrder } from '@/types';

const schema = z.object({
  project_id: z.string().min(1, 'Project is required'),
  title: z.string().min(1, 'Variation reference is required'),
  description: z.string().min(1, 'Description is required'),
  estimated_value: z.string().refine((value) => Number(value) > 0, 'Variation value must be positive'),
  impact_on_schedule: z.string().optional(),
  technical_notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface VariationFormProps {
  initialValues?: Partial<VariationOrder>;
  onSubmit: (values: VariationFormInput) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

export function VariationForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Variation',
  isSubmitting = false,
}: VariationFormProps) {
  const { projects } = useProjects({ page_size: 200 });

  const projectOptions = useMemo(
    () => projects.map((project) => ({ value: project.id, label: project.name })),
    [projects]
  );

  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      project_id:
        typeof initialValues?.project === 'string'
          ? initialValues.project
          : initialValues?.project?.id || '',
      title: initialValues?.title || initialValues?.reference_number || '',
      description: initialValues?.description || '',
      estimated_value: String(initialValues?.estimated_value || ''),
      impact_on_schedule: initialValues?.impact_on_schedule || '',
      technical_notes: initialValues?.technical_notes || '',
    },
  });

  return (
    <form className="space-y-5" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <Select label="Project" options={projectOptions} error={errors.project_id?.message} required {...register('project_id')} />

      <Input
        label="Variation Reference"
        placeholder="e.g. VO-2026-001"
        error={errors.title?.message}
        required
        {...register('title')}
      />

      <Textarea
        label="Description"
        rows={4}
        placeholder="Describe the variation request"
        error={errors.description?.message}
        required
        {...register('description')}
      />

      <Input
        label="Cost Impact"
        type="number"
        step="0.01"
        error={errors.estimated_value?.message}
        required
        {...register('estimated_value')}
      />

      <Textarea
        label="Time Impact"
        rows={3}
        placeholder="Describe expected schedule impact"
        error={errors.impact_on_schedule?.message}
        {...register('impact_on_schedule')}
      />

      <Textarea
        label="Supporting Documents / Notes"
        rows={3}
        placeholder="Include links or references to supporting documents"
        error={errors.technical_notes?.message}
        {...register('technical_notes')}
      />

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
