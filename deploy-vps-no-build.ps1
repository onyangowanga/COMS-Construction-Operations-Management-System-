# COMS VPS Deployment (No Build on VPS)
# This version syncs files only and uses existing images or builds locally

param(
    [switch]$BuildLocally = $false
)

$ErrorActionPreference = "Stop"

# Configuration
$VPS_HOST = "156.232.88.156"
$VPS_USER = "root"
$VPS_PROJECT_DIR = "/root/coms"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[STEP] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message
}

function Write-Success {
    param([string]$Message)
    Write-Host "  [OK] " -ForegroundColor Green -NoNewline
    Write-Host $Message
}

function Write-ErrorMsg {
    param([string]$Message)
    Write-Host "  [ERROR] " -ForegroundColor Red -NoNewline
    Write-Host $Message
}

function Write-Info {
    param([string]$Message)
    Write-Host "  [INFO] " -ForegroundColor Blue -NoNewline
    Write-Host $Message
}

Write-Host ""
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host "   COMS VPS Deployment (No Build on VPS)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Test SSH connection
Write-Step "Testing SSH connection to VPS..."
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "echo 'Connection successful'" 2>$null
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Cannot connect to VPS"
    exit 1
}
Write-Success "SSH connection successful"

# Sync files using rsync-like approach (just copy essential files)
Write-Step "Syncing application files to VPS..."

$filesToSync = @(
    "apps/",
    "api/",
    "config/",
    "frontend/",
    "nginx/",
    "manage.py",
    "requirements.txt",
    "docker-compose.prod.yml",
    "Dockerfile.prod",
    "deploy.sh"
)

Write-Info "Creating sync script..."
$syncScript = @"
cd $VPS_PROJECT_DIR

# Create backup
if [ -f manage.py ]; then
    echo 'Creating backup...'
    BACKUP_DIR="/root/coms-backups/backup-`$(date +%Y%m%d_%H%M%S)"
    mkdir -p `$BACKUP_DIR

    # Backup database if running
    if docker ps --filter 'name=coms_postgres_prod' | grep -q coms_postgres_prod; then
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > `$BACKUP_DIR/backup.sql 2>/dev/null || true
    fi

    # Backup .env.production
    if [ -f .env.production ]; then
        cp .env.production `$BACKUP_DIR/
    fi
fi

# Check .env.production exists
if [ ! -f .env.production ]; then
    echo 'ERROR: .env.production not found!'
    exit 1
fi

echo 'Stopping containers...'
docker-compose -f docker-compose.prod.yml down

echo 'Cleaning up old images...'
docker image prune -af

echo 'Starting services (using existing/base images)...'
docker-compose -f docker-compose.prod.yml up -d --no-build

echo 'Waiting for services...'
sleep 15

echo 'Running migrations...'
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

echo 'Collecting static files...'
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo 'Deployment complete!'
docker-compose -f docker-compose.prod.yml ps
"@

# Create tar of files
Write-Info "Creating archive..."
$tempDir = Join-Path $env:TEMP "coms-sync-$(Get-Date -Format 'yyyyMMddHHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

# Create tar archive
tar -czf "$tempDir/coms-sync.tar.gz" `
    --exclude=".git" `
    --exclude=".github" `
    --exclude=".env" `
    --exclude=".venv" `
    --exclude="__pycache__" `
    --exclude="*.pyc" `
    --exclude="node_modules" `
    --exclude=".next" `
    --exclude="staticfiles" `
    --exclude="media" `
    apps/ api/ config/ frontend/ nginx/ manage.py requirements.txt docker-compose.prod.yml Dockerfile.prod deploy.sh 2>$null

if (Test-Path "$tempDir/coms-sync.tar.gz") {
    Write-Success "Archive created"

    # Upload
    Write-Step "Uploading to VPS..."
    scp -o StrictHostKeyChecking=no "$tempDir/coms-sync.tar.gz" "${VPS_USER}@${VPS_HOST}:/tmp/"

    if ($LASTEXITCODE -eq 0) {
        Write-Success "Upload complete"
    } else {
        Write-ErrorMsg "Upload failed"
        exit 1
    }
} else {
    Write-ErrorMsg "Failed to create archive"
    exit 1
}

# Extract and deploy on VPS
Write-Step "Deploying on VPS..."

$deployScript = @"
cd $VPS_PROJECT_DIR

echo 'Extracting files...'
tar -xzf /tmp/coms-sync.tar.gz -C $VPS_PROJECT_DIR

rm /tmp/coms-sync.tar.gz

$syncScript
"@

ssh -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "$deployScript"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application URL: http://$VPS_HOST"
    Write-Host ""
    Write-Host "To view logs:"
    Write-Host "  ssh ${VPS_USER}@${VPS_HOST}"
    Write-Host "  cd $VPS_PROJECT_DIR"
    Write-Host "  docker-compose -f docker-compose.prod.yml logs -f"
    Write-Host ""
} else {
    Write-ErrorMsg "Deployment failed"
    exit 1
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force
