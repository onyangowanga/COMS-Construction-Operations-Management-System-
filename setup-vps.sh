#!/bin/bash

# COMS VPS Initial Setup Script
# This script sets up the VPS environment for the first time

set -e  # Exit on error

echo "================================"
echo "COMS VPS Initial Setup"
echo "================================"
echo ""

# Configuration
PROJECT_DIR="/root/coms"
REPO_URL="https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-.git"
BRANCH="main"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

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

# Update system packages
print_status "Updating system packages..."
apt-get update
apt-get upgrade -y

# Install essential tools
print_status "Installing essential tools..."
apt-get install -y \
    curl \
    wget \
    git \
    vim \
    htop \
    ufw \
    ca-certificates \
    gnupg \
    lsb-release

# Install Docker
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_status "Installing Docker..."
    
    # Add Docker's official GPG key
    mkdir -p /etc/apt/keyrings
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
    
    # Set up the repository
    echo \
      "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
      $(lsb_release -cs) stable" | tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker Engine
    apt-get update
    apt-get install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
    
    # Start and enable Docker
    systemctl start docker
    systemctl enable docker
    
    print_status "Docker installed successfully"
else
    print_status "Docker is already installed"
    docker --version
fi

# Install Docker Compose (standalone)
print_status "Checking Docker Compose installation..."
if ! command -v docker-compose &> /dev/null; then
    print_status "Installing Docker Compose..."
    curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    chmod +x /usr/local/bin/docker-compose
    print_status "Docker Compose installed successfully"
else
    print_status "Docker Compose is already installed"
    docker-compose --version
fi

# Configure firewall
print_status "Configuring firewall..."
ufw --force enable
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp    # SSH
ufw allow 80/tcp    # HTTP
ufw allow 443/tcp   # HTTPS
ufw reload

# Clone repository
print_status "Cloning repository..."
if [ -d "$PROJECT_DIR" ]; then
    print_warning "Project directory already exists. Backing up..."
    mv $PROJECT_DIR ${PROJECT_DIR}_backup_$(date +%Y%m%d_%H%M%S)
fi

git clone -b $BRANCH $REPO_URL $PROJECT_DIR
cd $PROJECT_DIR

# Create .env.production file
print_status "Creating .env.production file..."
if [ ! -f .env.production ]; then
    cp .env.production .env.production.example
    
    # Generate a random secret key
    SECRET_KEY=$(python3 -c 'from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())')
    
    # Update .env.production with generated secret key
    sed -i "s/your-secret-key-here-change-this/$SECRET_KEY/" .env.production
    
    print_warning "Please review and update .env.production with your actual credentials:"
    print_warning "  - Database passwords"
    print_warning "  - Email configuration"
    print_warning "  - Other sensitive settings"
    
    nano .env.production
else
    print_status ".env.production already exists"
fi

# Create directories for logs and SSL
print_status "Creating necessary directories..."
mkdir -p logs
mkdir -p nginx/ssl

# Set proper permissions
print_status "Setting permissions..."
chmod +x deploy.sh

# Build and start containers for the first time
print_status "Building and starting containers for the first time..."
docker-compose -f docker-compose.prod.yml build
docker-compose -f docker-compose.prod.yml up -d

# Wait for services to start
print_status "Waiting for services to start..."
sleep 15

# Run initial migrations
print_status "Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Create superuser
print_status "Creating superuser..."
print_warning "You will be prompted to create a superuser account."
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Collect static files
print_status "Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Setup GitHub webhook deploy key
print_status "Setting up SSH key for GitHub..."
if [ ! -f ~/.ssh/id_rsa ]; then
    ssh-keygen -t rsa -b 4096 -C "coms-deployment@vps" -N "" -f ~/.ssh/id_rsa
    print_status "SSH key generated. Add this public key to your GitHub repository:"
    cat ~/.ssh/id_rsa.pub
    print_warning "Press Enter after adding the key to GitHub..."
    read
fi

# Setup cron job for automatic deployment (optional)
print_status "Setting up deployment webhook listener..."
cat > /usr/local/bin/deploy-coms << 'EOF'
#!/bin/bash
cd /root/coms
./deploy.sh >> /var/log/coms-deploy.log 2>&1
EOF

chmod +x /usr/local/bin/deploy-coms

# Test deployment
print_status "Testing application..."
sleep 5
HEALTH_CHECK=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ || echo "000")

if [ "$HEALTH_CHECK" = "200" ]; then
    print_status "Application is running successfully!"
else
    print_error "Health check failed. Please check the logs:"
    docker-compose -f docker-compose.prod.yml logs web
fi

echo ""
echo "================================"
echo "Setup completed successfully!"
echo "================================"
echo ""
echo "Your COMS application is now running at:"
echo "  http://156.232.88.156"
echo ""
echo "Next steps:"
echo "  1. Configure SSL certificate for HTTPS"
echo "  2. Set up GitHub Actions for auto-deployment"
echo "  3. Configure email settings in .env.production"
echo "  4. Set up regular backups"
echo ""
echo "Useful commands:"
echo "  Deploy updates:        cd $PROJECT_DIR && ./deploy.sh"
echo "  View logs:             cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml logs -f"
echo "  Restart containers:    cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml restart"
echo "  Stop containers:       cd $PROJECT_DIR && docker-compose -f docker-compose.prod.yml down"
echo ""
