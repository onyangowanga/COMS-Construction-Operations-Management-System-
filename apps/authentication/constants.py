"""
Authentication Constants
Centralized configuration values to avoid magic numbers throughout the codebase.
"""

# Account Security
MAX_LOGIN_ATTEMPTS = 5
ACCOUNT_LOCK_MINUTES = 30
PASSWORD_RESET_TOKEN_HOURS = 24
EMAIL_VERIFICATION_TOKEN_HOURS = 48

# JWT Configuration
JWT_ACCESS_MINUTES = 15
JWT_REFRESH_DAYS = 7
JWT_ALGORITHM = 'HS256'

# Password Requirements
PASSWORD_MIN_LENGTH = 8
PASSWORD_MAX_LENGTH = 128
PASSWORD_REQUIRE_UPPERCASE = True
PASSWORD_REQUIRE_LOWERCASE = True
PASSWORD_REQUIRE_DIGIT = True
PASSWORD_REQUIRE_SPECIAL_CHAR = True

# File Upload Limits
PROFILE_PICTURE_MAX_SIZE_MB = 5
PROFILE_PICTURE_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'gif', 'webp']
ORGANIZATION_LOGO_MAX_SIZE_MB = 10
ORGANIZATION_LOGO_ALLOWED_EXTENSIONS = ['jpg', 'jpeg', 'png', 'svg', 'webp']

# Phone Number Validation
PHONE_MIN_LENGTH = 9
PHONE_MAX_LENGTH = 15
PHONE_REGEX_PATTERN = r'^\+?1?\d{9,15}$'

# Username Validation
USERNAME_MIN_LENGTH = 3
USERNAME_MAX_LENGTH = 150
USERNAME_REGEX_PATTERN = r'^[a-zA-Z0-9_.-]+$'

# Email Validation
EMAIL_MAX_LENGTH = 254

# Audit Log Retention
AUDIT_LOG_RETENTION_DAYS = 365
AUDIT_LOG_BATCH_SIZE = 1000

# Session Configuration
SESSION_TIMEOUT_MINUTES = 30
REMEMBER_ME_DAYS = 30

# Rate Limiting
LOGIN_RATE_LIMIT_ATTEMPTS = 10
LOGIN_RATE_LIMIT_PERIOD_MINUTES = 15
API_RATE_LIMIT_PER_MINUTE = 60
API_RATE_LIMIT_PER_HOUR = 1000

# Organization Limits
MAX_USERS_PER_ORGANIZATION = 1000
MAX_PROJECTS_PER_USER = 100

# Verification & Activation
REQUIRE_EMAIL_VERIFICATION = True  # Re-enabled for security with SMTP configured
AUTO_ACTIVATE_USERS = False

# Password Reset
PASSWORD_RESET_TIMEOUT_DAYS = 3
PASSWORD_RESET_MAX_ATTEMPTS = 3

# Two-Factor Authentication (for future implementation)
ENABLE_2FA = False
OTP_VALIDITY_MINUTES = 5
OTP_LENGTH = 6

# Pagination Defaults
DEFAULT_PAGE_SIZE = 20
MAX_PAGE_SIZE = 100

# User Agent Truncation for Logging
USER_AGENT_MAX_DISPLAY_LENGTH = 100

# Security Headers
REQUIRE_HTTPS = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# Django Axes Configuration (Login Attack Detection)
AXES_FAILURE_LIMIT = 5
AXES_COOLOFF_TIME = 30  # minutes
AXES_LOCKOUT_PARAMETERS = ['username', 'ip_address']

# Account Status Messages
ACCOUNT_LOCKED_MESSAGE = "Your account is temporarily locked due to multiple failed login attempts. Please try again after {minutes} minutes or contact support."
ACCOUNT_INACTIVE_MESSAGE = "Your account has been deactivated. Please contact support for assistance."
EMAIL_NOT_VERIFIED_MESSAGE = "Please verify your email address before logging in."

# System Roles (for reference - actual enums in models.py)
SYSTEM_ROLE_SUPER_ADMIN = 'super_admin'
SYSTEM_ROLE_CONTRACTOR = 'contractor'
SYSTEM_ROLE_SITE_MANAGER = 'site_manager'
SYSTEM_ROLE_QS = 'qs'
SYSTEM_ROLE_ARCHITECT = 'architect'
SYSTEM_ROLE_CLIENT = 'client'
SYSTEM_ROLE_STAFF = 'staff'

# Project Roles (for reference - actual enums in models.py)
PROJECT_ROLE_OWNER = 'owner'
PROJECT_ROLE_MANAGER = 'manager'
PROJECT_ROLE_SITE_MANAGER = 'site_manager'
PROJECT_ROLE_QS = 'qs'
PROJECT_ROLE_ARCHITECT = 'architect'
PROJECT_ROLE_FOREMAN = 'foreman'
PROJECT_ROLE_ENGINEER = 'engineer'
PROJECT_ROLE_SUPERVISOR = 'supervisor'
PROJECT_ROLE_VIEWER = 'viewer'
