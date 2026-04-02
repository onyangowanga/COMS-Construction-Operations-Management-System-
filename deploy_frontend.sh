#!/bin/bash

# COMS Frontend-Only Deployment Script for VPS
set -e

echo "================================"
echo "COMS Frontend Deployment"
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

# Stop frontend containers only
print_status "Stopping frontend containers..."
docker-compose -f docker-compose.prod.yml stop frontend
docker-compose -f docker-compose.prod.yml rm -f frontend

# Build frontend image
print_status "Building frontend Docker image..."
docker-compose -f docker-compose.prod.yml build --no-cache frontend

# Start frontend container
print_status "Starting frontend container..."
docker-compose -f docker-compose.prod.yml up -d frontend

# Wait for frontend to be ready
print_status "Waiting for frontend to start..."
sleep 15

# Check frontend status
print_status "Checking frontend container status..."
docker-compose -f docker-compose.prod.yml ps frontend

# Test frontend health (via nginx if it's running, or direct port 3000)
print_status "Testing frontend..."
sleep 5

# Try to check if frontend is responding
FRONTEND_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:3000/ 2>/dev/null || echo "000")

if [ "$FRONTEND_CHECK" = "200" ] || [ "$FRONTEND_CHECK" = "304" ]; then
    print_status "Frontend is responding on port 3000"
else
    print_warning "Frontend health check returned: $FRONTEND_CHECK"
    print_warning "Check logs with: docker-compose -f docker-compose.prod.yml logs frontend"
fi

# Restart nginx to pick up any changes
if docker-compose -f docker-compose.prod.yml ps nginx | grep -q "Up"; then
    print_status "Restarting nginx to apply changes..."
    docker-compose -f docker-compose.prod.yml restart nginx
    sleep 3
fi

echo ""
echo "================================"
echo "Frontend Deployment Complete!"
echo "================================"
echo ""
echo "Frontend (via nginx): http://localhost/"
echo "Frontend (direct):    http://localhost:3000/"
echo ""
echo "View logs: docker-compose -f docker-compose.prod.yml logs -f frontend"
echo ""
