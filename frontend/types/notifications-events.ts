// ============================================================================
// SYSTEM EVENT TYPES
// ============================================================================

export interface SystemEvent {
  id: string;
  event_type: string;
  category: string;
  severity: 'debug' | 'info' | 'warning' | 'error' | 'critical';
  user?: number;
  user_name?: string;
  message: string;
  description?: string;
  object_type?: string;
  object_id?: string;
  ip_address?: string;
  user_agent?: string;
  timestamp: string;
  metadata?: Record<string, any>;
}

export interface ActivityFeedItem {
  id: string;
  type: string;
  title: string;
  description: string;
  user_name: string;
  timestamp: string;
  entity_type?: string;
  entity_id?: string;
  icon?: string;
  color?: string;
}
