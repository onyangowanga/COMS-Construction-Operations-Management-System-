#!/bin/bash

# COMS VPS One-Time Setup Script
# Run this once on your VPS to prepare it for deployments

set -e

echo "========================================"
echo "COMS VPS Setup"
echo "========================================"
echo ""

# Colors
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [ "$EUID" -ne 0 ]; then
    print_error "Please run as root"
    exit 1
fi

# Update system packages
print_status "Updating system packages..."
apt-get update

# Install required packages
print_status "Installing required packages..."
apt-get install -y \
    git \
    curl \
    wget \
    unzip \
    dos2unix \
    docker.io \
    docker-compose

# Enable and start Docker
print_status "Enabling Docker service..."
systemctl enable docker
systemctl start docker

# Check Docker installation
print_status "Verifying Docker installation..."
docker --version
docker-compose --version

# Create project directory if it doesn't exist
PROJECT_DIR="/root/coms"
if [ ! -d "$PROJECT_DIR" ]; then
    print_status "Creating project directory..."
    mkdir -p $PROJECT_DIR
fi

# Configure firewall (if UFW is installed)
if command -v ufw &> /dev/null; then
    print_status "Configuring firewall..."
    ufw allow 22/tcp    # SSH
    ufw allow 80/tcp    # HTTP
    ufw allow 443/tcp   # HTTPS (for future SSL setup)
    print_warning "Firewall rules added. Enable with: ufw enable"
fi

print_status ""
print_status "VPS setup completed successfully!"
print_status ""
print_status "Next steps:"
print_status "1. Clone or deploy your COMS project to $PROJECT_DIR"
print_status "2. Create .env.production file in $PROJECT_DIR"
print_status "3. Run deployment: cd $PROJECT_DIR && ./deploy.sh"
print_status ""
