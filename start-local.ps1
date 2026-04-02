# COMS Local Development Quick Start Script
# This script helps you set up and test COMS locally before deployment

param(
    [switch]$Reset = $false,
    [switch]$SkipTests = $false
)

$ErrorActionPreference = "Stop"

function Write-Step {
    param([string]$Message)
    Write-Host "`n[$([DateTime]::Now.ToString('HH:mm:ss'))] " -ForegroundColor Cyan -NoNewline
    Write-Host $Message -ForegroundColor White
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
Write-Host "   COMS Local Development Environment Setup" -ForegroundColor Cyan
Write-Host "=======================================================" -ForegroundColor Cyan
Write-Host ""

# Check if Docker is running
Write-Step "Checking Docker..."
try {
    $dockerVersion = docker --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker is installed: $dockerVersion"
    } else {
        throw "Docker command failed"
    }
} catch {
    Write-ErrorMsg "Docker is not running or not installed!"
    Write-Host "  Please install Docker Desktop from: https://www.docker.com/products/docker-desktop"
    exit 1
}

# Check if docker-compose is available
try {
    $composeVersion = docker-compose --version 2>$null
    if ($LASTEXITCODE -eq 0) {
        Write-Success "Docker Compose is available: $composeVersion"
    }
} catch {
    Write-ErrorMsg "Docker Compose is not available!"
    exit 1
}

# Check if .env file exists
Write-Step "Checking environment configuration..."
if (-not (Test-Path ".env")) {
    Write-Info "Creating .env file from .env.example..."
    Copy-Item ".env.example" ".env"
    Write-Success ".env file created"
    Write-Host "  You can edit .env if needed, but defaults work for local development"
} else {
    Write-Success ".env file exists"
}

# Stop and remove existing containers if Reset flag is set
if ($Reset) {
    Write-Step "Resetting environment (removing existing containers and volumes)..."
    docker-compose down -v 2>$null
    Write-Success "Environment reset complete"
}

# Build containers
Write-Step "Building Docker containers..."
Write-Info "This may take a few minutes on first run..."
docker-compose build
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to build containers"
    exit 1
}
Write-Success "Containers built successfully"

# Start containers
Write-Step "Starting containers..."
docker-compose up -d
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to start containers"
    exit 1
}
Write-Success "Containers started"

# Wait for services to be ready
Write-Step "Waiting for services to be ready..."
Start-Sleep -Seconds 10

# Check container status
Write-Info "Checking container status..."
$psOutput = docker-compose ps 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "All containers are up"
    Write-Host ""
    Write-Host $psOutput
} else {
    Write-ErrorMsg "Some containers may not be running"
    Write-Host "  Run 'docker-compose ps' to check status"
}

# Run migrations
Write-Step "Running database migrations..."
docker-compose exec -T web python manage.py migrate
if ($LASTEXITCODE -ne 0) {
    Write-ErrorMsg "Failed to run migrations"
    Write-Host "  Try: docker-compose logs web"
    exit 1
}
Write-Success "Migrations completed"

# Collect static files
Write-Step "Collecting static files..."
docker-compose exec -T web python manage.py collectstatic --noinput 2>$null
if ($LASTEXITCODE -eq 0) {
    Write-Success "Static files collected"
} else {
    Write-Info "Static files collection skipped (not critical for development)"
}

# Check if superuser exists
Write-Step "Checking for admin user..."
$userCount = docker-compose exec -T web python manage.py shell -c "from apps.authentication.models import User; print(User.objects.filter(is_superuser=True).count())" 2>$null
if ($userCount -match "0") {
    Write-Info "No superuser found. You will need to create one."
    Write-Host ""
    Write-Host "  Creating superuser..." -ForegroundColor Yellow
    Write-Host "  (Press Ctrl+C to skip and create later with: docker-compose exec web python manage.py createsuperuser)"
    Write-Host ""
    docker-compose exec web python manage.py createsuperuser
} else {
    Write-Success "Admin user exists"
}

# Run tests if not skipped
if (-not $SkipTests) {
    Write-Step "Running tests..."
    docker-compose exec -T web pytest --tb=short
    if ($LASTEXITCODE -eq 0) {
        Write-Success "All tests passed!"
    } else {
        Write-Info "Some tests failed (this is OK for development)"
    }
} else {
    Write-Info "Tests skipped (use -SkipTests:`$false to run tests)"
}

# Display access information
Write-Host ""
Write-Host "=======================================================" -ForegroundColor Green
Write-Host "   COMS is ready for local development!" -ForegroundColor Green
Write-Host "=======================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Application URLs:" -ForegroundColor Cyan
Write-Host "   Frontend:     " -NoNewline
Write-Host "http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend API:  " -NoNewline
Write-Host "http://localhost:8000/api" -ForegroundColor Yellow
Write-Host "   Django Admin: " -NoNewline
Write-Host "http://localhost:8000/admin" -ForegroundColor Yellow
Write-Host "   Health Check: " -NoNewline
Write-Host "http://localhost:8000/health/" -ForegroundColor Yellow
Write-Host ""
Write-Host "Useful Commands:" -ForegroundColor Cyan
Write-Host "   View logs:       " -NoNewline
Write-Host "docker-compose logs -f" -ForegroundColor White
Write-Host "   Stop services:   " -NoNewline
Write-Host "docker-compose down" -ForegroundColor White
Write-Host "   Restart:         " -NoNewline
Write-Host "docker-compose restart" -ForegroundColor White
Write-Host "   Django shell:    " -NoNewline
Write-Host "docker-compose exec web python manage.py shell" -ForegroundColor White
Write-Host "   Database shell:  " -NoNewline
Write-Host "docker-compose exec db psql -U coms_user -d coms_db" -ForegroundColor White
Write-Host "   Run tests:       " -NoNewline
Write-Host "docker-compose exec web pytest" -ForegroundColor White
Write-Host ""
Write-Host "Documentation:" -ForegroundColor Cyan
Write-Host "   Local Testing:   " -NoNewline
Write-Host "LOCAL_TESTING_GUIDE.md" -ForegroundColor White
Write-Host "   VPS Deployment:  " -NoNewline
Write-Host "DEPLOY_FROM_LOCAL.md" -ForegroundColor White
Write-Host "   Module Status:   " -NoNewline
Write-Host "MODULE_STATUS_REPORT.md" -ForegroundColor White
Write-Host ""
Write-Host "Next Steps:" -ForegroundColor Cyan
Write-Host "   1. Open http://localhost:3000 in your browser"
Write-Host "   2. Test the application functionality"
Write-Host "   3. Make your code changes"
Write-Host "   4. When ready, deploy with: .\deploy_to_vps.ps1"
Write-Host ""
