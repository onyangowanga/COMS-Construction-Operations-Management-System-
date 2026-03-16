'use client';

import React from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Textarea } from '@/components/ui';
import type { Subcontractor, SubcontractorFormInput } from '@/types';

const schema = z.object({
  company_name: z.string().min(1, 'Company name is required'),
  contact_person: z.string().min(1, 'Contact person is required'),
  email: z.string().email('Email is required'),
  phone: z.string().min(1, 'Phone is required'),
  specialization: z.string().min(1, 'Specialization is required'),
  address: z.string().optional(),
  registration_number: z.string().optional(),
  notes: z.string().optional(),
});

type FormValues = z.infer<typeof schema>;

interface SubcontractorFormProps {
  initialValues?: Partial<Subcontractor>;
  onSubmit: (values: SubcontractorFormInput) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

export function SubcontractorForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Subcontractor',
  isSubmitting = false,
}: SubcontractorFormProps) {
  const {
    register,
    handleSubmit,
    formState: { errors },
  } = useForm<FormValues>({
    resolver: zodResolver(schema),
    defaultValues: {
      company_name: initialValues?.company_name || '',
      contact_person: initialValues?.contact_person || '',
      email: initialValues?.email || '',
      phone: initialValues?.phone || '',
      specialization: initialValues?.specialization || '',
      address: initialValues?.address || '',
      registration_number: initialValues?.registration_number || '',
      notes: initialValues?.notes || '',
    },
  });

  return (
    <form className="space-y-5" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <Input label="Company Name" error={errors.company_name?.message} required {...register('company_name')} />
      <Input label="Contact Person" error={errors.contact_person?.message} required {...register('contact_person')} />
      <Input label="Email" type="email" error={errors.email?.message} required {...register('email')} />
      <Input label="Phone" error={errors.phone?.message} required {...register('phone')} />
      <Input label="Specialization" error={errors.specialization?.message} required {...register('specialization')} />
      <Textarea label="Address" rows={3} error={errors.address?.message} {...register('address')} />
      <Input label="Registration Number" error={errors.registration_number?.message} {...register('registration_number')} />
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
