#!/bin/bash

# COMS Deployment Script for VPS
# This script handles the deployment process on the VPS

set -e  # Exit on error

echo "================================"
echo "COMS Deployment Script"
echo "================================"
echo ""

# Configuration
PROJECT_DIR="/root/coms"
REPO_URL="https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-.git"
BRANCH="master"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored output
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
print_status "Navigating to project directory..."
cd $PROJECT_DIR || {
    print_error "Project directory not found. Please run setup script first."
    exit 1
}

# Pull latest changes from GitHub
print_status "Pulling latest changes from GitHub..."
git fetch origin
git reset --hard origin/$BRANCH
git pull origin $BRANCH

# Check if .env.production exists
if [ ! -f .env.production ]; then
    print_warning ".env.production not found. Please create it before continuing."
    exit 1
fi

# Stop existing containers
print_status "Stopping existing containers..."
docker-compose -f docker-compose.prod.yml down || true

# Remove old images (optional, comment out to keep)
print_status "Removing old images..."
docker image prune -f

# Build new images
print_status "Building Docker images..."
docker-compose -f docker-compose.prod.yml build --no-cache

# Start containers
print_status "Starting containers..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to be healthy
print_status "Waiting for services to start..."
sleep 10

# Run database migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Create superuser if needed (optional)
# docker-compose -f docker-compose.prod.yml exec -T web python manage.py createsuperuser --noinput || true

# Check container status
print_status "Checking container status..."
docker-compose -f docker-compose.prod.yml ps

# Test application health
print_status "Testing application health..."
sleep 5
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    print_status "Deployment successful! Application is healthy."
else
    print_error "Health check failed. Status code: $HEALTH_CHECK"
    print_status "Checking logs..."
    docker-compose -f docker-compose.prod.yml logs --tail=50 web
    exit 1
fi

# Show running containers
print_status "Running containers:"
docker ps --filter "name=coms"

echo ""
echo "================================"
echo "Deployment completed successfully!"
echo "================================"
echo ""
echo "Access your application at:"
echo "  http://156.232.88.156"
echo ""
echo "To view logs, run:"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
