// ============================================================================
// ACTIVITY SERVICE
// ============================================================================

import { api } from './apiClient';
import type { Activity, ActivityQueryParams, PaginatedResponse } from '@/types';

function asRecord(value: unknown): Record<string, unknown> {
  return value && typeof value === 'object' ? (value as Record<string, unknown>) : {};
}

function extractPerformedBy(raw: Record<string, unknown>): string {
  if (typeof raw.performed_by_name === 'string' && raw.performed_by_name.trim()) {
    return raw.performed_by_name;
  }

  if (typeof raw.user_name === 'string' && raw.user_name.trim()) {
    return raw.user_name;
  }

  if (typeof raw.performed_by === 'string' && raw.performed_by.trim()) {
    return raw.performed_by;
  }

  const performedByObj = asRecord(raw.performed_by);
  if (typeof performedByObj.full_name === 'string' && performedByObj.full_name.trim()) {
    return String(performedByObj.full_name);
  }
  if (typeof performedByObj.username === 'string' && performedByObj.username.trim()) {
    return String(performedByObj.username);
  }

  return 'System';
}

function normalize(rawInput: unknown): Activity {
  const raw = asRecord(rawInput);

  const module = String(raw.module || 'PROJECT').toUpperCase();
  const eventType = String(raw.event_type || 'UPDATE').toUpperCase();
  const entityId = String(raw.entity_id || raw.id || '');

  const entityReference =
    String(raw.entity_reference || raw.reference || '').trim() ||
    `${module}-${entityId || 'N/A'}`;

  return {
    id: String(raw.id || ''),
    event_type: eventType,
    module,
    entity_id: entityId,
    entity_reference: entityReference,
    description: String(raw.description || `${module} ${entityReference} ${eventType.toLowerCase()}`),
    metadata: asRecord(raw.metadata),
    performed_by: extractPerformedBy(raw),
    timestamp: String(raw.timestamp || raw.created_at || new Date().toISOString()),
  };
}

function normalizeList(data: PaginatedResponse<unknown> | unknown[]): PaginatedResponse<Activity> | Activity[] {
  if (Array.isArray(data)) return data.map(normalize);

  return {
    ...data,
    results: (data.results || []).map(normalize),
  } as PaginatedResponse<Activity>;
}

export const activityService = {
  async getActivities(params?: ActivityQueryParams): Promise<PaginatedResponse<Activity> | Activity[]> {
    const data = await api.get<PaginatedResponse<unknown> | unknown[]>('/activities/', {
      params,
    });

    return normalizeList(data);
  },

  async getActivity(id: string): Promise<Activity> {
    const data = await api.get<unknown>(`/activities/${id}/`);
    return normalize(data);
  },
};
