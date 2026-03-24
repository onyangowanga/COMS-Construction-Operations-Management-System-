# Direct Local-to-VPS Deployment Script for COMS (PowerShell)
# Bypasses GitHub Actions CI/CD
# Run this from your local Windows machine

param(
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$VPS_HOST = "156.232.88.156"
$VPS_USER = "root"
$VPS_PROJECT_DIR = "/root/coms"
$LOCAL_PROJECT_DIR = Get-Location

# Colors
function Write-Status {
    param([string]$Message)
    Write-Host "[INFO] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "[ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-WarningMsg {
    param([string]$Message)
    Write-Host "[WARNING] " -ForegroundColor Yellow -NoNewline
    Write-Host $Message
}

function Write-StepMsg {
    param([string]$Message)
    Write-Host "[STEP] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

Write-Host ""
Write-Host "================================" -ForegroundColor Cyan
Write-Host "COMS Direct VPS Deployment" -ForegroundColor Cyan
Write-Host "Deploying from Local to VPS" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""

# Check if we're in the correct directory
if (-not (Test-Path "manage.py") -or -not (Test-Path "docker-compose.prod.yml")) {
    Write-ErrorMsg "Not in COMS project directory. Please run from project root."
    exit 1
}

# Check if SSH is available
$sshAvailable = Get-Command ssh -ErrorAction SilentlyContinue
if (-not $sshAvailable) {
    Write-ErrorMsg "SSH client not found. Please install OpenSSH client."
    Write-Host "  Install via: Settings > Apps > Optional Features > OpenSSH Client"
    exit 1
}

# Check if SCP is available
$scpAvailable = Get-Command scp -ErrorAction SilentlyContinue
if (-not $scpAvailable) {
    Write-ErrorMsg "SCP not found. OpenSSH client may not be properly installed."
    exit 1
}

# Test SSH connection
Write-StepMsg "Testing SSH connection to VPS..."
$sshTest = ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "echo 'Connection successful'" 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Cannot connect to VPS. Please check:"
    Write-Host "  - VPS IP: $VPS_HOST"
    Write-Host "  - Username: $VPS_USER"
    Write-Host "  - SSH is configured correctly"
    Write-Host ""
    Write-Host "To setup SSH key authentication (recommended):"
    Write-Host "  ssh-keygen -t ed25519"
    Write-Host "  type `$env:USERPROFILE\.ssh\id_ed25519.pub | ssh ${VPS_USER}@${VPS_HOST} 'cat >> ~/.ssh/authorized_keys'"
    exit 1
}
Write-Status "SSH connection successful!"

# Create temporary directory
Write-StepMsg "Preparing deployment files..."
$TEMP_DIR = Join-Path $env:TEMP "coms-deploy-$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $TEMP_DIR -Force | Out-Null

$ARCHIVE_NAME = "coms-deployment-$(Get-Date -Format 'yyyyMMdd_HHmmss').zip"
$ARCHIVE_PATH = Join-Path $TEMP_DIR $ARCHIVE_NAME

# Create list of exclusions
$excludePatterns = @(
    ".git",
    ".github",
    ".env",
    ".venv",
    "__pycache__",
    "*.pyc",
    "*.pyo",
    "*.pyd",
    ".Python",
    "*.so",
    "*.egg",
    "*.egg-info",
    "dist",
    "build",
    "node_modules",
    ".next",
    "*.log",
    "logs",
    ".DS_Store",
    ".idea",
    ".vscode",
    "*.swp",
    "staticfiles",
    "media",
    "postgres_data",
    "redis_data"
)

# Create archive
Write-Status "Creating deployment archive..."
try {
    # Get all files except excluded ones
    $files = Get-ChildItem -Path $LOCAL_PROJECT_DIR -Recurse -File | Where-Object {
        $file = $_
        $shouldExclude = $false
        foreach ($pattern in $excludePatterns) {
            if ($file.FullName -like "*$pattern*" -or $file.Name -like $pattern) {
                $shouldExclude = $true
                break
            }
        }
        -not $shouldExclude
    }

    # Create zip archive
    Compress-Archive -Path $files.FullName -DestinationPath $ARCHIVE_PATH -CompressionLevel Optimal -Force

    $archiveSize = (Get-Item $ARCHIVE_PATH).Length / 1MB
    Write-Status "Archive created: $ARCHIVE_NAME ($([math]::Round($archiveSize, 2)) MB)"
} catch {
    Write-ErrorMsg "Failed to create archive: $_"
    exit 1
}

# Transfer archive to VPS
Write-StepMsg "Transferring files to VPS..."
Write-Status "Uploading archive (this may take a few minutes)..."
scp -o StrictHostKeyChecking=no $ARCHIVE_PATH "${VPS_USER}@${VPS_HOST}:/tmp/"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to transfer files to VPS"
    exit 1
}
Write-Status "Transfer complete!"

# Execute deployment on VPS
Write-StepMsg "Executing deployment on VPS..."

$deploymentScript = @"
set -e

echo '================================'
echo 'VPS Deployment Execution'
echo '================================'

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "\${GREEN}[VPS]\${NC} \$1"
}

print_error() {
    echo -e "\${RED}[VPS ERROR]\${NC} \$1"
}

# Navigate to project directory (create if doesn't exist)
if [ ! -d '$VPS_PROJECT_DIR' ]; then
    print_status 'Creating project directory...'
    mkdir -p $VPS_PROJECT_DIR
fi

cd $VPS_PROJECT_DIR

# Backup current deployment (if exists)
if [ -f 'manage.py' ]; then
    print_status 'Creating backup of current deployment...'
    BACKUP_DIR="/root/coms-backups/deployment-`$(date +%Y%m%d_%H%M%S)"
    mkdir -p `$BACKUP_DIR

    # Backup database
    if docker ps --filter 'name=coms_postgres_prod' --format '{{.Names}}' | grep -q coms_postgres_prod; then
        print_status 'Backing up database...'
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > `$BACKUP_DIR/database_backup.sql || true
    fi

    # Backup .env.production
    if [ -f '.env.production' ]; then
        cp .env.production `$BACKUP_DIR/
    fi
fi

# Extract new deployment
print_status 'Extracting new deployment files...'

# Install unzip if not available
if ! command -v unzip &> /dev/null; then
    apt-get update && apt-get install -y unzip
fi

unzip -o /tmp/$ARCHIVE_NAME -d $VPS_PROJECT_DIR

# Remove uploaded archive
rm /tmp/$ARCHIVE_NAME

# Verify .env.production exists
if [ ! -f '.env.production' ]; then
    print_error '.env.production not found!'
    if [ -n "`$BACKUP_DIR" ] && [ -f "`$BACKUP_DIR/.env.production" ]; then
        print_status 'Restoring .env.production from backup...'
        cp `$BACKUP_DIR/.env.production .env.production
    else
        print_error 'No backup found. Please create .env.production manually.'
        exit 1
    fi
fi

# Make deploy script executable
chmod +x deploy.sh

# Run deployment
print_status 'Running deployment script...'
./deploy.sh

print_status 'Deployment completed!'
"@

ssh -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" $deploymentScript

if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Deployment failed on VPS"
    exit 1
}

# Cleanup local temporary files
Write-Status "Cleaning up temporary files..."
Remove-Item -Path $TEMP_DIR -Recurse -Force

# Verify deployment
Write-StepMsg "Verifying deployment..."
Start-Sleep -Seconds 3

$verificationScript = @"
echo ''
echo 'Container Status:'
docker ps --filter 'name=coms' --format 'table {{.Names}}\t{{.Status}}\t{{.Ports}}'

echo ''
echo 'Health Check:'
HEALTH=`$(curl -s -o /dev/null -w '%{http_code}' http://localhost/health/ 2>/dev/null)
if [ -z "`$HEALTH" ]; then
    HEALTH='000'
fi
if [ "`$HEALTH" = '200' ]; then
    echo 'Application is healthy!'
else
    echo 'Health check returned: '`$HEALTH
fi
"@

ssh -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" $verificationScript

Write-Host ""
Write-Host "================================" -ForegroundColor Green
Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
Write-Host "================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application URL: http://$VPS_HOST"
Write-Host ""
Write-Host "To view logs:"
Write-Host "  ssh ${VPS_USER}@${VPS_HOST}"
Write-Host "  cd $VPS_PROJECT_DIR"
Write-Host "  docker-compose -f docker-compose.prod.yml logs -f"
Write-Host ""
