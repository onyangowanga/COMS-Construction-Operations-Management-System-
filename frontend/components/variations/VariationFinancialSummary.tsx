import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { formatCurrency } from '@/utils/formatters';
import type { VariationOrder } from '@/types';

interface VariationFinancialSummaryProps {
  variation: VariationOrder;
}

export function VariationFinancialSummary({ variation }: VariationFinancialSummaryProps) {
  const estimated = Number(variation.estimated_value || 0);
  const approved = Number(variation.approved_value || 0);
  const paid = Number(variation.paid_value || 0);
  const outstanding = Math.max(approved - paid, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Financial Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Estimated</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(estimated)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Approved</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(approved)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Paid</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(paid)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Outstanding</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(outstanding)}</p>
        </div>
      </CardContent>
    </Card>
  );
}
