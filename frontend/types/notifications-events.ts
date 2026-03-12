// ============================================================================
// NOTIFICATION TYPES
// ============================================================================

export interface Notification {
  id: string;
  recipient: number;
  notification_type: NotificationType;
  title: string;
  message: string;
  priority: 'low' | 'medium' | 'high' | 'critical';
  is_read: boolean;
  read_at?: string;
  related_object_type?: string;
  related_object_id?: string;
  action_url?: string;
  created_at: string;
  metadata?: Record<string, any>;
}

export enum NotificationType {
  INFO = 'info',
  SUCCESS = 'success',
  WARNING = 'warning',
  ERROR = 'error',
  APPROVAL_REQUIRED = 'approval_required',
  DOCUMENT_UPLOADED = 'document_uploaded',
  VARIATION_CREATED = 'variation_created',
  CLAIM_SUBMITTED = 'claim_submitted',
  PAYMENT_APPROVED = 'payment_approved',
}

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
