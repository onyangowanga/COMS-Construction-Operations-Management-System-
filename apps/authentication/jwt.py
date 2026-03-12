"""
JWT Utilities
Custom JWT token handling with HTTP-only cookies.
"""
from datetime import timedelta
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError

from .constants import JWT_ACCESS_MINUTES, JWT_REFRESH_DAYS


def get_tokens_for_user(user):
    """
    Generate JWT tokens for a user.
    
    Args:
        user: User instance
    
    Returns:
        dict: Contains 'access' and 'refresh' tokens
    """
    refresh = RefreshToken.for_user(user)
    
    # Add custom claims
    refresh['email'] = user.email
    refresh['username'] = user.username
    refresh['system_role'] = user.system_role
    
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def set_jwt_cookies(response, tokens):
    """
    Set JWT tokens in HTTP-only cookies.
    
    Args:
        response: Django Response object
        tokens: Dict with 'access' and 'refresh' tokens
    """
    # Access token cookie (15 minutes)
    response.set_cookie(
        key='access_token',
        value=tokens['access'],
        max_age=JWT_ACCESS_MINUTES * 60,  # Convert to seconds
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path='/',
    )
    
    # Refresh token cookie (7 days)
    response.set_cookie(
        key='refresh_token',
        value=tokens['refresh'],
        max_age=JWT_REFRESH_DAYS * 24 * 60 * 60,  # Convert to seconds
        httponly=True,
        secure=settings.SESSION_COOKIE_SECURE,
        samesite=settings.SESSION_COOKIE_SAMESITE,
        path='/api/auth/',  # Only send to auth endpoints
    )


def clear_jwt_cookies(response):
    """
    Clear JWT cookies on logout.
    
    Args:
        response: Django Response object
    """
    response.delete_cookie('access_token', path='/')
    response.delete_cookie('refresh_token', path='/api/auth/')


def get_token_from_cookie(request, token_type='access'):
    """
    Extract JWT token from cookie.
    
    Args:
        request: Django Request object
        token_type: 'access' or 'refresh'
    
    Returns:
        str: Token string or None
    """
    cookie_name = f'{token_type}_token'
    return request.COOKIES.get(cookie_name)


def blacklist_refresh_token(refresh_token_str):
    """
    Blacklist a refresh token.
    
    Args:
        refresh_token_str: Refresh token string
    
    Returns:
        bool: True if blacklisted successfully, False otherwise
    """
    try:
        token = RefreshToken(refresh_token_str)
        token.blacklist()
        return True
    except TokenError:
        return False


def verify_token(token_str):
    """
    Verify a JWT token.
    
    Args:
        token_str: Token string
    
    Returns:
        dict: Token payload if valid, None if invalid
    """
    try:
        from rest_framework_simplejwt.tokens import AccessToken
        token = AccessToken(token_str)
        return dict(token.payload)
    except TokenError:
        return None
