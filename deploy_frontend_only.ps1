# COMS - Deploy Frontend Only from Local to VPS
# This script deploys only the Next.js frontend

$ErrorActionPreference = "Stop"

# Configuration
$VPS_HOST = "156.232.88.156"
$VPS_USER = "root"
$VPS_PROJECT_DIR = "/root/coms"
$LOCAL_DIR = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMS - Deploy Frontend Only to VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Source: $LOCAL_DIR\frontend" -ForegroundColor Green
Write-Host "[INFO] Target: ${VPS_USER}@${VPS_HOST}:${VPS_PROJECT_DIR}/frontend" -ForegroundColor Green
Write-Host ""

# Check if frontend directory exists
$frontendDir = Join-Path $LOCAL_DIR "frontend"
if (-not (Test-Path $frontendDir)) {
    Write-Host "[ERROR] Frontend directory not found at $frontendDir" -ForegroundColor Red
    exit 1
}

# Create temporary directory
$tempDir = Join-Path $env:TEMP "coms_frontend_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Write-Host "[INFO] Step 1: Preparing frontend files..." -ForegroundColor Green

# Copy frontend directory
$frontendTempDir = Join-Path $tempDir "frontend"
Copy-Item -Path $frontendDir -Destination $frontendTempDir -Recurse -Force -Exclude @('node_modules', '.next', '.git', 'build', 'dist', '*.log')

# Copy deployment script
if (Test-Path (Join-Path $LOCAL_DIR "deploy_frontend.sh")) {
    Copy-Item (Join-Path $LOCAL_DIR "deploy_frontend.sh") -Destination $tempDir -Force
}

# Create zip
$zipPath = "$tempDir.zip"
Write-Host "[INFO] Creating archive..." -ForegroundColor Green
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Upload
Write-Host "[INFO] Uploading frontend files to VPS..." -ForegroundColor Green
scp "$zipPath" "${VPS_USER}@${VPS_HOST}:/tmp/coms_frontend.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    exit 1
}

# Extract and deploy frontend
Write-Host "[INFO] Step 2: Deploying frontend on VPS..." -ForegroundColor Green
$bashScript = @"
cd /tmp
unzip -o coms_frontend.zip -d coms_frontend_extracted

# Backup current frontend if it exists
if [ -d "$VPS_PROJECT_DIR/frontend" ]; then
    mv $VPS_PROJECT_DIR/frontend `$VPS_PROJECT_DIR/frontend.backup.`$(date +%Y%m%d_%H%M%S)
fi

# Copy new frontend
cp -r coms_frontend_extracted/frontend $VPS_PROJECT_DIR/

# Copy deployment script if exists
if [ -f coms_frontend_extracted/deploy_frontend.sh ]; then
    cp coms_frontend_extracted/deploy_frontend.sh $VPS_PROJECT_DIR/
fi

# Fix line endings
cd $VPS_PROJECT_DIR
find . -type f -name "*.sh" -exec dos2unix {} \; 2>/dev/null || true
find . -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Run frontend deployment
if [ -f deploy_frontend.sh ]; then
    chmod +x deploy_frontend.sh
    ./deploy_frontend.sh
else
    echo "Deploying frontend manually..."
    docker-compose -f docker-compose.prod.yml stop frontend
    docker-compose -f docker-compose.prod.yml rm -f frontend
    docker-compose -f docker-compose.prod.yml build --no-cache frontend
    docker-compose -f docker-compose.prod.yml up -d frontend
    sleep 10
    docker-compose -f docker-compose.prod.yml restart nginx
fi

# Cleanup
rm -rf /tmp/coms_frontend_extracted
rm /tmp/coms_frontend.zip

# Remove old backups (keep last 3)
cd $VPS_PROJECT_DIR
ls -t frontend.backup.* 2>/dev/null | tail -n +4 | xargs -r rm -rf
"@

ssh "${VPS_USER}@${VPS_HOST}" $bashScript

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Frontend deployment failed" -ForegroundColor Red

    # Cleanup local files
    Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
    Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

    exit 1
}

# Cleanup local files
Write-Host "[INFO] Cleaning up..." -ForegroundColor Green
Remove-Item $tempDir -Recurse -Force -ErrorAction SilentlyContinue
Remove-Item $zipPath -Force -ErrorAction SilentlyContinue

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Frontend Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Frontend is running at:" -ForegroundColor Green
Write-Host "  http://$VPS_HOST" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  ssh ${VPS_USER}@${VPS_HOST} 'cd /root/coms && docker-compose -f docker-compose.prod.yml logs -f frontend'" -ForegroundColor White
Write-Host ""
