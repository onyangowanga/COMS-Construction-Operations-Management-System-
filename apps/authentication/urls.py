"""
Authentication URLs
URL routing for authentication endpoints.
"""
from django.urls import path
from .views import (
    LoginView,
    LogoutView,
    RegisterView,
    TokenRefreshView,
    UserProfileView,
    ChangePasswordView,
    PasswordResetRequestView,
)

app_name = 'authentication'

urlpatterns = [
    # Authentication
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    
    # Token management
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
    
    # User profile
    path('me/', UserProfileView.as_view(), name='user-profile'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
]
