'use client';

import React, { useMemo } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { useProjects } from '@/hooks';
import type { Claim, ClaimFormInput } from '@/types';

const schema = z.object({
  claim_number: z.string().min(1, 'Claim number is required'),
  project: z.string().min(1, 'Project is required'),
  claim_amount: z.string().refine((value) => Number(value) > 0, 'Claim amount must be positive'),
  description: z.string().min(1, 'Description is required'),
});

type FormValues = z.infer<typeof schema>;

interface ClaimFormProps {
  initialValues?: Partial<Claim>;
  onSubmit: (values: ClaimFormInput) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

export function ClaimForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Claim',
  isSubmitting = false,
}: ClaimFormProps) {
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
      claim_number: initialValues?.claim_number || '',
      project: initialValues?.project || '',
      claim_amount: String(initialValues?.claim_amount || initialValues?.gross_amount || ''),
      description: initialValues?.description || initialValues?.notes || '',
    },
  });

  return (
    <form className="space-y-5" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <Input label="Claim Number" error={errors.claim_number?.message} required {...register('claim_number')} />

      <Select label="Project" options={projectOptions} error={errors.project?.message} required {...register('project')} />

      <Input
        label="Claim Amount"
        type="number"
        step="0.01"
        error={errors.claim_amount?.message}
        required
        {...register('claim_amount')}
      />

      <Textarea
        label="Description"
        rows={4}
        placeholder="Describe the scope covered by this claim"
        error={errors.description?.message}
        required
        {...register('description')}
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
