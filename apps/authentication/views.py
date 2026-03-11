"""
Authentication Views
Thin views following service layer pattern.
Business logic is in services, queries in selectors, validation in serializers.
"""
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django.contrib.auth import authenticate, login, logout
from django.db import transaction
from django.utils import timezone

from .serializers import (
    LoginSerializer,
    RegisterSerializer,
    TokenRefreshSerializer,
    ChangePasswordSerializer,
    UserProfileSerializer,
    UserUpdateSerializer,
    PasswordResetRequestSerializer,
    PasswordResetConfirmSerializer,
)
from .services import SecurityService, OrganizationService
from .selectors import UserSelectors
from .jwt import (
    get_tokens_for_user,
    set_jwt_cookies,
    clear_jwt_cookies,
    get_token_from_cookie,
    blacklist_refresh_token,
)
from .models import User, AuditLog
from .constants import ACCOUNT_LOCKED_MESSAGE, EMAIL_NOT_VERIFIED_MESSAGE


def get_client_ip(request):
    """Extract client IP from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_user_agent(request):
    """Extract user agent from request"""
    return request.META.get('HTTP_USER_AGENT', '')


class LoginView(APIView):
    """
    User login endpoint.
    
    POST /api/auth/login/
    Body: {"email": "user@example.com", "password": "password123"}
    
    Returns JWT tokens in HTTP-only cookies and user profile.
    Integrates with django-axes for throttling.
    """
    permission_classes = [AllowAny]
    serializer_class = LoginSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Get user
        user = UserSelectors.get_by_email(email)
        
        if not user:
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if account is locked
        if SecurityService.is_account_locked(user):
            lock_minutes = (user.locked_until - timezone.now()).seconds // 60
            return Response(
                {'detail': ACCOUNT_LOCKED_MESSAGE.format(minutes=lock_minutes)},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Check if email is verified (if required)
        from .constants import REQUIRE_EMAIL_VERIFICATION
        if REQUIRE_EMAIL_VERIFICATION and not user.is_verified:
            return Response(
                {'detail': EMAIL_NOT_VERIFIED_MESSAGE},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Authenticate user
        user = authenticate(request, username=user.username, password=password)
        
        if not user:
            # Record failed login
            failed_user = UserSelectors.get_by_email(email)
            if failed_user:
                is_locked = SecurityService.record_failed_login(failed_user)
                
                # Log failed attempt
                AuditLog.objects.create(
                    user=failed_user,
                    action=AuditLog.Action.LOGIN_FAILED,
                    ip_address=get_client_ip(request),
                    user_agent=get_user_agent(request),
                    details={'email': email, 'locked': is_locked}
                )
                
                if is_locked:
                    return Response(
                        {'detail': ACCOUNT_LOCKED_MESSAGE.format(minutes=30)},
                        status=status.HTTP_403_FORBIDDEN
                    )
            
            return Response(
                {'detail': 'Invalid email or password.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        # Check if user is active
        if not user.is_active:
            return Response(
                {'detail': 'This account has been deactivated.'},
                status=status.HTTP_403_FORBIDDEN
            )
        
        # Establish Django session (required for @login_required decorator)
        login(request, user)
        
        # Reset failed attempts on successful login
        SecurityService.reset_failed_attempts(user)
        
        # Update last login IP
        SecurityService.update_last_login_ip(user, get_client_ip(request))
        
        # Generate tokens
        tokens = get_tokens_for_user(user)
        
        # Log successful login
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.USER_LOGIN,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={'email': email}
        )
        
        # Prepare response with user profile
        user_data = UserProfileSerializer(user).data
        response = Response({
            'user': user_data,
            'message': 'Login successful'
        }, status=status.HTTP_200_OK)
        
        # Set tokens in HTTP-only cookies
        set_jwt_cookies(response, tokens)
        
        return response


class LogoutView(APIView):
    """
    User logout endpoint.
    
    POST /api/auth/logout/
    
    Blacklists refresh token and clears cookies.
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        # Get refresh token from cookie
        refresh_token = get_token_from_cookie(request, 'refresh')
        
        # Blacklist the refresh token
        if refresh_token:
            blacklist_refresh_token(refresh_token)
        
        # Log logout
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.USER_LOGOUT,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        
        # Clear Django session
        logout(request)
        
        # Clear cookies and redirect
        response = Response({
            'message': 'Logout successful',
            'redirect': '/login/'
        }, status=status.HTTP_200_OK)
        
        clear_jwt_cookies(response)
        
        return response


class RegisterView(APIView):
    """
    User registration endpoint.
    
    POST /api/auth/register/
    Body: {
        "email": "user@example.com",
        "username": "username",
        "password": "SecurePass123!",
        "password_confirm": "SecurePass123!",
        "first_name": "John",
        "last_name": "Doe",
        "phone": "+1234567890",
        "system_role": "client",
        "organization_id": 1
    }
    
    Creates new user account.
    """
    permission_classes = [AllowAny]
    serializer_class = RegisterSerializer
    
    @transaction.atomic
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Extract data
        data = serializer.validated_data
        organization_id = data.pop('organization_id', None)
        password_confirm = data.pop('password_confirm')
        password = data.pop('password')
        
        # Create user
        user = User.objects.create_user(
            password=password,
            **data
        )
        
        # Assign to organization if provided
        if organization_id:
            from .selectors import OrganizationSelectors
            organization = OrganizationSelectors.get_by_id(organization_id)
            if organization:
                OrganizationService.add_member(organization, user)
        
        # Log user creation
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.USER_CREATED,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={'email': user.email, 'system_role': user.system_role}
        )
        
        # Return user profile
        user_data = UserProfileSerializer(user).data
        
        return Response({
            'user': user_data,
            'message': 'Registration successful. Please verify your email.'
        }, status=status.HTTP_201_CREATED)


class TokenRefreshView(APIView):
    """
    Token refresh endpoint.
    
    POST /api/auth/token/refresh/
    
    Refreshes access token using refresh token from cookie.
    """
    permission_classes = [AllowAny]
    
    def post(self, request):
        # Get refresh token from cookie
        refresh_token = get_token_from_cookie(request, 'refresh')
        
        if not refresh_token:
            return Response(
                {'detail': 'Refresh token not found in cookies.'},
                status=status.HTTP_401_UNAUTHORIZED
            )
        
        try:
            from rest_framework_simplejwt.tokens import RefreshToken
            
            # Validate refresh token
            token = RefreshToken(refresh_token)
            
            # Get user
            user_id = token.payload.get('user_id')
            user = UserSelectors.get_by_id(user_id)
            
            if not user or not user.is_active:
                return Response(
                    {'detail': 'User not found or inactive.'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
            
            # Generate new tokens
            new_tokens = get_tokens_for_user(user)
            
            response = Response({
                'message': 'Token refreshed successfully'
            }, status=status.HTTP_200_OK)
            
            # Set new tokens in cookies
            set_jwt_cookies(response, new_tokens)
            
            return response
            
        except TokenError as e:
            return Response(
                {'detail': 'Invalid or expired refresh token.'},
                status=status.HTTP_401_UNAUTHORIZED
            )


class UserProfileView(APIView):
    """
    Get current user profile.
    
    GET /api/auth/me/
    
    Returns authenticated user's profile.
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def patch(self, request):
        """Update user profile"""
        serializer = UserUpdateSerializer(
            request.user,
            data=request.data,
            partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        # Log profile update
        AuditLog.objects.create(
            user=request.user,
            action=AuditLog.Action.USER_UPDATED,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
            details={'fields_updated': list(request.data.keys())}
        )
        
        return Response(
            UserProfileSerializer(request.user).data,
            status=status.HTTP_200_OK
        )


class ChangePasswordView(APIView):
    """
    Change password for authenticated user.
    
    POST /api/auth/change-password/
    Body: {
        "old_password": "current_password",
        "new_password": "new_password",
        "new_password_confirm": "new_password"
    }
    """
    permission_classes = [IsAuthenticated]
    serializer_class = ChangePasswordSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = request.user
        old_password = serializer.validated_data['old_password']
        new_password = serializer.validated_data['new_password']
        
        # Check old password
        if not user.check_password(old_password):
            return Response(
                {'detail': 'Current password is incorrect.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Set new password
        user.set_password(new_password)
        user.save()
        
        # Log password change
        AuditLog.objects.create(
            user=user,
            action=AuditLog.Action.PASSWORD_CHANGED,
            ip_address=get_client_ip(request),
            user_agent=get_user_agent(request),
        )
        
        return Response({
            'message': 'Password changed successfully.'
        }, status=status.HTTP_200_OK)


class PasswordResetRequestView(APIView):
    """
    Request password reset.
    
    POST /api/auth/password-reset/
    Body: {"email": "user@example.com"}
    
    Sends password reset email (to be implemented).
    """
    permission_classes = [AllowAny]
    serializer_class = PasswordResetRequestSerializer
    
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        user = UserSelectors.get_by_email(email)
        
        # Always return success to prevent email enumeration
        message = 'If an account exists with this email, a password reset link will be sent.'
        
        if user:
            # TODO: Generate reset token and send email
            # This would use a token generation service
            
            # Log password reset request
            AuditLog.objects.create(
                user=user,
                action=AuditLog.Action.PASSWORD_RESET,
                ip_address=get_client_ip(request),
                user_agent=get_user_agent(request),
                details={'email': email}
            )
        
        return Response({
            'message': message
        }, status=status.HTTP_200_OK)
