# 🧪 COMS Local Testing & Development Guide

Complete guide for running and testing COMS on your local Docker environment before deploying to VPS.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [Initial Setup](#initial-setup)
3. [Running Locally](#running-locally)
4. [Testing the Application](#testing-the-application)
5. [Development Workflow](#development-workflow)
6. [Troubleshooting](#troubleshooting)
7. [Ready for Deployment](#ready-for-deployment)

---

## Prerequisites

### Required Software

**Windows:**
- ✅ Docker Desktop for Windows
- ✅ Git for Windows
- ✅ PowerShell 5.1+ or PowerShell Core
- ✅ Code Editor (VS Code recommended)

**Installation Check:**
```powershell
# Check Docker
docker --version
docker-compose --version

# Check Git
git --version

# Check PowerShell
$PSVersionTable.PSVersion
```

Expected output:
```
Docker version 24.0.x
Docker Compose version v2.x.x
git version 2.x.x
Major  Minor  Build  Revision
-----  -----  -----  --------
5      1      x      x
```

---

## Initial Setup

### Step 1: Navigate to Project Directory

```powershell
cd "C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"
```

### Step 2: Create Environment File

```powershell
# Copy example environment file
Copy-Item .env.example .env

# Edit the .env file
notepad .env
```

**Default `.env` for local development:**
```env
# Django Settings
DEBUG=True
SECRET_KEY=local-dev-secret-key-12345
ALLOWED_HOSTS=localhost,127.0.0.1,0.0.0.0

# Database Configuration
DATABASE_URL=postgresql://coms_user:coms_pass@db:5432/coms_db

# Redis Configuration
REDIS_URL=redis://redis:6379/0

# JWT Settings
JWT_ACCESS_TOKEN_LIFETIME=60
JWT_REFRESH_TOKEN_LIFETIME=1440

# Email Configuration (Console for development)
EMAIL_BACKEND=django.core.mail.backends.console.EmailBackend

# Application Settings
SITE_URL=http://localhost:8000
FRONTEND_URL=http://localhost:3000

# Security Settings (Development - all False)
SECURE_SSL_REDIRECT=False
SESSION_COOKIE_SECURE=False
CSRF_COOKIE_SECURE=False

# AWS S3 (Disabled for local)
USE_S3=False
```

**💡 Tip:** For local development, you don't need to change most values. The defaults work fine!

### Step 3: Build Docker Images

```powershell
# Build all containers
docker-compose build

# Or rebuild from scratch (if you have issues)
docker-compose build --no-cache
```

Expected output:
```
[+] Building 45.2s (15/15) FINISHED
 => [web internal] load build definition...
 => [frontend internal] load build definition...
 => CACHED [web 2/8] RUN apt-get update...
 ...
```

---

## Running Locally

### Method 1: Using Docker Compose (Recommended)

#### Start All Services

```powershell
# Start all containers in detached mode
docker-compose up -d

# Or start with logs visible
docker-compose up
```

**What happens:**
1. PostgreSQL database starts (port 5432)
2. Redis cache starts (port 6379)
3. Django backend starts (port 8000)
4. Next.js frontend starts (port 3000)

**Check Status:**
```powershell
docker-compose ps
```

Expected output:
```
NAME                IMAGE              STATUS              PORTS
coms_postgres       postgres:15-alpine Up 2 minutes        0.0.0.0:5432->5432/tcp
coms_redis          redis:7-alpine     Up 2 minutes        0.0.0.0:6379->6379/tcp
coms_web            coms-web           Up 2 minutes        0.0.0.0:8000->8000/tcp
coms_frontend       coms-frontend      Up 2 minutes        0.0.0.0:3000->3000/tcp
```

#### Run Database Migrations

**First time setup:**
```powershell
# Run migrations
docker-compose exec web python manage.py migrate

# Create static files directory
docker-compose exec web python manage.py collectstatic --noinput
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, authentication, projects, bq, ...
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  Applying authentication.0001_initial... OK
  ...
```

#### Create Superuser

```powershell
docker-compose exec web python manage.py createsuperuser
```

Follow prompts:
```
Email: admin@coms.local
First Name: Admin
Last Name: User
Password: ******** (choose a strong password)
Password (again): ********
Superuser created successfully.
```

### Method 2: Using PowerShell Commands File

```powershell
# Source the commands file
. .\commands.ps1

# Then use helper functions
Start-COMS          # Start all containers
Stop-COMS           # Stop all containers
Restart-COMS        # Restart all containers
Show-Logs           # View logs
```

---

## Testing the Application

### 1. Test Backend API

#### Health Check
```powershell
# Test health endpoint
curl http://localhost:8000/health/
```

Expected response:
```json
{
  "status": "healthy",
  "timestamp": "2026-03-23T10:30:00Z",
  "services": {
    "database": "connected",
    "redis": "connected"
  }
}
```

#### Django Admin
1. Open browser: http://localhost:8000/admin
2. Login with superuser credentials
3. Verify you can see all modules

#### API Root
```powershell
# View available API endpoints
curl http://localhost:8000/api/
```

#### Test Authentication
```powershell
# Register a new user
curl -X POST http://localhost:8000/api/auth/register/ `
  -H "Content-Type: application/json" `
  -d '{
    "email": "test@example.com",
    "password": "TestPass123!",
    "first_name": "Test",
    "last_name": "User"
  }'
```

Expected response:
```json
{
  "user": {
    "id": 2,
    "email": "test@example.com",
    "first_name": "Test",
    "last_name": "User"
  },
  "tokens": {
    "access": "eyJ0eXAiOiJKV1QiLCJhb...",
    "refresh": "eyJ0eXAiOiJKV1QiLCJhb..."
  }
}
```

### 2. Test Frontend

#### Open Application
1. Open browser: http://localhost:3000
2. You should see the COMS landing page
3. Test login with superuser credentials
4. Navigate through different modules

#### Hot Reload Test
1. Edit a frontend file (e.g., `frontend/src/app/page.tsx`)
2. Save the file
3. Browser should auto-refresh with changes

### 3. Test Database

#### Access Database Shell
```powershell
docker-compose exec db psql -U coms_user -d coms_db
```

SQL commands to test:
```sql
-- List all tables
\dt

-- Count users
SELECT COUNT(*) FROM authentication_user;

-- View recent events
SELECT * FROM events_systemevent ORDER BY created_at DESC LIMIT 5;

-- Exit
\q
```

### 4. Test Redis Cache

```powershell
# Access Redis CLI
docker-compose exec redis redis-cli

# Test commands
> PING
PONG

> KEYS *
(lists all cached keys)

> EXIT
```

### 5. Run Automated Tests

#### Backend Tests
```powershell
# Run all tests
docker-compose exec web pytest

# Run with coverage
docker-compose exec web pytest --cov=apps --cov-report=html

# Run specific module tests
docker-compose exec web pytest apps/authentication/tests/
docker-compose exec web pytest apps/projects/tests/
```

Expected output:
```
======================== test session starts ========================
collected 45 items

apps/authentication/tests/test_models.py ....                  [ 8%]
apps/projects/tests/test_views.py ..........                   [ 30%]
apps/subcontracts/tests/test_services.py .........              [ 50%]
...

======================== 45 passed in 12.34s =======================
```

#### Frontend Tests
```powershell
# Access frontend container
docker-compose exec frontend sh

# Run tests
npm test

# Run linting
npm run lint

# Build test
npm run build
```

### 6. Test File Uploads

#### Test Document Upload
```powershell
# Create a test file
echo "Test document content" > test.txt

# Upload via API (replace TOKEN with your JWT token)
curl -X POST http://localhost:8000/api/documents/ `
  -H "Authorization: Bearer YOUR_JWT_TOKEN" `
  -F "file=@test.txt" `
  -F "name=Test Document" `
  -F "document_type=report"
```

Check uploaded file:
- Django Admin: http://localhost:8000/admin/documents/document/
- File system: Check `media/` directory in project root

---

## Development Workflow

### Daily Development Cycle

#### 1. Start Development Environment
```powershell
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f
```

#### 2. Make Code Changes

**Backend changes:**
- Edit files in `apps/`, `api/`, or `config/`
- Django auto-reloads on file changes
- No restart needed for Python code changes

**Frontend changes:**
- Edit files in `frontend/src/`
- Next.js hot-reloads automatically
- Browser refreshes automatically

**Database changes:**
```powershell
# Create migrations
docker-compose exec web python manage.py makemigrations

# Apply migrations
docker-compose exec web python manage.py migrate
```

#### 3. Test Your Changes

```powershell
# Test specific endpoint
curl http://localhost:8000/api/your-endpoint/

# Run relevant tests
docker-compose exec web pytest apps/your_module/

# Check logs
docker-compose logs -f web
```

#### 4. Commit Changes

```powershell
# Check status
git status

# Add changes
git add .

# Commit (but don't push yet)
git commit -m "Description of changes"
```

### Common Development Tasks

#### View Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f frontend
docker-compose logs -f db

# Last 100 lines
docker-compose logs --tail=100 web
```

#### Django Shell
```powershell
# Interactive Python shell
docker-compose exec web python manage.py shell

# Example: Create test data
from apps.authentication.models import User
user = User.objects.create_user(
    email='dev@test.com',
    password='TestPass123!'
)
```

#### Database Management
```powershell
# Backup database
docker-compose exec -T db pg_dump -U coms_user coms_db > backup_$(date +%Y%m%d).sql

# Restore database
docker-compose exec -T db psql -U coms_user coms_db < backup_20260323.sql

# Reset database (CAUTION: Deletes all data!)
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

#### Rebuild Containers
```powershell
# After changing Dockerfile or requirements.txt
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

---

## Troubleshooting

### Issue 1: Containers Won't Start

**Error:** "Cannot start service web: port is already allocated"

**Solution:**
```powershell
# Check what's using the port
netstat -ano | findstr :8000

# Kill the process (replace PID)
taskkill /PID <process_id> /F

# Or change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use 8001 instead
```

### Issue 2: Database Connection Error

**Error:** "could not connect to server: Connection refused"

**Solution:**
```powershell
# Check database is running
docker-compose ps db

# Check database health
docker-compose exec db pg_isready -U coms_user -d coms_db

# Restart database
docker-compose restart db

# Wait for it to be healthy
docker-compose logs -f db
```

### Issue 3: Frontend Not Loading

**Error:** "Cannot GET /" or blank page

**Solution:**
```powershell
# Check frontend logs
docker-compose logs frontend

# Rebuild frontend
docker-compose exec frontend npm install
docker-compose restart frontend

# Or rebuild container
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

### Issue 4: Migrations Not Applied

**Error:** "no such table: authentication_user"

**Solution:**
```powershell
# Run migrations
docker-compose exec web python manage.py migrate

# If migrations exist but aren't detected
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

### Issue 5: Static Files Not Loading

**Error:** 404 on /static/ URLs

**Solution:**
```powershell
# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Check DEBUG=True in .env (for development)
```

### Issue 6: Permission Errors

**Error:** "Permission denied" when accessing files

**Solution:**
```powershell
# Fix permissions (Windows)
# Right-click project folder > Properties > Security > Edit
# Give your user full control

# Or run Docker as administrator
```

### Issue 7: Out of Disk Space

```powershell
# Clean Docker system
docker system prune -a

# Remove unused volumes
docker volume prune

# Remove old containers
docker-compose down -v
```

---

## Pre-Deployment Checklist

Before deploying to VPS, verify everything works locally:

### ✅ Backend Checks

```powershell
# 1. All migrations applied
docker-compose exec web python manage.py showmigrations

# 2. No model changes pending
docker-compose exec web python manage.py makemigrations --dry-run

# 3. Static files collected
docker-compose exec web python manage.py collectstatic --noinput --dry-run

# 4. Django checks pass
docker-compose exec web python manage.py check

# 5. Tests pass
docker-compose exec web pytest

# 6. Security checks (if installed)
docker-compose exec web python manage.py check --deploy
```

### ✅ Frontend Checks

```powershell
# 1. Build succeeds
docker-compose exec frontend npm run build

# 2. No TypeScript errors
docker-compose exec frontend npx tsc --noEmit

# 3. Linting passes
docker-compose exec frontend npm run lint
```

### ✅ Functionality Tests

- [ ] Can register new user
- [ ] Can login/logout
- [ ] Can create project
- [ ] Can upload document
- [ ] Can create BQ items
- [ ] Can submit approvals
- [ ] All modules accessible
- [ ] API responses correct
- [ ] No console errors in browser
- [ ] No errors in Docker logs

### ✅ Production Environment File

```powershell
# Verify .env.production exists with correct values
Get-Content .env.production
```

Required in `.env.production`:
- [ ] `DEBUG=False`
- [ ] Strong `SECRET_KEY` (different from dev)
- [ ] Correct `ALLOWED_HOSTS` (VPS IP)
- [ ] Production database credentials
- [ ] Email configuration (if using)
- [ ] S3 configuration (if using)

---

## Ready for Deployment

Once all tests pass locally, you're ready to deploy to VPS!

### Deploy to VPS

```powershell
# From project directory
.\deploy_to_vps.ps1
```

See [DEPLOY_FROM_LOCAL.md](DEPLOY_FROM_LOCAL.md) for detailed deployment instructions.

### Post-Deployment Verification

After deploying to VPS:

```powershell
# Test VPS endpoints
curl http://156.232.88.156/health/
curl http://156.232.88.156/api/

# SSH into VPS and check
ssh root@156.232.88.156
cd /root/coms
docker-compose -f docker-compose.prod.yml ps
docker-compose -f docker-compose.prod.yml logs -f
```

---

## Quick Command Reference

### Essential Commands

```powershell
# Start development
docker-compose up -d

# View logs
docker-compose logs -f

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run tests
docker-compose exec web pytest

# Django shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec db psql -U coms_user -d coms_db

# Stop all
docker-compose down

# Rebuild
docker-compose build --no-cache
docker-compose up -d
```

### Application URLs

- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin
- **Health Check:** http://localhost:8000/health/

---

## Getting Help

### View Documentation
- [README.md](README.md) - Project overview
- [MODULE_STATUS_REPORT.md](MODULE_STATUS_REPORT.md) - Module implementation status
- [DEPLOY_FROM_LOCAL.md](DEPLOY_FROM_LOCAL.md) - VPS deployment guide

### Check Logs
```powershell
# Application logs
docker-compose logs -f web

# All services
docker-compose logs -f

# Database logs
docker-compose logs db
```

### Docker Status
```powershell
# Container status
docker-compose ps

# Resource usage
docker stats

# Network info
docker network ls
docker network inspect coms_default
```

---

**Happy Development! 🚀**

Remember:
1. **Test locally first** - Always test changes before deploying
2. **Commit frequently** - Small, focused commits are best
3. **Run tests** - Ensure tests pass before deployment
4. **Check logs** - Monitor logs for errors
5. **Backup data** - Create database backups before major changes
