# Makefile-equivalent PowerShell Commands for COMS
# Save this as: commands.ps1
# Usage: . .\commands.ps1; Invoke-<CommandName>

function Invoke-Setup {
    Write-Host "🔧 Setting up COMS project..." -ForegroundColor Green
    Copy-Item .env.example .env -ErrorAction SilentlyContinue
    docker-compose build
    Write-Host "✅ Setup complete!" -ForegroundColor Green
}

function Invoke-Up {
    Write-Host "🚀 Starting COMS containers..." -ForegroundColor Green
    docker-compose up -d
    Write-Host "✅ Containers started! Visit http://localhost:8000" -ForegroundColor Green
}

function Invoke-Down {
    Write-Host "🛑 Stopping COMS containers..." -ForegroundColor Yellow
    docker-compose down
    Write-Host "✅ Containers stopped!" -ForegroundColor Green
}

function Invoke-Logs {
    docker-compose logs -f web
}

function Invoke-Shell {
    Write-Host "🐚 Opening Django shell..." -ForegroundColor Cyan
    docker-compose exec web python manage.py shell
}

function Invoke-DBShell {
    Write-Host "🗄️ Opening database shell..." -ForegroundColor Cyan
    docker-compose exec db psql -U coms_user -d coms_db
}

function Invoke-Migrate {
    Write-Host "🔄 Running migrations..." -ForegroundColor Yellow
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    Write-Host "✅ Migrations complete!" -ForegroundColor Green
}

function Invoke-Superuser {
    Write-Host "👤 Creating superuser..." -ForegroundColor Cyan
    docker-compose exec web python manage.py createsuperuser
}

function Invoke-Test {
    Write-Host "🧪 Running tests..." -ForegroundColor Yellow
    docker-compose exec web pytest
}

function Invoke-TestCoverage {
    Write-Host "📊 Running tests with coverage..." -ForegroundColor Yellow
    docker-compose exec web pytest --cov=apps --cov-report=html
    Write-Host "✅ Coverage report generated in htmlcov/" -ForegroundColor Green
}

function Invoke-Lint {
    Write-Host "🔍 Running linters..." -ForegroundColor Yellow
    docker-compose exec web pylint apps/
}

function Invoke-Format {
    Write-Host "✨ Formatting code with Black..." -ForegroundColor Yellow
    docker-compose exec web black apps/
    Write-Host "✅ Code formatted!" -ForegroundColor Green
}

function Invoke-Static {
    Write-Host "📦 Collecting static files..." -ForegroundColor Yellow
    docker-compose exec web python manage.py collectstatic --noinput
    Write-Host "✅ Static files collected!" -ForegroundColor Green
}

function Invoke-Clean {
    Write-Host "🧹 Cleaning up..." -ForegroundColor Yellow
    docker-compose down -v
    Remove-Item -Recurse -Force __pycache__, *.pyc, .pytest_cache, htmlcov -ErrorAction SilentlyContinue
    Write-Host "✅ Cleanup complete!" -ForegroundColor Green
}

function Invoke-Rebuild {
    Write-Host "🔨 Rebuilding containers..." -ForegroundColor Yellow
    docker-compose down
    docker-compose build --no-cache
    docker-compose up -d
    Write-Host "✅ Rebuild complete!" -ForegroundColor Green
}

function Invoke-Backup {
    $timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
    $backupFile = "backups/coms_backup_$timestamp.sql"
    Write-Host "💾 Creating database backup: $backupFile" -ForegroundColor Yellow
    New-Item -ItemType Directory -Force -Path backups | Out-Null
    docker-compose exec -T db pg_dump -U coms_user coms_db > $backupFile
    Write-Host "✅ Backup created!" -ForegroundColor Green
}

function Invoke-Help {
    Write-Host @"
🏗️  COMS Project Commands

Setup & Management:
  Invoke-Setup         - Initial project setup
  Invoke-Up           - Start all containers
  Invoke-Down         - Stop all containers
  Invoke-Rebuild      - Rebuild containers from scratch

Development:
  Invoke-Logs         - View web container logs
  Invoke-Shell        - Open Django shell
  Invoke-DBShell      - Open PostgreSQL shell

Database:
  Invoke-Migrate      - Run database migrations
  Invoke-Backup       - Create database backup

Testing & Quality:
  Invoke-Test         - Run test suite
  Invoke-TestCoverage - Run tests with coverage report
  Invoke-Lint         - Run code linting
  Invoke-Format       - Format code with Black

Utilities:
  Invoke-Superuser    - Create Django superuser
  Invoke-Static       - Collect static files
  Invoke-Clean        - Clean up containers and cache
  Invoke-Help         - Show this help message

Usage: . .\commands.ps1; Invoke-<CommandName>
"@ -ForegroundColor Cyan
}

Write-Host "✅ COMS commands loaded! Type 'Invoke-Help' for available commands." -ForegroundColor Green
