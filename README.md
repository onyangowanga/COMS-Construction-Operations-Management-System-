# COMS - Construction Operations Management System

A comprehensive web-based platform for managing construction projects, finances, workers, and client communications.

## 🏗️ Project Overview

COMS is designed to streamline construction project management with features including:
- **Smart Financial Ledger** - Real-time P&L tracking
- **Digital Muster Roll** - Worker attendance and payroll
- **Project Management** - Multi-project tracking with health indicators
- **Document Management** - Version-controlled drawings and BOQs
- **Client Portal** - Transparent project visibility
- **Role-Based Access Control** - Secure multi-user system

## 🚀 Technology Stack

### Backend
- **Framework:** Django 4.2+ with Django REST Framework
- **Database:** PostgreSQL 15
- **Cache/Queue:** Redis
- **Authentication:** JWT (Simple JWT)
- **API Docs:** DRF Spectacular (Swagger/OpenAPI)

### Frontend
- **Template Engine:** Django Templates
- **Interactivity:** HTMX
- **Styling:** Bootstrap 5

### DevOps
- **Containerization:** Docker + Docker Compose
- **Development:** VS Code Dev Containers
- **Production:** Gunicorn + Nginx
- **CI/CD:** GitHub Actions (to be configured)

## 📋 Prerequisites

- **Docker Desktop** installed and running
- **VS Code** with Dev Containers extension
- **Git** for version control

## 🛠️ Getting Started

### 1. Clone the Repository
```bash
git clone <repository-url>
cd COMS
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Update .env with your configuration
# (Use your preferred text editor)
```

### 3. Open in Dev Container

**Option A: Using VS Code**
1. Open the project folder in VS Code
2. Click "Reopen in Container" when prompted
3. Wait for the container to build and start

**Option B: Using Command Palette**
1. Press `Ctrl+Shift+P` (Windows) or `Cmd+Shift+P` (Mac)
2. Type "Dev Containers: Reopen in Container"
3. Select it and wait for the setup

### 4. Initialize the Project

```bash
# Inside the container terminal (PowerShell)
.\init-project.ps1

# Or if using bash
chmod +x init-project.sh
./init-project.sh
```

### 5. Create Superuser
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

Visit: http://localhost:8000

## 📁 Project Structure

```
COMS/
├── .devcontainer/          # VS Code Dev Container configuration
├── apps/                   # Django applications
│   ├── authentication/     # User auth & RBAC
│   ├── projects/          # Project management
│   ├── ledger/            # Financial tracking
│   ├── workers/           # Muster roll & attendance
│   ├── consultants/       # Document management
│   ├── clients/           # Client portal
│   └── core/              # Shared utilities
├── config/                # Django settings
├── static/                # Static files (CSS, JS)
├── staticfiles/          # Collected static files
├── media/                # User uploads
├── templates/            # HTML templates
├── logs/                 # Application logs
├── docker-compose.yml    # Docker services
├── Dockerfile            # Container definition
├── requirements.txt      # Python dependencies
└── manage.py            # Django management script
```

## 🎯 Development Phases

### Week 1: Authentication & Role Management ✅
- [ ] Custom User model
- [ ] JWT authentication
- [ ] Role-based permissions
- [ ] Login/logout flow

### Week 2: Project Management Core
- [ ] Project CRUD operations
- [ ] Budget allocation
- [ ] Milestone tracking
- [ ] Health status indicators

### Week 3-4: Smart Ledger
- [ ] Expense tracking
- [ ] Payment recording
- [ ] P&L calculations
- [ ] Financial dashboards
- [ ] CSV exports

### Week 4: Digital Muster Roll
- [ ] Worker management
- [ ] Attendance logging
- [ ] Machine tracking
- [ ] Payroll reports

### Week 5: Consultant Hub
- [ ] Document upload/download
- [ ] Version control
- [ ] Approval workflows
- [ ] Activity logs

### Week 6: Client Portal
- [ ] Read-only project view
- [ ] Milestone visibility
- [ ] Image gallery
- [ ] Messaging system

## 🔐 User Roles

1. **Super Admin** - Full system access
2. **Contractor** - Project owner/manager
3. **Site Manager/Foreman** - Daily operations
4. **Quantity Surveyor (QS)** - Financial oversight
5. **Architect** - Design & approvals
6. **Client** - Read-only progress tracking

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=apps

# Run specific app tests
pytest apps/authentication/tests/
```

## 📊 Database Migrations

```bash
# Create migrations
python manage.py makemigrations

# Apply migrations
python manage.py migrate

# Check migration status
python manage.py showmigrations
```

## 🔧 Useful Commands

```bash
# Create new Django app
python manage.py startapp app_name apps/app_name

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Django shell
python manage.py shell

# Database shell
python manage.py dbshell
```

## 📝 API Documentation

Once the server is running, access Swagger documentation at:
- http://localhost:8000/api/docs/
- http://localhost:8000/api/schema/

## 🚀 Deployment

### Quick Deployment to VPS

**1. Quick Start (15 minutes):**
```bash
# On your VPS
ssh root@156.232.88.156
curl -o setup-vps.sh https://raw.githubusercontent.com/onyangowanga/COMS-Construction-Operations-Management-System-/master/setup-vps.sh
chmod +x setup-vps.sh
./setup-vps.sh
```

**2. Configure GitHub Secrets:**
Go to: https://github.com/YOUR_USERNAME/COMS/settings/secrets/actions

Add:
- `VPS_HOST`: `156.232.88.156`
- `VPS_USERNAME`: `root`
- `VPS_PASSWORD`: `Your-VPS-Password`

**3. Push to Deploy:**
```bash
git push origin master
# Automatically deploys via GitHub Actions!
```

### Documentation

- 📘 [Complete Deployment Guide](docs/VPS_DEPLOYMENT_GUIDE.md)
- 🚀 [Quick Start Guide](docs/QUICK_START_DEPLOYMENT.md)
- 📋 [Deployment Summary](docs/DEPLOYMENT_SUMMARY.md)

### Production Stack

- **Web Server:** Nginx (reverse proxy, static files, SSL)
- **App Server:** Gunicorn (4 workers)
- **Database:** PostgreSQL 15 (persistent volumes)
- **Cache:** Redis 7
- **Containers:** Docker + Docker Compose
- **CI/CD:** GitHub Actions (auto-deploy on push)

### Production Checklist
- [x] Docker production configuration (`docker-compose.prod.yml`)
- [x] Nginx reverse proxy with SSL support
- [x] Production Dockerfile (`Dockerfile.prod`)
- [x] Environment configuration (`.env.production`)
- [x] Deployment scripts (`setup-vps.sh`, `deploy.sh`)
- [x] GitHub Actions CI/CD pipeline
- [x] Health checks and monitoring
- [ ] SSL certificate (enable after domain setup)
- [ ] Email notifications configured
- [ ] Database backups automated

## 📖 Documentation

### General Documentation
- [System Architecture](docs/ARCHITECTURE.md) (To be created)
- [API Documentation](docs/API.md) (To be created)
- [Database Schema](docs/DATABASE.md) (To be created)
- [User Manual](docs/USER_MANUAL.md) (To be created)

### Deployment Documentation
- [VPS Deployment Guide](docs/VPS_DEPLOYMENT_GUIDE.md) - Complete deployment guide
- [Quick Start Deployment](docs/QUICK_START_DEPLOYMENT.md) - 15-minute setup
- [Deployment Summary](docs/DEPLOYMENT_SUMMARY.md) - Files and checklist
- [Frontend Implementation](docs/FRONTEND_IMPLEMENTATION.md) - UI documentation
- [Client Demo Guide](docs/CLIENT_DEMO_GUIDE.md) - Demo walkthrough

## 🤝 Contributing

This is a solo project, but best practices are followed:
- Feature branches for new work
- Descriptive commit messages
- Code reviews (self-review checklist)
- Documentation updates

## 📄 License

Proprietary - All rights reserved

## 👤 Author

**Your Name**
- Role: Full Stack Developer
- Project: COMS Construction Management System

## 📞 Support

For issues or questions:
- Create an issue in the repository
- Contact: [your-email@example.com]

---

**Status:** 🟢 Active Development
**Version:** 0.1.0 (Alpha)
**Last Updated:** March 2026
