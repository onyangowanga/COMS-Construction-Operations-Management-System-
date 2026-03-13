import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { formatCurrency } from '@/utils/formatters';
import type { Claim } from '@/types';

interface ClaimFinancialSummaryProps {
  claim: Claim;
}

export function ClaimFinancialSummary({ claim }: ClaimFinancialSummaryProps) {
  const claimed = Number(claim.claim_amount || claim.gross_amount || 0);
  const certified = Number(claim.certified_amount || 0);
  const paid = claim.status === 'PAID' ? certified : 0;
  const outstanding = Math.max(certified - paid, 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Claim Financial Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Claimed</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(claimed)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Certified</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(certified)}</p>
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
