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
from django.db.models import Q
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404

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
from .auth_selectors import UserSelectors
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


@method_decorator(csrf_exempt, name='dispatch')
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


@method_decorator(csrf_exempt, name='dispatch')
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


@method_decorator(csrf_exempt, name='dispatch')
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


class UIPreferencesView(APIView):
    """Get/update UI preferences for current user."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response(
            {
                'theme': user.ui_theme,
                'timezone': user.ui_timezone,
                'language': user.ui_language,
                'compact_mode': user.ui_compact_mode,
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        user = request.user
        data = request.data

        if 'theme' in data:
            user.ui_theme = data['theme']
        if 'timezone' in data:
            user.ui_timezone = data['timezone']
        if 'language' in data:
            user.ui_language = data['language']
        if 'compact_mode' in data:
            user.ui_compact_mode = bool(data['compact_mode'])

        user.save(update_fields=['ui_theme', 'ui_timezone', 'ui_language', 'ui_compact_mode', 'updated_at'])

        return self.get(request)


class OrganizationSettingsView(APIView):
    """Get/update current user's organization settings."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org = request.user.organization
        if not org:
            return Response({'detail': 'User has no organization assigned.'}, status=status.HTTP_400_BAD_REQUEST)

        return Response(
            {
                'name': org.name,
                'code': org.registration_number or org.name[:4].upper(),
                'logo': org.logo.url if org.logo else None,
                'default_currency': org.default_currency or 'KES',
                'fiscal_year_start': org.fiscal_year_start or 'January 1',
            },
            status=status.HTTP_200_OK,
        )

    def patch(self, request):
        org = request.user.organization
        if not org:
            return Response({'detail': 'User has no organization assigned.'}, status=status.HTTP_400_BAD_REQUEST)

        data = request.data
        if 'name' in data:
            org.name = data['name']
        if 'code' in data:
            org.registration_number = data['code']
        if 'default_currency' in data:
            org.default_currency = str(data['default_currency']).upper()
        if 'fiscal_year_start' in data:
            org.fiscal_year_start = data['fiscal_year_start']

        org.save(update_fields=['name', 'registration_number', 'default_currency', 'fiscal_year_start', 'updated_at'])
        return self.get(request)


class UserManagementView(APIView):
    """List and create users for admin/system-admin pages."""
    permission_classes = [IsAuthenticated]

    def _check_admin(self, request):
        return request.user.is_staff or request.user.is_superuser

    def get(self, request):
        if not self._check_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        queryset = User.objects.select_related('organization').all().order_by('-date_joined')

        search = request.query_params.get('search')
        is_active = request.query_params.get('is_active')

        if search:
            queryset = queryset.filter(
                Q(username__icontains=search)
                | Q(email__icontains=search)
                | Q(first_name__icontains=search)
                | Q(last_name__icontains=search)
            )

        if is_active in ['true', 'false']:
            queryset = queryset.filter(is_active=(is_active == 'true'))

        results = [
            {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'is_active': user.is_active,
                'organization': user.organization.name if user.organization else '',
                'date_joined': user.date_joined,
                'roles': [user.system_role],
            }
            for user in queryset
        ]

        return Response(results, status=status.HTTP_200_OK)

    @transaction.atomic
    def post(self, request):
        if not self._check_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        payload = request.data.copy()
        payload.pop('organization', None)
        if payload.get('password') and not payload.get('password_confirm'):
            payload['password_confirm'] = payload.get('password')

        serializer = RegisterSerializer(data=payload)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        data.pop('password_confirm', None)
        organization_id = data.pop('organization_id', None)
        password = data.pop('password')
        user = User.objects.create_user(password=password, **data)

        if organization_id:
            try:
                from .auth_selectors import OrganizationSelectors
                org = OrganizationSelectors.get_by_id(organization_id)
                if org:
                    user.organization = org
                    user.save(update_fields=['organization'])
            except Exception:
                pass

        return Response(UserProfileSerializer(user).data, status=status.HTTP_201_CREATED)


class UserDetailManagementView(APIView):
    """Update user details from system-admin page."""
    permission_classes = [IsAuthenticated]

    def _check_admin(self, request):
        return request.user.is_staff or request.user.is_superuser

    @transaction.atomic
    def patch(self, request, user_id):
        if not self._check_admin(request):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)
        allowed_fields = ['first_name', 'last_name', 'email', 'username', 'phone', 'system_role']
        updated = []

        for field in allowed_fields:
            if field in request.data:
                setattr(user, field, request.data[field])
                updated.append(field)

        if 'is_active' in request.data:
            user.is_active = bool(request.data['is_active'])
            updated.append('is_active')

        if updated:
            user.save(update_fields=list(set(updated + ['updated_at'])))

        return Response(UserProfileSerializer(user).data, status=status.HTTP_200_OK)


class UserActivationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)
        user.is_active = True
        user.save(update_fields=['is_active', 'updated_at'])
        return Response({'message': 'User activated'}, status=status.HTTP_200_OK)


class UserDeactivationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, user_id):
        if not (request.user.is_staff or request.user.is_superuser):
            return Response({'detail': 'Forbidden'}, status=status.HTTP_403_FORBIDDEN)

        user = get_object_or_404(User, id=user_id)
        user.is_active = False
        user.save(update_fields=['is_active', 'updated_at'])
        return Response({'message': 'User deactivated'}, status=status.HTTP_200_OK)


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
