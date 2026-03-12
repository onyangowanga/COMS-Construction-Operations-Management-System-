"""
Event Logging Middleware

This middleware automatically logs:
- User login/logout events
- API requests and responses
- Performance metrics (request duration)
- Error tracking
"""

import time
from django.utils.deprecation import MiddlewareMixin
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from typing import Optional

from apps.events.models import SystemEvent
from apps.events.services import EventLoggingService, get_client_ip, get_user_agent


class EventLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to automatically log API requests and responses.
    
    This middleware:
    - Logs all API requests (configurable paths)
    - Tracks request duration for performance monitoring
    - Logs errors (4xx, 5xx responses)
    - Excludes static files and health checks
    """
    
    # Paths to exclude from logging
    EXCLUDED_PATHS = [
        '/static/',
        '/media/',
        '/health/',
        '/favicon.ico',
        '/admin/jsi18n/',
    ]
    
    # Paths to include (log only API requests by default)
    INCLUDED_PATHS = [
        '/api/',
    ]
    
    def process_request(self, request):
        """Mark the start time of the request"""
        request._event_start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """
        Log the request after processing.
        
        Args:
            request: Django request object
            response: Django response object
            
        Returns:
            Response object (unmodified)
        """
        # Skip excluded paths
        if self._should_exclude_path(request.path):
            return response
        
        # Only log included paths (API requests)
        if not self._should_include_path(request.path):
            return response
        
        # Calculate request duration
        duration_ms = None
        if hasattr(request, '_event_start_time'):
            duration_ms = int((time.time() - request._event_start_time) * 1000)
        
        # Log the API request
        try:
            user = request.user if request.user.is_authenticated else None
            
            EventLoggingService.log_api_request(
                user=user,
                request_path=request.path,
                request_method=request.method,
                response_status=response.status_code,
                duration_ms=duration_ms,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                metadata={
                    'query_params': dict(request.GET),
                    'content_type': request.content_type,
                }
            )
        except Exception as e:
            # Don't let logging errors break the application
            print(f"Error logging event: {e}")
        
        return response
    
    def _should_exclude_path(self, path: str) -> bool:
        """Check if path should be excluded from logging"""
        return any(path.startswith(excluded) for excluded in self.EXCLUDED_PATHS)
    
    def _should_include_path(self, path: str) -> bool:
        """Check if path should be included in logging"""
        return any(path.startswith(included) for included in self.INCLUDED_PATHS)


# Signal handlers for authentication events
@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """
    Log user login events.
    
    This signal handler is triggered when a user successfully logs in.
    """
    try:
        EventLoggingService.log_authentication_event(
            event_type=SystemEvent.USER_LOGIN,
            user=user,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            success=True,
            metadata={
                'login_method': 'credentials',  # Could be extended for OAuth, etc.
            }
        )
    except Exception as e:
        print(f"Error logging user login: {e}")


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """
    Log user logout events.
    
    This signal handler is triggered when a user logs out.
    """
    try:
        if user:  # user might be None if session expired
            EventLoggingService.log_authentication_event(
                event_type=SystemEvent.USER_LOGOUT,
                user=user,
                ip_address=get_client_ip(request) if request else None,
                user_agent=get_user_agent(request) if request else None,
                success=True
            )
    except Exception as e:
        print(f"Error logging user logout: {e}")
