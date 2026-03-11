#!/bin/bash
# Quick VPS Setup Script
# Creates .env.production file with required environment variables

set -e

echo "================================"
echo "COMS VPS Quick Setup"
echo "================================"

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root (use sudo)"
    exit 1
fi

# Navigate to project directory
cd /root/coms || {
    echo "Error: /root/coms directory not found"
    exit 1
}

# Check if .env.production already exists
if [ -f .env.production ]; then
    echo ".env.production already exists. Backing up to .env.production.backup"
    cp .env.production .env.production.backup
fi

# Generate random secret key
SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')

# Create .env.production file
cat > .env.production << EOF
# COMS Production Environment Configuration
# Generated on $(date)

# Django Settings
SECRET_KEY=${SECRET_KEY}
DEBUG=False
ALLOWED_HOSTS=*
DJANGO_SETTINGS_MODULE=config.settings

# Database Configuration
POSTGRES_DB=coms_production
POSTGRES_USER=coms_user
POSTGRES_PASSWORD=coms_secure_password_$(openssl rand -hex 16)
DATABASE_URL=postgresql://coms_user:coms_secure_password_$(openssl rand -hex 16)@db:5432/coms_production

# Redis Configuration
REDIS_URL=redis://redis:6379/0
CELERY_BROKER_URL=redis://redis:6379/0
CELERY_RESULT_BACKEND=redis://redis:6379/0

# Email Configuration (configure later as needed)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-password
DEFAULT_FROM_EMAIL=COMS System <noreply@example.com>

# Security
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# CORS Settings
CORS_ALLOWED_ORIGINS=http://localhost,http://127.0.0.1
CORS_ALLOW_CREDENTIALS=True

# Logging
LOG_LEVEL=INFO

# Celery Configuration
CELERY_TIMEZONE=UTC
CELERY_TASK_TRACK_STARTED=True
CELERY_TASK_TIME_LIMIT=300

# Report Generation
REPORT_CACHE_DURATION=600
EOF

# Fix password consistency (ensure DB password matches in DATABASE_URL)
DB_PASSWORD=$(grep "POSTGRES_PASSWORD=" .env.production | cut -d= -f2)
sed -i "s|DATABASE_URL=.*|DATABASE_URL=postgresql://coms_user:${DB_PASSWORD}@db:5432/coms_production|" .env.production

echo ""
echo "✅ .env.production created successfully!"
echo ""
echo "IMPORTANT: Review and update the following in .env.production:"
echo "  - ALLOWED_HOSTS (add your domain/IP)"
echo "  - EMAIL_* settings (if using email)"
echo "  - SECURE_SSL_REDIRECT=True (when using HTTPS)"
echo "  - CORS_ALLOWED_ORIGINS (add your frontend URLs)"
echo ""
echo "To edit: nano .env.production"
echo ""
