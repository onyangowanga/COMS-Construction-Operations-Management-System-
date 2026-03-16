'use client';

import React from 'react';
import { useRouter } from 'next/navigation';
import { Button, LoadingSpinner } from '@/components/ui';
import { useProcurement } from '@/hooks';
import { formatCurrency, formatDate } from '@/utils/formatters';

interface SupplierOrdersListProps {
  supplierId: string;
}

export function SupplierOrdersList({ supplierId }: SupplierOrdersListProps) {
  const router = useRouter();
  const { orders, isLoading } = useProcurement({
    page: 1,
    page_size: 10,
    supplier: supplierId,
    ordering: '-created_at',
  });

  if (isLoading) {
    return (
      <div className="py-8 flex justify-center">
        <LoadingSpinner />
      </div>
    );
  }

  if (!orders.length) {
    return <p className="text-sm text-gray-500">No procurement orders linked to this supplier yet.</p>;
  }

  return (
    <div className="space-y-3">
      {orders.map((order) => (
        <div
          key={order.id}
          className="border border-gray-200 rounded-lg p-4 flex flex-col md:flex-row md:items-center md:justify-between gap-3"
        >
          <div>
            <p className="font-semibold text-gray-900">{order.reference_number}</p>
            <p className="text-sm text-gray-600">{order.project_name || order.project}</p>
            <p className="text-sm text-gray-500 mt-1">
              {formatCurrency(order.order_value || 0)} • {order.delivery_date ? formatDate(order.delivery_date) : 'No delivery deadline'}
            </p>
          </div>
          <Button variant="outline" size="sm" onClick={() => router.push(`/procurement/${order.id}`)}>
            View Order
          </Button>
        </div>
      ))}
    </div>
  );
}
