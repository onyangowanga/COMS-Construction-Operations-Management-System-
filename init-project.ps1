# init-project.ps1 - Initialize Django COMS Project (PowerShell version)

Write-Host "🚀 Initializing COMS Project..." -ForegroundColor Green

# Create Django project if manage.py doesn't exist
if (-not (Test-Path "manage.py")) {
    Write-Host "📦 Creating Django project..." -ForegroundColor Yellow
    django-admin startproject config .
}

# Create apps directory
New-Item -ItemType Directory -Force -Path "apps" | Out-Null

# Create core Django apps
$apps = @("authentication", "projects", "ledger", "workers", "consultants", "clients", "core")

foreach ($app in $apps) {
    if (-not (Test-Path "apps\$app")) {
        Write-Host "📂 Creating app: $app" -ForegroundColor Yellow
        python manage.py startapp $app "apps\$app"
    }
}

# Create static and media directories
New-Item -ItemType Directory -Force -Path "static" | Out-Null
New-Item -ItemType Directory -Force -Path "staticfiles" | Out-Null
New-Item -ItemType Directory -Force -Path "media\uploads\documents" | Out-Null
New-Item -ItemType Directory -Force -Path "media\uploads\drawings" | Out-Null
New-Item -ItemType Directory -Force -Path "media\uploads\photos" | Out-Null

# Create templates directory
$templateDirs = @("authentication", "projects", "ledger", "workers", "consultants", "clients", "base")
foreach ($dir in $templateDirs) {
    New-Item -ItemType Directory -Force -Path "templates\$dir" | Out-Null
}

# Create logs directory
New-Item -ItemType Directory -Force -Path "logs" | Out-Null

# Copy .env.example to .env if it doesn't exist
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.example") {
        Copy-Item ".env.example" ".env"
        Write-Host "📄 Created .env file from .env.example" -ForegroundColor Green
    }
}

Write-Host ""
Write-Host "✅ Project structure created successfully!" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Update .env file with your configuration" -ForegroundColor White
Write-Host "2. Run migrations: python manage.py migrate" -ForegroundColor White
Write-Host "3. Create superuser: python manage.py createsuperuser" -ForegroundColor White
Write-Host "4. Start server: python manage.py runserver" -ForegroundColor White
