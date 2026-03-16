import React from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui';
import { formatCurrency } from '@/utils/formatters';
import type { ProcurementOrder } from '@/types';

interface ProcurementFinancialSummaryProps {
  order: ProcurementOrder;
}

export function ProcurementFinancialSummary({ order }: ProcurementFinancialSummaryProps) {
  const orderValue = Number(order.order_value || 0);

  return (
    <Card>
      <CardHeader>
        <CardTitle>Procurement Financial Summary</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Order Value</p>
          <p className="text-lg font-semibold text-gray-900">{formatCurrency(orderValue)}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Status</p>
          <p className="text-lg font-semibold text-gray-900">{String(order.status || '').replace('_', ' ')}</p>
        </div>
        <div>
          <p className="text-xs uppercase tracking-wide text-gray-500">Delivery Date</p>
          <p className="text-lg font-semibold text-gray-900">{order.delivery_date || 'Not set'}</p>
        </div>
      </CardContent>
    </Card>
  );
}
