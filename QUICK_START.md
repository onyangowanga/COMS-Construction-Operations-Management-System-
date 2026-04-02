# 🚀 COMS Quick Start Guide

Get started with COMS Construction Management System in minutes!

---

## 📌 Choose Your Path

### 1️⃣ First Time Developer? → Start Here!

**Goal:** Run COMS locally and test it

```powershell
# Navigate to project
cd "C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"

# Run automatic setup (recommended!)
.\start-local.ps1
```

This script will:
- ✅ Check Docker installation
- ✅ Create environment file
- ✅ Build containers
- ✅ Run migrations
- ✅ Create superuser
- ✅ Run tests
- ✅ Start application

**Then:** Open http://localhost:3000 and start developing!

📖 **Detailed Guide:** [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)

---

### 2️⃣ Ready to Deploy? → Deploy to VPS!

**Prerequisite:** ✅ Application tested locally and working

```powershell
# Deploy from local to VPS (bypasses GitHub Actions)
.\deploy_to_vps.ps1
```

📖 **Detailed Guide:** [DEPLOY_FROM_LOCAL.md](DEPLOY_FROM_LOCAL.md)

---

### 3️⃣ Want to Know What's Built? → Check Status

📊 **Module Status:** [MODULE_STATUS_REPORT.md](MODULE_STATUS_REPORT.md)

**Summary:**
- ✅ 19 modules complete (79%)
- ⚠️ 3 modules partial (13%)
- 🔄 2 modules pending (8%)

---

## 🎯 Common Tasks

### Local Development

```powershell
# Start containers
docker-compose up -d

# View logs
docker-compose logs -f

# Stop containers
docker-compose down

# Run tests
docker-compose exec web pytest

# Django shell
docker-compose exec web python manage.py shell

# Database migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser
```

### Deploy to VPS

```powershell
# Full deployment
.\deploy_to_vps.ps1

# Check VPS status
ssh root@156.232.88.156 "cd /root/coms && docker-compose -f docker-compose.prod.yml ps"

# View VPS logs
ssh root@156.232.88.156 "cd /root/coms && docker-compose -f docker-compose.prod.yml logs -f"
```

---

## 📂 Project Structure

```
COMS/
├── apps/                    # Django apps (24 modules)
│   ├── authentication/      # User authentication & auth
│   ├── projects/           # Project management
│   ├── bq/                 # Bill of Quantities
│   ├── cashflow/           # Cash flow forecasting
│   ├── valuations/         # IPCs and valuations
│   ├── subcontracts/       # Subcontractor management
│   ├── variations/         # Change orders
│   ├── documents/          # Document management
│   ├── notifications/      # Multi-channel notifications
│   ├── reporting/          # Report builder
│   └── ... (15 more)
│
├── api/                    # Centralized API
│   ├── serializers/        # DRF serializers
│   ├── views/              # API viewsets
│   └── routers.py          # URL routing
│
├── frontend/               # Next.js frontend
│   └── src/
│       ├── app/            # Next.js app directory
│       ├── components/     # React components
│       └── lib/            # Utilities
│
├── config/                 # Django settings
│   ├── settings.py         # Configuration
│   └── urls.py             # URL routing
│
├── docker-compose.yml      # Local development
├── docker-compose.prod.yml # Production VPS
├── .env                    # Local environment
├── .env.production         # Production environment
│
└── Documentation/
    ├── QUICK_START.md              # This file
    ├── LOCAL_TESTING_GUIDE.md      # Local development guide
    ├── DEPLOY_FROM_LOCAL.md        # VPS deployment guide
    └── MODULE_STATUS_REPORT.md     # Implementation status
```

---

## 🌐 Application URLs

### Local Development
- **Frontend:** http://localhost:3000
- **Backend API:** http://localhost:8000/api
- **Django Admin:** http://localhost:8000/admin
- **Health Check:** http://localhost:8000/health/

### Production (VPS)
- **Frontend:** http://156.232.88.156
- **Backend API:** http://156.232.88.156/api
- **Django Admin:** http://156.232.88.156/admin
- **Health Check:** http://156.232.88.156/health/

---

## 🛠️ Technology Stack

### Backend
- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL 15
- **Cache:** Redis 7
- **Task Queue:** Celery (configured)
- **Authentication:** JWT (Simple JWT)

### Frontend
- **Framework:** Next.js 14+ (App Router)
- **UI Library:** React 18
- **Styling:** Tailwind CSS
- **State Management:** React Context/Hooks
- **API Client:** Axios

### Infrastructure
- **Containerization:** Docker & Docker Compose
- **Web Server:** Nginx (production)
- **Deployment:** Direct SSH deployment script
- **Version Control:** Git

---

## 📋 Prerequisites

### Required
- ✅ Docker Desktop (Windows/Mac) or Docker Engine (Linux)
- ✅ Git
- ✅ PowerShell (Windows) or Bash (Linux/Mac)
- ✅ Code Editor (VS Code recommended)

### For VPS Deployment
- ✅ SSH access to VPS (root@156.232.88.156)
- ✅ VPS with Docker installed
- ✅ `.env.production` configured

---

## ⚡ Quick Commands

### Setup and Start
```powershell
# Automated setup (recommended)
.\start-local.ps1

# Manual setup
docker-compose build
docker-compose up -d
docker-compose exec web python manage.py migrate
docker-compose exec web python manage.py createsuperuser
```

### Development
```powershell
# Start with logs
docker-compose up

# Start in background
docker-compose up -d

# Restart specific service
docker-compose restart web
docker-compose restart frontend

# Rebuild after code changes
docker-compose build
docker-compose up -d
```

### Testing
```powershell
# Run all tests
docker-compose exec web pytest

# Run with coverage
docker-compose exec web pytest --cov=apps --cov-report=html

# Run specific module
docker-compose exec web pytest apps/projects/tests/

# Frontend tests
docker-compose exec frontend npm test
```

### Database
```powershell
# Django shell
docker-compose exec web python manage.py shell

# Database shell
docker-compose exec db psql -U coms_user -d coms_db

# Migrations
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate

# Backup
docker-compose exec -T db pg_dump -U coms_user coms_db > backup.sql
```

### Deployment
```powershell
# Deploy to VPS
.\deploy_to_vps.ps1

# SSH to VPS
ssh root@156.232.88.156
```

---

## 🔍 Troubleshooting

### Containers won't start
```powershell
# Check Docker is running
docker --version

# Check logs
docker-compose logs

# Rebuild
docker-compose down
docker-compose build --no-cache
docker-compose up -d
```

### Port already in use
```powershell
# Find process using port 8000
netstat -ano | findstr :8000

# Kill process
taskkill /PID <process_id> /F
```

### Database errors
```powershell
# Reset database
docker-compose down -v
docker-compose up -d
docker-compose exec web python manage.py migrate
```

### Frontend not loading
```powershell
# Check logs
docker-compose logs frontend

# Rebuild
docker-compose build --no-cache frontend
docker-compose up -d frontend
```

---

## 📚 Documentation Index

| Document | Purpose |
|----------|---------|
| [QUICK_START.md](QUICK_START.md) | This file - getting started |
| [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md) | Complete local development guide |
| [DEPLOY_FROM_LOCAL.md](DEPLOY_FROM_LOCAL.md) | VPS deployment instructions |
| [MODULE_STATUS_REPORT.md](MODULE_STATUS_REPORT.md) | Implementation status report |
| [README.md](README.md) | Main project README |

---

## 🎓 Learning Path

### Day 1: Setup
1. ✅ Run `.\start-local.ps1`
2. ✅ Open http://localhost:3000
3. ✅ Login to Django admin
4. ✅ Explore the modules

### Day 2: Development
1. ✅ Read [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)
2. ✅ Make a small code change
3. ✅ Test locally
4. ✅ Run tests with `docker-compose exec web pytest`

### Day 3: Deployment
1. ✅ Ensure all tests pass
2. ✅ Read [DEPLOY_FROM_LOCAL.md](DEPLOY_FROM_LOCAL.md)
3. ✅ Run `.\deploy_to_vps.ps1`
4. ✅ Verify deployment on VPS

### Week 2+: Feature Development
1. ✅ Review [MODULE_STATUS_REPORT.md](MODULE_STATUS_REPORT.md)
2. ✅ Pick a module to enhance
3. ✅ Add tests
4. ✅ Deploy to VPS

---

## 🤝 Contributing

### Before Making Changes
1. Pull latest code: `git pull`
2. Test locally: `.\start-local.ps1`
3. Create feature branch: `git checkout -b feature/your-feature`

### After Making Changes
1. Run tests: `docker-compose exec web pytest`
2. Commit changes: `git commit -m "Your message"`
3. Test deployment (if needed): `.\deploy_to_vps.ps1`
4. Push to repository: `git push`

---

## 🆘 Getting Help

### Check Logs
```powershell
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f web
docker-compose logs -f frontend
docker-compose logs -f db
```

### Check Container Status
```powershell
docker-compose ps
docker stats
```

### Common Issues
- **Port conflicts:** Stop other services using ports 3000, 8000, 5432, 6379
- **Docker not running:** Start Docker Desktop
- **Permission errors:** Run as Administrator
- **Build failures:** Clear Docker cache with `docker system prune -a`

---

## ✅ Pre-Deployment Checklist

Before deploying to VPS:

- [ ] All tests pass locally (`docker-compose exec web pytest`)
- [ ] Frontend builds successfully (`docker-compose exec frontend npm run build`)
- [ ] No console errors in browser
- [ ] Database migrations up to date
- [ ] `.env.production` configured correctly
- [ ] Application works at http://localhost:3000
- [ ] Admin panel works at http://localhost:8000/admin
- [ ] API responds at http://localhost:8000/api

---

## 🚀 You're Ready!

Choose your next step:

**→ New to the project?**
Run: `.\start-local.ps1`

**→ Ready to develop?**
Read: [LOCAL_TESTING_GUIDE.md](LOCAL_TESTING_GUIDE.md)

**→ Ready to deploy?**
Run: `.\deploy_to_vps.ps1`

**Happy Building! 🏗️**
