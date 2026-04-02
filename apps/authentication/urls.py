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
    UIPreferencesView,
    OrganizationSettingsView,
    UserManagementView,
    UserDetailManagementView,
    UserActivationView,
    UserDeactivationView,
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
    path('profile/', UserProfileView.as_view(), name='user-profile-alias'),
    path('ui-preferences/', UIPreferencesView.as_view(), name='ui-preferences'),
    path('organization-settings/', OrganizationSettingsView.as_view(), name='organization-settings'),
    path('users/', UserManagementView.as_view(), name='users-list-create'),
    path('users/<uuid:user_id>/', UserDetailManagementView.as_view(), name='users-update'),
    path('users/<uuid:user_id>/activate/', UserActivationView.as_view(), name='users-activate'),
    path('users/<uuid:user_id>/deactivate/', UserDeactivationView.as_view(), name='users-deactivate'),
    
    # Password management
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    path('password-reset/', PasswordResetRequestView.as_view(), name='password-reset'),
]
