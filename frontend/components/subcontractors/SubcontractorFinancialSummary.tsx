import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { formatCurrency } from '@/utils/formatters';
import type { Subcontractor } from '@/types';

interface SubcontractorFinancialSummaryProps {
  subcontractor: Subcontractor;
}

export function SubcontractorFinancialSummary({ subcontractor }: SubcontractorFinancialSummaryProps) {
  const total = Number(subcontractor.total_contract_value || 0);
  const paid = Number(subcontractor.total_paid || 0);
  const outstanding = Number(subcontractor.outstanding_balance || Math.max(total - paid, 0));

  return (
    <Card>
      <CardHeader>
        <CardTitle>Financial Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Total Contract Value</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(total)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Total Paid</p>
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
