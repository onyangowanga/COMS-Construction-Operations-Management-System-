'use client';

import React, { useMemo, useState } from 'react';
import Link from 'next/link';
import { Card, CardContent } from '@/components/ui';
import { useApi } from '@/hooks';
import {
  claimService,
  documentService,
  procurementService,
  projectService,
  variationService,
} from '@/services';
import { cn } from '@/utils/helpers';

type ContractModuleTab = 'overview' | 'projects' | 'documents' | 'variations' | 'claims' | 'procurement';

type MinimalItem = {
  id: string;
  label: string;
  status?: string;
};

const tabs: Array<{ key: ContractModuleTab; label: string }> = [
  { key: 'overview', label: 'Overview' },
  { key: 'projects', label: 'Projects' },
  { key: 'documents', label: 'Documents' },
  { key: 'variations', label: 'Variations' },
  { key: 'claims', label: 'Claims' },
  { key: 'procurement', label: 'Procurement' },
];

function extractResults<T>(data: unknown): { items: T[]; total: number } {
  if (Array.isArray(data)) {
    return { items: data, total: data.length };
  }

  if (data && typeof data === 'object' && 'results' in data && Array.isArray((data as { results: unknown[] }).results)) {
    const results = (data as { results: T[]; count?: number }).results;
    const total = Number((data as { count?: number }).count || 0);
    return { items: results, total };
  }

  return { items: [], total: 0 };
}

function toMinimalItems(items: unknown[], labelKeys: string[]): MinimalItem[] {
  return items.map((item, index) => {
    const record = (item && typeof item === 'object' ? item : {}) as Record<string, unknown>;
    const id = String(record.id || index);
    const status = record.status ? String(record.status) : undefined;

    const label =
      labelKeys
        .map((key) => record[key])
        .find((value) => typeof value === 'string' && String(value).trim().length > 0) ||
      `Item ${index + 1}`;

    return {
      id,
      label: String(label),
      status,
    };
  });
}

interface ContractModulesTabsProps {
  contractId: string;
  contractNumber: string;
}

export function ContractModulesTabs({ contractId, contractNumber }: ContractModulesTabsProps) {
  const [activeTab, setActiveTab] = useState<ContractModuleTab>('overview');
  const { useQuery } = useApi();

  const projectQuery = useQuery(
    ['contract-projects', contractId],
    () => projectService.getProjects({ page: 1, page_size: 5, ordering: '-created_at', contract_id: contractId }),
    { enabled: activeTab === 'projects' }
  );

  const documentQuery = useQuery(
    ['contract-documents', contractId],
    () => documentService.getDocuments({ page: 1, page_size: 5, ordering: '-uploaded_at', contract_id: contractId } as never),
    { enabled: activeTab === 'documents' }
  );

  const variationQuery = useQuery(
    ['contract-variations', contractId],
    () => variationService.getVariations({ page: 1, page_size: 5, ordering: '-created_at', contract_id: contractId } as never),
    { enabled: activeTab === 'variations' }
  );

  const claimQuery = useQuery(
    ['contract-claims', contractId],
    () => claimService.getClaims({ page: 1, page_size: 5, ordering: '-created_at', contract_id: contractId } as never),
    { enabled: activeTab === 'claims' }
  );

  const procurementQuery = useQuery(
    ['contract-procurement', contractId],
    () => procurementService.getOrders({ page: 1, page_size: 5, ordering: '-created_at', contract_id: contractId } as never),
    { enabled: activeTab === 'procurement' }
  );

  const tabData = useMemo(() => {
    const projects = extractResults<Record<string, unknown>>(projectQuery.data);
    const documents = extractResults<Record<string, unknown>>(documentQuery.data);
    const variations = extractResults<Record<string, unknown>>(variationQuery.data);
    const claims = extractResults<Record<string, unknown>>(claimQuery.data);
    const procurement = extractResults<Record<string, unknown>>(procurementQuery.data);

    return {
      projects: {
        ...projects,
        mapped: toMinimalItems(projects.items, ['name', 'project_name', 'code']),
        href: '/projects',
      },
      documents: {
        ...documents,
        mapped: toMinimalItems(documents.items, ['title', 'name', 'document_type_display']),
        href: '/documents',
      },
      variations: {
        ...variations,
        mapped: toMinimalItems(variations.items, ['variation_number', 'title', 'reference_number']),
        href: '/variations',
      },
      claims: {
        ...claims,
        mapped: toMinimalItems(claims.items, ['claim_number', 'title', 'project_name']),
        href: '/claims',
      },
      procurement: {
        ...procurement,
        mapped: toMinimalItems(procurement.items, ['reference_number', 'lpo_number', 'description']),
        href: '/procurement',
      },
    };
  }, [claimQuery.data, documentQuery.data, procurementQuery.data, projectQuery.data, variationQuery.data]);

  const renderModuleList = (
    title: string,
    isLoading: boolean,
    items: MinimalItem[],
    total: number,
    href: string
  ) => {
    if (isLoading) {
      return <p className="text-sm text-gray-500">Loading {title.toLowerCase()}...</p>;
    }

    if (items.length === 0) {
      return <p className="text-sm text-gray-500">No {title.toLowerCase()} found for this contract.</p>;
    }

    return (
      <div className="space-y-3">
        <div className="text-sm text-gray-500">Showing {items.length} of {total} records</div>
        <div className="space-y-2">
          {items.map((item) => (
            <div key={item.id} className="flex items-center justify-between rounded-lg border border-gray-200 p-3">
              <div>
                <p className="font-medium text-gray-900">{item.label}</p>
                {item.status ? <p className="text-xs text-gray-500 mt-1">Status: {item.status}</p> : null}
              </div>
            </div>
          ))}
        </div>
        <Link href={`${href}?contract_id=${contractId}`} className="text-sm font-medium text-primary-700 hover:text-primary-900">
          Open full {title.toLowerCase()} module
        </Link>
      </div>
    );
  };

  return (
    <Card>
      <CardContent>
        <div className="border-b border-gray-200 overflow-x-auto">
          <div className="flex gap-1 min-w-max">
            {tabs.map((tab) => (
              <button
                key={tab.key}
                type="button"
                onClick={() => setActiveTab(tab.key)}
                className={cn(
                  'px-4 py-2.5 text-sm font-medium border-b-2 transition-colors',
                  activeTab === tab.key
                    ? 'text-primary-700 border-primary-600'
                    : 'text-gray-600 border-transparent hover:text-gray-900 hover:border-gray-300'
                )}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>

        <div className="pt-4">
          {activeTab === 'overview' ? (
            <div className="space-y-2">
              <p className="text-gray-700">Contract <span className="font-semibold">{contractNumber}</span> is the parent scope for all downstream modules.</p>
              <p className="text-sm text-gray-500">Use tabs to view projects, documents, variations, claims, and procurement records linked via contract_id.</p>
            </div>
          ) : null}

          {activeTab === 'projects'
            ? renderModuleList('Projects', projectQuery.isLoading, tabData.projects.mapped, tabData.projects.total, tabData.projects.href)
            : null}
          {activeTab === 'documents'
            ? renderModuleList('Documents', documentQuery.isLoading, tabData.documents.mapped, tabData.documents.total, tabData.documents.href)
            : null}
          {activeTab === 'variations'
            ? renderModuleList('Variations', variationQuery.isLoading, tabData.variations.mapped, tabData.variations.total, tabData.variations.href)
            : null}
          {activeTab === 'claims'
            ? renderModuleList('Claims', claimQuery.isLoading, tabData.claims.mapped, tabData.claims.total, tabData.claims.href)
            : null}
          {activeTab === 'procurement'
            ? renderModuleList('Procurement', procurementQuery.isLoading, tabData.procurement.mapped, tabData.procurement.total, tabData.procurement.href)
            : null}
        </div>
      </CardContent>
    </Card>
  );
}
