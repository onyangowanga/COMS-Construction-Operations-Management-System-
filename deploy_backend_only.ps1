# COMS - Deploy Backend Only from Local to VPS
# This script deploys only the Django backend

$ErrorActionPreference = "Stop"

# Configuration
$VPS_HOST = "156.232.88.156"
$VPS_USER = "root"
$VPS_PROJECT_DIR = "/root/coms"
$LOCAL_DIR = $PSScriptRoot

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "COMS - Deploy Backend Only to VPS" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "[INFO] Source: $LOCAL_DIR" -ForegroundColor Green
Write-Host "[INFO] Target: ${VPS_USER}@${VPS_HOST}:${VPS_PROJECT_DIR}" -ForegroundColor Green
Write-Host ""

# Create temporary directory
$tempDir = Join-Path $env:TEMP "coms_backend_$(Get-Date -Format 'yyyyMMdd_HHmmss')"
New-Item -ItemType Directory -Path $tempDir -Force | Out-Null

Write-Host "[INFO] Step 1: Preparing backend files..." -ForegroundColor Green

# Backend-specific files to sync
$backendFiles = @(
    "*.py",
    "requirements.txt",
    "Dockerfile",
    "Dockerfile.prod",
    "manage.py",
    "config",
    "apps",
    "api",
    "deploy_backend.sh",
    ".env.production.example"
)

# Copy backend files
foreach ($pattern in $backendFiles) {
    Get-ChildItem -Path $LOCAL_DIR -Filter $pattern -Recurse -ErrorAction SilentlyContinue | Where-Object {
        $relativePath = $_.FullName.Substring($LOCAL_DIR.Length)
        -not ($relativePath -match "\\__pycache__\\|\\\.pyc$|\\\.pyo$|\\node_modules\\|\\frontend\\|\\staticfiles\\|\\media\\")
    } | ForEach-Object {
        $targetPath = Join-Path $tempDir ($_.FullName.Substring($LOCAL_DIR.Length + 1))
        $targetDir = Split-Path $targetPath -Parent

        if (-not (Test-Path $targetDir)) {
            New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
        }

        if (-not $_.PSIsContainer) {
            Copy-Item $_.FullName -Destination $targetPath -Force
        }
    }
}

# Create zip
$zipPath = "$tempDir.zip"
Write-Host "[INFO] Creating archive..." -ForegroundColor Green
Compress-Archive -Path "$tempDir\*" -DestinationPath $zipPath -Force

# Upload
Write-Host "[INFO] Uploading backend files to VPS..." -ForegroundColor Green
scp "$zipPath" "${VPS_USER}@${VPS_HOST}:/tmp/coms_backend.zip"

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Upload failed" -ForegroundColor Red
    exit 1
}

# Extract and deploy backend
Write-Host "[INFO] Step 2: Deploying backend on VPS..." -ForegroundColor Green
ssh "${VPS_USER}@${VPS_HOST}" @"
cd /tmp
unzip -o coms_backend.zip -d coms_backend_extracted

# Sync backend files to project directory (preserve frontend)
cp -r coms_backend_extracted/* $VPS_PROJECT_DIR/

# Fix line endings
cd $VPS_PROJECT_DIR
find . -type f \( -name "*.sh" -o -name ".env*" -o -name "Dockerfile*" \) -exec dos2unix {} \; 2>/dev/null || true
find . -type f -name "*.sh" -exec chmod +x {} \; 2>/dev/null || true

# Run backend deployment
chmod +x deploy_backend.sh
./deploy_backend.sh

# Cleanup
rm -rf /tmp/coms_backend_extracted
rm /tmp/coms_backend.zip
"@

if ($LASTEXITCODE -ne 0) {
    Write-Host "[ERROR] Backend deployment failed" -ForegroundColor Red

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
Write-Host "Backend Deployment Complete!" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Backend API is running at:" -ForegroundColor Green
Write-Host "  API:   http://$VPS_HOST/api" -ForegroundColor White
Write-Host "  Admin: http://$VPS_HOST/admin" -ForegroundColor White
Write-Host ""
Write-Host "View logs:" -ForegroundColor Yellow
Write-Host "  ssh ${VPS_USER}@${VPS_HOST} 'cd /root/coms && docker-compose -f docker-compose.prod.yml logs -f web'" -ForegroundColor White
Write-Host ""
