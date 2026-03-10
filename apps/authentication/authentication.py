"""
Custom JWT Authentication
Authenticates users using JWT tokens from HTTP-only cookies.
"""
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken


class JWTCookieAuthentication(JWTAuthentication):
    """
    Custom JWT authentication class that reads tokens from cookies
    instead of Authorization header.
    
    Falls back to header authentication if cookie is not present.
    """
    
    def authenticate(self, request):
        """
        Try to authenticate using cookie first, then fall back to header.
        """
        # Try to get token from cookie
        cookie_token = request.COOKIES.get('access_token')
        
        if cookie_token:
            try:
                validated_token = self.get_validated_token(cookie_token)
                return self.get_user(validated_token), validated_token
            except InvalidToken:
                pass  # Fall through to try header authentication
        
        # Fall back to standard header authentication
        return super().authenticate(request)
