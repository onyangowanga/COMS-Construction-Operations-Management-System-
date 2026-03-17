'use client';

import React from 'react';
import { Button, Card, CardContent, CardHeader, CardTitle, Input, Select } from '@/components/ui';

export interface ActivityFilterValues {
  module: string;
  event_type: string;
  start_date: string;
  end_date: string;
}

interface ActivityFiltersProps {
  values: ActivityFilterValues;
  onChange: (values: ActivityFilterValues) => void;
  onReset: () => void;
}

const moduleOptions = [
  { value: '', label: 'All modules' },
  { value: 'CONTRACT', label: 'Contract' },
  { value: 'PROJECT', label: 'Project' },
  { value: 'DOCUMENT', label: 'Document' },
  { value: 'VARIATION', label: 'Variation' },
  { value: 'CLAIM', label: 'Claim' },
  { value: 'PROCUREMENT', label: 'Procurement' },
  { value: 'SUPPLIER', label: 'Supplier' },
  { value: 'SUBCONTRACTOR', label: 'Subcontractor' },
];

const eventTypeOptions = [
  { value: '', label: 'All events' },
  { value: 'CREATE', label: 'Create' },
  { value: 'UPDATE', label: 'Update' },
  { value: 'DELETE', label: 'Delete' },
  { value: 'APPROVE', label: 'Approve' },
  { value: 'REJECT', label: 'Reject' },
  { value: 'SUBMIT', label: 'Submit' },
  { value: 'CERTIFY', label: 'Certify' },
];

export function ActivityFilters({ values, onChange, onReset }: ActivityFiltersProps) {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Filters</CardTitle>
      </CardHeader>
      <CardContent className="space-y-3">
        <Select
          label="Module"
          value={values.module}
          options={moduleOptions}
          onChange={(event) => onChange({ ...values, module: event.target.value })}
        />

        <Select
          label="Event Type"
          value={values.event_type}
          options={eventTypeOptions}
          onChange={(event) => onChange({ ...values, event_type: event.target.value })}
        />

        <Input
          label="Start Date"
          type="date"
          value={values.start_date}
          onChange={(event) => onChange({ ...values, start_date: event.target.value })}
        />

        <Input
          label="End Date"
          type="date"
          value={values.end_date}
          onChange={(event) => onChange({ ...values, end_date: event.target.value })}
        />

        <Button variant="outline" className="w-full" onClick={onReset}>
          Reset Filters
        </Button>
      </CardContent>
    </Card>
  );
}
