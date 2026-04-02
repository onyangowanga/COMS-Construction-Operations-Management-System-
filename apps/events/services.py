"""
Event Logging Services

This module provides services for creating and managing system events.
These services should be used throughout the application to log significant activities.
"""

from django.utils import timezone
from django.contrib.contenttypes.models import ContentType
from typing import Optional, Dict, Any
from datetime import timedelta

from apps.events.models import SystemEvent


class EventLoggingService:
    """
    Service for creating and managing system events.
    
    This service provides methods to log events throughout the application.
    All significant user actions, system events, and entity changes should be logged.
    """
    
    @staticmethod
    def log_event(
        event_type: str,
        user=None,
        organization=None,
        project=None,
        entity=None,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        request_path: Optional[str] = None,
        request_method: Optional[str] = None,
        response_status: Optional[int] = None,
        duration_ms: Optional[int] = None
    ) -> SystemEvent:
        """
        Create a new system event log entry.
        
        Args:
            event_type: Type of event (must be valid SystemEvent.EVENT_TYPE_CHOICES)
            user: User who triggered the event
            organization: Organization context
            project: Project context
            entity: Any Django model instance to link to this event
            metadata: Additional event data as dict
            ip_address: IP address of the request
            user_agent: User agent string
            request_path: Request path (for API events)
            request_method: HTTP method
            response_status: HTTP response status code
            duration_ms: Request duration in milliseconds
            
        Returns:
            Created SystemEvent instance
            
        Example:
            from apps.events.services import EventLoggingService
            
            event = EventLoggingService.log_event(
                event_type=SystemEvent.VARIATION_APPROVED,
                user=request.user,
                organization=variation.organization,
                project=variation.project,
                entity=variation,
                metadata={
                    'variation_number': variation.variation_number,
                    'amount': str(variation.amount),
                    'approved_by': request.user.get_full_name()
                },
                ip_address=get_client_ip(request)
            )
        """
        event = SystemEvent(
            event_type=event_type,
            user=user,
            organization=organization,
            project=project,
            metadata=metadata or {},
            ip_address=ip_address,
            user_agent=user_agent or '',
            request_path=request_path or '',
            request_method=request_method or '',
            response_status=response_status,
            duration_ms=duration_ms
        )
        
        # Link entity if provided
        if entity:
            event.entity = entity
        
        event.save()
        return event
    
    @staticmethod
    def log_authentication_event(
        event_type: str,
        user,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        success: bool = True,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Log authentication-related events (login, logout, password changes).
        
        Args:
            event_type: Type of auth event (USER_LOGIN, USER_LOGOUT, etc.)
            user: User instance
            ip_address: IP address
            user_agent: User agent string
            success: Whether the action was successful
            metadata: Additional metadata
            
        Returns:
            Created SystemEvent instance
        """
        meta = metadata or {}
        meta['success'] = success
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=getattr(user, 'organization', None),
            metadata=meta,
            ip_address=ip_address,
            user_agent=user_agent
        )
    
    @staticmethod
    def log_document_event(
        event_type: str,
        document,
        user,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> SystemEvent:
        """
        Log document-related events.
        
        Args:
            event_type: Type of document event
            document: Document instance
            user: User who performed the action
            metadata: Additional metadata
            ip_address: IP address
            
        Returns:
            Created SystemEvent instance
        """
        meta = metadata or {}
        meta.update({
            'document_name': document.name,
            'document_type': document.document_type,
            'file_size': document.file.size if hasattr(document, 'file') else None
        })
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=document.organization,
            project=document.project,
            entity=document,
            metadata=meta,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_variation_event(
        event_type: str,
        variation,
        user,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> SystemEvent:
        """
        Log variation-related events.
        
        Args:
            event_type: Type of variation event
            variation: Variation instance
            user: User who performed the action
            metadata: Additional metadata
            ip_address: IP address
            
        Returns:
            Created SystemEvent instance
        """
        meta = metadata or {}
        meta.update({
            'variation_number': variation.variation_number,
            'amount': str(variation.amount),
            'status': variation.status,
            'title': variation.title
        })
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=variation.organization,
            project=variation.project,
            entity=variation,
            metadata=meta,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_claim_event(
        event_type: str,
        claim,
        user,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> SystemEvent:
        """
        Log claim/valuation-related events.
        
        Args:
            event_type: Type of claim event
            claim: Claim instance
            user: User who performed the action
            metadata: Additional metadata
            ip_address: IP address
            
        Returns:
            Created SystemEvent instance
        """
        meta = metadata or {}
        meta.update({
            'claim_number': claim.claim_number,
            'amount': str(claim.total_amount),
            'status': claim.status,
            'period_start': claim.period_start.isoformat() if hasattr(claim, 'period_start') else None,
            'period_end': claim.period_end.isoformat() if hasattr(claim, 'period_end') else None
        })
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=claim.organization,
            project=claim.project,
            entity=claim,
            metadata=meta,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_payment_event(
        event_type: str,
        payment,
        user,
        metadata: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> SystemEvent:
        """
        Log payment-related events.
        
        Args:
            event_type: Type of payment event
            payment: Payment instance
            user: User who performed the action
            metadata: Additional metadata
            ip_address: IP address
            
        Returns:
            Created SystemEvent instance
        """
        meta = metadata or {}
        meta.update({
            'payment_reference': payment.reference,
            'amount': str(payment.amount),
            'payment_method': payment.payment_method,
            'status': payment.status
        })
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=payment.organization,
            project=payment.project,
            entity=payment,
            metadata=meta,
            ip_address=ip_address
        )
    
    @staticmethod
    def log_api_request(
        user,
        request_path: str,
        request_method: str,
        response_status: int,
        duration_ms: Optional[int] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> SystemEvent:
        """
        Log API request events.
        
        Args:
            user: User making the request
            request_path: Request path
            request_method: HTTP method
            response_status: Response status code
            duration_ms: Request duration in milliseconds
            ip_address: IP address
            user_agent: User agent string
            metadata: Additional metadata
            
        Returns:
            Created SystemEvent instance
        """
        event_type = SystemEvent.API_ERROR if response_status >= 400 else SystemEvent.API_REQUEST
        
        return EventLoggingService.log_event(
            event_type=event_type,
            user=user,
            organization=getattr(user, 'organization', None),
            request_path=request_path,
            request_method=request_method,
            response_status=response_status,
            duration_ms=duration_ms,
            ip_address=ip_address,
            user_agent=user_agent,
            metadata=metadata or {}
        )
    
    @staticmethod
    def get_entity_events(entity, limit: Optional[int] = None):
        """
        Get all events related to a specific entity.
        
        Args:
            entity: Django model instance
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        from apps.events.event_selectors import EventSelector
        
        content_type = ContentType.objects.get_for_model(entity)
        return EventSelector.get_entity_events(
            entity_type=content_type.model,
            entity_id=str(entity.pk),
            limit=limit
        )
    
    @staticmethod
    def get_project_events(project, event_types=None, days=None):
        """
        Get all events for a specific project.
        
        Args:
            project: Project instance
            event_types: Optional list of event types to filter
            days: Number of days to look back
            
        Returns:
            QuerySet of SystemEvent objects
        """
        from apps.events.event_selectors import EventSelector
        return EventSelector.get_project_events(project, event_types, days)
    
    @staticmethod
    def get_user_activity(user, days=None, limit=None):
        """
        Get activity log for a specific user.
        
        Args:
            user: User instance
            days: Number of days to look back
            limit: Maximum number of results
            
        Returns:
            QuerySet of SystemEvent objects
        """
        from apps.events.event_selectors import EventSelector
        return EventSelector.get_user_activity(user, days, limit)
    
    @staticmethod
    def cleanup_old_events(days: int = 365):
        """
        Delete events older than specified days.
        
        This should be run periodically to prevent unlimited growth
        of the events table.
        
        Args:
            days: Delete events older than this many days
            
        Returns:
            Number of deleted events
        """
        cutoff_date = timezone.now() - timedelta(days=days)
        deleted_count, _ = SystemEvent.objects.filter(
            timestamp__lt=cutoff_date
        ).delete()
        
        return deleted_count


def get_client_ip(request) -> Optional[str]:
    """
    Extract client IP address from request.
    
    Args:
        request: Django request object
        
    Returns:
        IP address string or None
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request) -> str:
    """
    Extract user agent from request.
    
    Args:
        request: Django request object
        
    Returns:
        User agent string
    """
    return request.META.get('HTTP_USER_AGENT', '')
