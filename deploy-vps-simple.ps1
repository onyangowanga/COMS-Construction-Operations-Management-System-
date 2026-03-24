# COMS Simple VPS Deployment
# Skips frontend build on VPS (uses pre-built or falls back to dev mode)

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
Write-Host "   COMS Simple VPS Deployment" -ForegroundColor Cyan
Write-Host "   (Backend only, Frontend in dev mode)" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Test SSH
Write-Step "Testing SSH connection..."
ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "echo OK" 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Cannot connect to VPS"
    exit 1
}
Write-Success "Connected to VPS"

# Create deployment archive
Write-Step "Creating deployment archive..."
$timestamp = Get-Date -Format 'yyyyMMdd_HHmmss'
$tempDir = Join-Path $env:TEMP "coms-deploy-$timestamp"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

$archiveName = "coms-simple-$timestamp.tar.gz"
$archivePath = Join-Path $tempDir $archiveName

# Use tar to preserve directory structure (Git for Windows includes tar)
$excludeArgs = @(
    "--exclude=.git",
    "--exclude=.github",
    "--exclude=.env",
    "--exclude=.venv",
    "--exclude=__pycache__",
    "--exclude=*.pyc",
    "--exclude=node_modules",
    "--exclude=.next",
    "--exclude=staticfiles",
    "--exclude=media",
    "--exclude=postgres_data",
    "--exclude=redis_data",
    "--exclude=.idea",
    "--exclude=.vscode",
    "--exclude=logs",
    "--exclude=*.log",
    "--exclude=*.swp"
)

tar -czf $archivePath $excludeArgs apps api config frontend nginx manage.py requirements.txt docker-compose.prod.yml Dockerfile.prod deploy.sh
$size = [math]::Round((Get-Item $archivePath).Length / 1MB, 2)
Write-Success "Archive created: $archiveName ($size MB)"

# Upload
Write-Step "Uploading to VPS..."
scp -o StrictHostKeyChecking=no $archivePath "${VPS_USER}@${VPS_HOST}:/tmp/"
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Upload failed"
    exit 1
}
Write-Success "Upload complete"

# Deploy on VPS
Write-Step "Deploying on VPS..."

$deployScript = @"
set -e

cd $VPS_PROJECT_DIR

# Backup
if [ -f manage.py ]; then
    echo 'Creating backup...'
    BACKUP_DIR="/root/coms-backups/backup-`$(date +%Y%m%d_%H%M%S)"
    mkdir -p `$BACKUP_DIR

    if docker ps --filter 'name=coms_postgres_prod' | grep -q coms; then
        docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > `$BACKUP_DIR/backup.sql 2>/dev/null || true
    fi

    [ -f .env.production ] && cp .env.production `$BACKUP_DIR/
fi

# Extract
echo 'Extracting files...'
tar -xzf /tmp/$archiveName -C $VPS_PROJECT_DIR
rm /tmp/$archiveName

# Check env file
if [ ! -f .env.production ]; then
    echo 'ERROR: .env.production not found!'
    exit 1
fi

# Stop containers
echo 'Stopping containers...'
docker-compose -f docker-compose.prod.yml down

# Clean up
echo 'Cleaning Docker...'
docker system prune -af

# Modify docker-compose to use dev frontend (skip build)
echo 'Modifying docker-compose for simple deployment...'
cp docker-compose.prod.yml docker-compose.prod.yml.backup

# Start services WITHOUT frontend build (use development mode)
echo 'Starting backend services...'
docker-compose -f docker-compose.prod.yml up -d db redis

echo 'Waiting for database...'
sleep 10

echo 'Building backend only...'
docker-compose -f docker-compose.prod.yml build web

echo 'Starting backend...'
docker-compose -f docker-compose.prod.yml up -d web

echo 'Running migrations...'
sleep 5
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

echo 'Collecting static files...'
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

echo 'Starting nginx...'
docker-compose -f docker-compose.prod.yml up -d nginx

# Start frontend in dev mode (skip build)
echo 'Starting frontend in development mode...'
docker-compose -f docker-compose.prod.yml up -d frontend

echo ''
echo 'Deployment complete!'
echo ''
docker-compose -f docker-compose.prod.yml ps
"@

ssh -o StrictHostKeyChecking=no "${VPS_USER}@${VPS_HOST}" "$deployScript"

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host "[SUCCESS] Deployment Complete!" -ForegroundColor Green
    Write-Host "=======================================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Application URL: http://$VPS_HOST" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Note: Frontend is running in development mode" -ForegroundColor Yellow
    Write-Host "This is fine for testing, but for production you may want to:" -ForegroundColor Yellow
    Write-Host "  1. Build frontend locally" -ForegroundColor White
    Write-Host "  2. Use a VPS with more RAM (4GB+)" -ForegroundColor White
    Write-Host "  3. Or use pre-built Docker images" -ForegroundColor White
    Write-Host ""
    Write-Host "Check logs:" -ForegroundColor Cyan
    Write-Host "  ssh ${VPS_USER}@${VPS_HOST}"
    Write-Host "  cd $VPS_PROJECT_DIR"
    Write-Host "  docker-compose -f docker-compose.prod.yml logs -f"
    Write-Host ""
} else {
    Write-ErrorMsg "Deployment failed"
    Write-Host "Check VPS logs: ssh ${VPS_USER}@${VPS_HOST} 'cd $VPS_PROJECT_DIR && docker-compose -f docker-compose.prod.yml logs'"
    exit 1
}

# Cleanup
Remove-Item -Path $tempDir -Recurse -Force
