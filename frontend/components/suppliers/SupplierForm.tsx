'use client';

import React from 'react';
import { z } from 'zod';
import { zodResolver } from '@hookform/resolvers/zod';
import { useForm } from 'react-hook-form';
import { Button, Input, Select, Textarea } from '@/components/ui';
import type { Supplier, SupplierCreatePayload } from '@/types';

const schema = z.object({
  company_name: z.string().min(1, 'Company name is required'),
  contact_person: z.string().optional(),
  email: z.string().email('Valid email is required'),
  phone: z.string().min(1, 'Phone is required'),
  address: z.string().optional(),
  registration_number: z.string().optional(),
  tax_number: z.string().optional(),
  notes: z.string().optional(),
  status: z.enum(['ACTIVE', 'INACTIVE']).default('ACTIVE'),
});

type FormValues = z.infer<typeof schema>;

interface SupplierFormProps {
  initialValues?: Partial<Supplier>;
  onSubmit: (values: SupplierCreatePayload) => Promise<void>;
  onCancel: () => void;
  submitText?: string;
  isSubmitting?: boolean;
}

const statusOptions = [
  { value: 'ACTIVE', label: 'Active' },
  { value: 'INACTIVE', label: 'Inactive' },
];

export function SupplierForm({
  initialValues,
  onSubmit,
  onCancel,
  submitText = 'Save Supplier',
  isSubmitting = false,
}: SupplierFormProps) {
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
      address: initialValues?.address || '',
      registration_number: initialValues?.registration_number || '',
      tax_number: initialValues?.tax_number || '',
      notes: initialValues?.notes || '',
      status: (String(initialValues?.status || 'ACTIVE').toUpperCase() as FormValues['status']),
    },
  });

  return (
    <form className="space-y-5" onSubmit={handleSubmit((values) => onSubmit(values))}>
      <Input label="Company Name" error={errors.company_name?.message} required {...register('company_name')} />
      <Input label="Contact Person" error={errors.contact_person?.message} {...register('contact_person')} />
      <Input label="Email" type="email" error={errors.email?.message} required {...register('email')} />
      <Input label="Phone" error={errors.phone?.message} required {...register('phone')} />

      <Textarea label="Address" rows={3} error={errors.address?.message} {...register('address')} />

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <Input label="Registration Number" error={errors.registration_number?.message} {...register('registration_number')} />
        <Input label="Tax Number" error={errors.tax_number?.message} {...register('tax_number')} />
      </div>

      <Select label="Status" options={statusOptions} error={errors.status?.message} required {...register('status')} />

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
