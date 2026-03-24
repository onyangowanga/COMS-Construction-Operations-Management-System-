#!/bin/bash

# Direct Local-to-VPS Deployment Script for COMS
# Bypasses GitHub Actions CI/CD
# Run this from your local machine

set -e  # Exit on error

echo "================================"
echo "COMS Direct VPS Deployment"
echo "Deploying from Local to VPS"
echo "================================"
echo ""

# Configuration
VPS_HOST="156.232.88.156"
VPS_USER="root"
VPS_PROJECT_DIR="/root/coms"
LOCAL_PROJECT_DIR="."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
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

print_step() {
    echo -e "${BLUE}[STEP]${NC} $1"
}

# Validate we're in the correct directory
if [ ! -f "manage.py" ] || [ ! -f "docker-compose.prod.yml" ]; then
    print_error "Not in COMS project directory. Please run from project root."
    exit 1
fi

# Test SSH connection
print_step "Testing SSH connection to VPS..."
if ! ssh -o ConnectTimeout=5 ${VPS_USER}@${VPS_HOST} "echo 'Connection successful'" > /dev/null 2>&1; then
    print_error "Cannot connect to VPS. Please check:"
    echo "  - VPS IP: ${VPS_HOST}"
    echo "  - Username: ${VPS_USER}"
    echo "  - SSH is configured correctly"
    echo ""
    echo "To setup SSH key authentication (recommended):"
    echo "  ssh-copy-id ${VPS_USER}@${VPS_HOST}"
    exit 1
fi
print_status "SSH connection successful!"

# Create temporary directory for deployment files
print_step "Preparing deployment files..."
TEMP_DIR=$(mktemp -d)
ARCHIVE_NAME="coms-deployment-$(date +%Y%m%d_%H%M%S).tar.gz"

print_status "Creating deployment archive..."

# Create list of files to exclude
cat > ${TEMP_DIR}/exclude.txt << 'EOF'
.git
.github
.env
.venv
__pycache__
*.pyc
*.pyo
*.pyd
.Python
*.so
*.egg
*.egg-info
dist
build
node_modules
.next
*.log
logs
.DS_Store
.idea
.vscode
*.swp
staticfiles
media
postgres_data
redis_data
EOF

# Create archive excluding unnecessary files
print_status "Archiving project files..."
tar -czf ${TEMP_DIR}/${ARCHIVE_NAME} \
    --exclude-from=${TEMP_DIR}/exclude.txt \
    -C ${LOCAL_PROJECT_DIR} .

ARCHIVE_SIZE=$(du -h ${TEMP_DIR}/${ARCHIVE_NAME} | cut -f1)
print_status "Archive created: ${ARCHIVE_NAME} (${ARCHIVE_SIZE})"

# Transfer archive to VPS
print_step "Transferring files to VPS..."
scp ${TEMP_DIR}/${ARCHIVE_NAME} ${VPS_USER}@${VPS_HOST}:/tmp/

# Execute deployment on VPS
print_step "Executing deployment on VPS..."
ssh ${VPS_USER}@${VPS_HOST} bash << EOF
set -e

echo "================================"
echo "VPS Deployment Execution"
echo "================================"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "\${GREEN}[VPS]${NC} \$1"
}

print_error() {
    echo -e "\${RED}[VPS ERROR]${NC} \$1"
}

# Navigate to project directory (create if doesn't exist)
if [ ! -d "${VPS_PROJECT_DIR}" ]; then
    print_status "Creating project directory..."
    mkdir -p ${VPS_PROJECT_DIR}
fi

cd ${VPS_PROJECT_DIR}

# Backup current deployment (if exists)
if [ -f "manage.py" ]; then
    print_status "Creating backup of current deployment..."
    BACKUP_DIR="/root/coms-backups/deployment-\$(date +%Y%m%d_%H%M%S)"
    mkdir -p \${BACKUP_DIR}

    # Backup database
    if docker ps --filter "name=coms_postgres_prod" --format "{{.Names}}" | grep -q coms_postgres_prod; then
        print_status "Backing up database..."
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > \${BACKUP_DIR}/database_backup.sql || true
    fi

    # Backup .env.production
    if [ -f ".env.production" ]; then
        cp .env.production \${BACKUP_DIR}/
    fi
fi

# Extract new deployment
print_status "Extracting new deployment files..."
tar -xzf /tmp/${ARCHIVE_NAME} -C ${VPS_PROJECT_DIR}

# Remove uploaded archive
rm /tmp/${ARCHIVE_NAME}

# Verify .env.production exists
if [ ! -f ".env.production" ]; then
    print_error ".env.production not found!"
    print_status "Restoring from backup..."
    if [ -f "\${BACKUP_DIR}/.env.production" ]; then
        cp \${BACKUP_DIR}/.env.production .env.production
    else
        print_error "No backup found. Please create .env.production manually."
        exit 1
    fi
fi

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
print_status "Running deployment script..."
./deploy.sh

print_status "Deployment completed!"
EOF

# Cleanup local temporary files
print_status "Cleaning up temporary files..."
rm -rf ${TEMP_DIR}

# Verify deployment
print_step "Verifying deployment..."
sleep 3

ssh ${VPS_USER}@${VPS_HOST} bash << 'EOF'
# Check containers
echo ""
echo "Container Status:"
docker ps --filter "name=coms" --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"

echo ""
echo "Health Check:"
HEALTH=$(curl -s -o /dev/null -w "%{http_code}" http://localhost/health/ 2>/dev/null || echo "000")
if [ "$HEALTH" = "200" ]; then
    echo "✅ Application is healthy!"
else
    echo "⚠️  Health check returned: $HEALTH"
fi
EOF

echo ""
echo "================================"
echo "✅ Deployment Complete!"
echo "================================"
echo ""
echo "Application URL: http://${VPS_HOST}"
echo ""
echo "To view logs:"
echo "  ssh ${VPS_USER}@${VPS_HOST}"
echo "  cd ${VPS_PROJECT_DIR}"
echo "  docker-compose -f docker-compose.prod.yml logs -f"
echo ""
