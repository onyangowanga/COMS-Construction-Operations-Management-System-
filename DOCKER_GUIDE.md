# 🐳 COMS Docker Setup Guide

Complete guide for running COMS frontend and backend in Docker containers.

---

## 📋 Overview

Your COMS application now runs in Docker with the following services:

- **PostgreSQL** (port 5432) - Database
- **Redis** (port 6379) - Caching and sessions
- **Django Backend** (port 8000) - API server
- **Next.js Frontend** (port 3000) - Web application

---

## 🚀 Quick Start (Development)

### Prerequisites

- **Docker Desktop** installed and running
- **Docker Compose** (included with Docker Desktop)

### Start All Services

```bash
# From the COMS root directory
docker-compose up -d
```

This will:
1. Build the frontend and backend images
2. Start all containers in the background
3. Set up networking between services

### Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000/api
- **Django Admin**: http://localhost:8000/admin

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f frontend
docker-compose logs -f web
docker-compose logs -f db
```

### Stop All Services

```bash
docker-compose down
```

To remove volumes (⚠️ deletes database data):
```bash
docker-compose down -v
```

---

## 🔧 Development Workflow

### Hot Reload

Both frontend and backend have hot-reload enabled:
- **Frontend**: Changes to `/frontend` files trigger rebuild
- **Backend**: Changes to Python files restart the server

### Install New Dependencies

**Frontend:**
```bash
# Enter the container
docker-compose exec frontend sh

# Inside container
npm install <package-name>

# Exit and rebuild
exit
docker-compose restart frontend
```

**Backend:**
```bash
docker-compose exec web sh
pip install <package-name>
exit
docker-compose restart web
```

### Run Commands Inside Containers

**Django Commands:**
```bash
# Create superuser
docker-compose exec web python manage.py createsuperuser

# Run migrations
docker-compose exec web python manage.py migrate

# Collect static files
docker-compose exec web python manage.py collectstatic --noinput

# Create new migration
docker-compose exec web python manage.py makemigrations

# Django shell
docker-compose exec web python manage.py shell
```

**Frontend Commands:**
```bash
# Access frontend shell
docker-compose exec frontend sh

# Run linter
docker-compose exec frontend npm run lint

# Run build
docker-compose exec frontend npm run build
```

**Database Commands:**
```bash
# Access PostgreSQL shell
docker-compose exec db psql -U coms_user -d coms_db

# Create database backup
docker-compose exec db pg_dump -U coms_user coms_db > backup.sql

# Restore database
docker-compose exec -T db psql -U coms_user coms_db < backup.sql
```

---

## 🏗️ First-Time Setup

### 1. Build and Start Containers

```bash
docker-compose up -d --build
```

### 2. Run Database Migrations

```bash
docker-compose exec web python manage.py migrate
```

### 3. Create Django Superuser

```bash
docker-compose exec web python manage.py createsuperuser
```

### 4. Collect Static Files

```bash
docker-compose exec web python manage.py collectstatic --noinput
```

### 5. Load Initial Data (if any)

```bash
docker-compose exec web python manage.py loaddata initial_data.json
```

---

## 🌐 Production Deployment

### Using Production Docker Compose

```bash
# Build production images
docker-compose -f docker-compose.prod.yml build

# Start production services
docker-compose -f docker-compose.prod.yml up -d

# View logs
docker-compose -f docker-compose.prod.yml logs -f
```

### Production Checklist

Before deploying to production:

1. **Environment Variables**: Create `.env` file with production values:
```env
# Database
POSTGRES_USER=coms_user
POSTGRES_PASSWORD=<strong-password>
POSTGRES_DB=coms_db

# Django
SECRET_KEY=<generate-secret-key>
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Frontend
NEXT_PUBLIC_API_URL=https://yourdomain.com/api
NEXT_PUBLIC_WS_URL=wss://yourdomain.com/ws
```

2. **SSL/TLS**: Set up HTTPS with Let's Encrypt (nginx service included)

3. **Database Backups**: Set up automated backups

4. **Monitoring**: Configure logging and monitoring

5. **Security**: Review security settings in Django and Next.js

---

## 🔍 Troubleshooting

### Container Won't Start

**Check logs:**
```bash
docker-compose logs <service-name>
```

**Rebuild the container:**
```bash
docker-compose up -d --build <service-name>
```

### Database Connection Error

**Check database is ready:**
```bash
docker-compose exec db pg_isready -U coms_user -d coms_db
```

**Restart database:**
```bash
docker-compose restart db
```

### Frontend Build Errors

**Clear node_modules volume:**
```bash
docker-compose down
docker volume rm coms_frontend_node_modules
docker-compose up -d --build frontend
```

### Port Already in Use

**Change ports in docker-compose.yml:**
```yaml
ports:
  - "3001:3000"  # Change 3000 to 3001
```

### Out of Disk Space

**Clean up Docker:**
```bash
# Remove unused containers, networks, images
docker system prune -a

# Remove volumes (⚠️ deletes data)
docker volume prune
```

---

## 📊 Container Management

### View Running Containers

```bash
docker-compose ps
```

### Restart a Service

```bash
docker-compose restart <service-name>
```

### Rebuild a Service

```bash
docker-compose up -d --build <service-name>
```

### Access Container Shell

```bash
# Frontend
docker-compose exec frontend sh

# Backend
docker-compose exec web sh

# Database
docker-compose exec db sh
```

### Monitor Resource Usage

```bash
docker stats
```

---

## 🔄 Updates and Maintenance

### Update Application Code

```bash
# Pull latest code
git pull

# Rebuild and restart
docker-compose up -d --build
```

### Update Dependencies

**Frontend:**
```bash
# Update package.json, then:
docker-compose exec frontend npm install
docker-compose restart frontend
```

**Backend:**
```bash
# Update requirements.txt, then:
docker-compose exec web pip install -r requirements.txt
docker-compose restart web
```

### Database Migrations

```bash
# After model changes
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## 📁 Docker File Structure

```
COMS/
├── docker-compose.yml         # Development setup
├── docker-compose.prod.yml    # Production setup
├── Dockerfile                 # Backend Dockerfile
├── frontend/
│   ├── Dockerfile            # Frontend production
│   ├── Dockerfile.dev        # Frontend development
│   └── .dockerignore         # Ignored files
└── nginx/                    # Nginx config (production)
    ├── nginx.conf
    └── conf.d/
```

---

## ⚙️ Environment Variables

### Frontend (.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000/api
NEXT_PUBLIC_WS_URL=ws://localhost:8000/ws
NEXT_PUBLIC_ACCESS_TOKEN_EXPIRE=86400
NEXT_PUBLIC_REFRESH_TOKEN_EXPIRE=604800
```

### Backend (django .env or docker-compose)

```env
DEBUG=True
SECRET_KEY=dev-secret-key
DATABASE_URL=postgresql://coms_user:coms_pass@db:5432/coms_db
REDIS_URL=redis://redis:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
```

---

## 🚦 Health Checks

All services have health checks configured:

**Check service health:**
```bash
docker inspect --format='{{.State.Health.Status}}' coms_postgres
docker inspect --format='{{.State.Health.Status}}' coms_redis
```

---

## 📝 Best Practices

1. **Use .dockerignore**: Keep image sizes small
2. **Multi-stage builds**: Frontend uses multi-stage for optimization
3. **Volume mounts**: Development uses volumes for hot-reload
4. **Health checks**: Ensure dependencies are ready
5. **Named volumes**: Persist data between restarts
6. **Networks**: Isolate services with Docker networks
7. **Environment variables**: Never hardcode secrets

---

## 🎯 Quick Reference

| Action | Command |
|--------|---------|
| Start all | `docker-compose up -d` |
| Stop all | `docker-compose down` |
| View logs | `docker-compose logs -f` |
| Rebuild | `docker-compose up -d --build` |
| Django shell | `docker-compose exec web python manage.py shell` |
| Frontend shell | `docker-compose exec frontend sh` |
| Database shell | `docker-compose exec db psql -U coms_user -d coms_db` |
| Create superuser | `docker-compose exec web python manage.py createsuperuser` |
| Run migrations | `docker-compose exec web python manage.py migrate` |
| Clean up | `docker system prune -a` |

---

**Your COMS application is now fully containerized and ready for development and production deployment!** 🎉
