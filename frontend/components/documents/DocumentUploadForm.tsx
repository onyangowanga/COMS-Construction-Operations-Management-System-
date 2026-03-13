'use client';

import React, { useMemo } from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import { useProjects } from '@/hooks';
import type { DocumentUploadInput } from '@/types';

const MAX_FILE_SIZE = 25 * 1024 * 1024;
const ALLOWED_TYPES = [
  'application/pdf',
  'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
  'image/png',
  'image/jpeg',
  'image/jpg',
  'image/webp',
  'image/gif',
];

const schema = z.object({
  file: z
    .any()
    .refine((value) => value instanceof File, 'File is required')
    .refine((value) => value?.size <= MAX_FILE_SIZE, 'Max file size is 25MB')
    .refine((value) => ALLOWED_TYPES.includes(value?.type), 'Allowed types: pdf, docx, xlsx, images'),
  title: z.string().min(1, 'Document name is required'),
  document_type: z.string().min(1, 'Document type is required'),
  project: z.string().optional(),
  description: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface DocumentUploadFormProps {
  onSubmit: (values: DocumentUploadInput) => Promise<void>;
  onCancel: () => void;
  isSubmitting?: boolean;
}

const documentTypeOptions = [
  { value: 'CONTRACT', label: 'Contract' },
  { value: 'DRAWING', label: 'Drawing' },
  { value: 'BOQ', label: 'BOQ' },
  { value: 'PROGRESS_REPORT', label: 'Progress Report' },
  { value: 'VARIATION_INSTRUCTION', label: 'Variation Instruction' },
  { value: 'VALUATION_CERTIFICATE', label: 'Valuation Certificate' },
  { value: 'CORRESPONDENCE', label: 'Correspondence' },
  { value: 'OTHER', label: 'Other' },
];

export function DocumentUploadForm({ onSubmit, onCancel, isSubmitting = false }: DocumentUploadFormProps) {
  const { projects } = useProjects({ page_size: 200 });

  const projectOptions = useMemo(
    () => [
      { value: '', label: 'No project (global document)' },
      ...projects.map((project) => ({ value: project.id, label: project.name })),
    ],
    [projects]
  );

  const {
    register,
    handleSubmit,
    setValue,
    watch,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      title: '',
      document_type: 'OTHER',
      project: '',
      description: '',
    },
  });

  const file = watch('file');

  return (
    <form className="space-y-5" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <div>
        <label className="block text-sm font-medium text-gray-700 mb-1.5">
          File <span className="text-destructive-600">*</span>
        </label>
        <input
          type="file"
          onChange={(event) => {
            const selected = event.target.files?.[0];
            if (selected) {
              setValue('file', selected, { shouldValidate: true });
              if (!watch('title')) {
                setValue('title', selected.name.replace(/\.[^/.]+$/, ''), { shouldValidate: true });
              }
            }
          }}
          className="block w-full text-sm text-gray-700 file:mr-4 file:py-2 file:px-4 file:rounded-md file:border-0 file:bg-primary-50 file:text-primary-700 hover:file:bg-primary-100"
        />
        {errors.file?.message ? <p className="mt-1.5 text-sm text-destructive-600">{String(errors.file.message)}</p> : null}
        {file instanceof File ? <p className="mt-1 text-xs text-gray-500">Selected: {file.name}</p> : null}
      </div>

      <Input label="Document Name" error={errors.title?.message} required {...register('title')} />

      <Select
        label="Document Type"
        options={documentTypeOptions}
        error={errors.document_type?.message}
        required
        {...register('document_type')}
      />

      <Select label="Project" options={projectOptions} error={errors.project?.message} {...register('project')} />

      <Textarea
        label="Description"
        rows={4}
        placeholder="Briefly describe this document"
        error={errors.description?.message}
        {...register('description')}
      />

      <div className="flex items-center justify-end gap-3">
        <Button variant="outline" type="button" onClick={onCancel} disabled={isSubmitting}>
          Cancel
        </Button>
        <Button type="submit" isLoading={isSubmitting}>
          Upload Document
        </Button>
      </div>
    </form>
  );
}
