#!/bin/bash

# COMS Backend-Only Deployment Script for VPS
set -e

echo "================================"
echo "COMS Backend Deployment"
echo "================================"
echo ""

# Configuration
PROJECT_DIR="/root/coms"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Navigate to project directory
cd $PROJECT_DIR || exit 1

# Load environment variables
if [ ! -f .env.production ]; then
    print_warning ".env.production not found. Skipping env load."
else
    print_status "Loading environment variables..."
    if command -v dos2unix &> /dev/null; then
        dos2unix .env.production 2>/dev/null || true
    else
        sed -i 's/\r$//' .env.production 2>/dev/null || true
    fi
    set -a
    source .env.production
    set +a
fi

# Stop backend containers only
print_status "Stopping backend containers..."
docker-compose -f docker-compose.prod.yml stop web
docker-compose -f docker-compose.prod.yml rm -f web

# Build backend image
print_status "Building backend Docker image..."
docker-compose -f docker-compose.prod.yml build --no-cache web

# Start backend container
print_status "Starting backend container..."
docker-compose -f docker-compose.prod.yml up -d web

# Wait for backend to be ready
print_status "Waiting for backend to start..."
sleep 10

# Wait for database to be ready
print_status "Waiting for database to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U coms_user 2>/dev/null; then
        print_status "Database is ready!"
        break
    fi
    echo -n "."
    sleep 2
done
echo ""

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Check backend status
print_status "Checking backend container status..."
docker-compose -f docker-compose.prod.yml ps web

# Test backend health
print_status "Testing backend health..."
sleep 5
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/health/ 2>/dev/null || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    print_status "Backend deployment successful!"
else
    print_warning "Backend health check returned: $HEALTH_CHECK"
    print_warning "Check logs with: docker-compose -f docker-compose.prod.yml logs web"
fi

echo ""
echo "================================"
echo "Backend Deployment Complete!"
echo "================================"
echo ""
echo "Backend API: http://localhost:8000/api"
echo "Admin Panel: http://localhost:8000/admin"
echo ""
echo "View logs: docker-compose -f docker-compose.prod.yml logs -f web"
echo ""
