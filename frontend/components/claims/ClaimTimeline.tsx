import React from 'react';
import { CheckCircle2 } from 'lucide-react';
import { cn } from '@/utils/helpers';
import { formatDateTime } from '@/utils/formatters';
import type { Claim } from '@/types';

interface ClaimTimelineProps {
  claim: Claim;
}

export function ClaimTimeline({ claim }: ClaimTimelineProps) {
  const steps = [
    { key: 'DRAFT', label: 'Draft', date: claim.created_at },
    { key: 'SUBMITTED', label: 'Submitted', date: claim.submitted_date },
    { key: 'CERTIFIED', label: 'Certified', date: claim.certified_date },
    { key: 'PAID', label: 'Paid', date: claim.payment_date },
  ];

  const currentIndex = steps.findIndex((step) => step.key === claim.status);

  return (
    <div className="space-y-4">
      {steps.map((step, index) => {
        const completed = currentIndex >= index;

        return (
          <div key={step.key} className="flex items-start gap-3">
            <div
              className={cn(
                'mt-0.5 h-6 w-6 rounded-full flex items-center justify-center border',
                completed ? 'bg-success-100 border-success-300 text-success-700' : 'bg-gray-100 border-gray-300 text-gray-400'
              )}
            >
              <CheckCircle2 className="h-4 w-4" />
            </div>
            <div>
              <p className={cn('font-medium', completed ? 'text-gray-900' : 'text-gray-500')}>{step.label}</p>
              <p className="text-xs text-gray-500">{step.date ? formatDateTime(step.date) : 'Pending'}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
