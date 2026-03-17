// ============================================================================
// NOTIFICATION TYPES
// Spec-aligned notification entity definitions
// ============================================================================

export enum NotificationType {
  INFO = 'INFO',
  SUCCESS = 'SUCCESS',
  WARNING = 'WARNING',
  ERROR = 'ERROR',
}

export enum NotificationPriority {
  LOW = 'LOW',
  MEDIUM = 'MEDIUM',
  HIGH = 'HIGH',
}

export interface Notification {
  id: string;
  title: string;
  message: string;
  type: NotificationType | string;
  module?: string;
  entity_id?: string;
  entity_reference?: string;
  is_read: boolean;
  created_at: string;
  action_url?: string;
  priority?: NotificationPriority | string;
}

export interface NotificationQueryParams {
  is_read?: boolean;
  page?: number;
  page_size?: number;
}
