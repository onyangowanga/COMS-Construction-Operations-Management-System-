# COMS VPS Deployment Guide

Complete guide to deploy COMS (Construction Operations Management System) to your VPS with automatic deployment from GitHub.

---

## 📋 Table of Contents

1. [Prerequisites](#prerequisites)
2. [VPS Information](#vps-information)
3. [Initial Setup](#initial-setup)
4. [GitHub Configuration](#github-configuration)
5. [First Deployment](#first-deployment)
6. [Automatic Deployment](#automatic-deployment)
7. [SSL Configuration](#ssl-configuration)
8. [Maintenance](#maintenance)
9. [Troubleshooting](#troubleshooting)

---

## Prerequisites

### On Your Local Machine
- Git installed
- GitHub account with repository access
- SSH client (PuTTY for Windows or built-in SSH for Linux/Mac)

### VPS Requirements
- Ubuntu 20.04+ or Debian 11+
- Minimum 2GB RAM (4GB recommended)
- 20GB+ storage
- Root access

---

## VPS Information

**Your VPS Details:**
```
Hostname: coms-rsv-02
IP Address: 156.232.88.156
Username: root
Password: Coms@0722!
VNC: 156.232.88.18:5937 (Password: 1eSVlnTJ)
```

**GitHub Repository:**
```
Owner: onyangowanga
Repository: COMS-Construction-Operations-Management-System-
Branch: main
```

---

## Initial Setup

### Step 1: Connect to Your VPS

#### On Windows (using PowerShell):
```powershell
ssh root@156.232.88.156
# Enter password when prompted: Coms@0722!
```

#### On Linux/Mac:
```bash
ssh root@156.232.88.156
# Enter password when prompted: Coms@0722!
```

### Step 2: Download and Run Setup Script

Once connected to your VPS, run these commands:

```bash
# Download the setup script directly from GitHub
curl -o setup-vps.sh https://raw.githubusercontent.com/onyangowanga/COMS-Construction-Operations-Management-System-/master/setup-vps.sh

# Make it executable
chmod +x setup-vps.sh

# Run the setup script
./setup-vps.sh
```

**What the setup script does:**
1. Updates system packages
2. Installs Docker and Docker Compose
3. Configures firewall (UFW)
4. Clones your GitHub repository
5. Creates `.env.production` file
6. Builds and starts Docker containers
7. Runs database migrations
8. Creates Django superuser
9. Collects static files

**During setup, you'll be prompted to:**
- Review and edit `.env.production` file
- Create a Django superuser account (admin credentials)
- Add SSH public key to GitHub (for easier future deployments)

### Step 3: Configure Environment Variables

The setup script will open nano editor for `.env.production`. Update these critical values:

```bash
# Generate a strong secret key
SECRET_KEY=<will be auto-generated>

# Database credentials (change these!)
POSTGRES_PASSWORD=your_strong_db_password_here

# Email configuration (for password reset, notifications)
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password

# Optional: Update allowed hosts if using domain name
ALLOWED_HOSTS=156.232.88.156,coms-rsv-02,yourdomain.com
```

**To save and exit nano:**
- Press `Ctrl+X`
- Press `Y` to confirm
- Press `Enter` to save

### Step 4: Create Superuser

You'll be prompted to create a Django superuser:

```
Username: admin
Email: admin@yourdomain.com
Password: <strong-password>
Password (again): <strong-password>
```

**Save these credentials securely!**

### Step 5: Verify Installation

After setup completes, verify the application is running:

```bash
# Check container status
docker ps

# Should see 4 containers:
# - coms_nginx_prod (nginx)
# - coms_web_prod (Django)
# - coms_postgres_prod (PostgreSQL)
# - coms_redis_prod (Redis)

# Test the application
curl http://localhost/health/

# Should return: {"status":"healthy","timestamp":"..."}
```

### Step 6: Access Your Application

Open a web browser and visit:
```
http://156.232.88.156
```

You should see the COMS login page!

**Default login (test user from development):**
```
Email: admin@test.com
Password: TestPass123!
```

**Or login with the superuser you just created.**

---

## GitHub Configuration

To enable automatic deployment when you push code to GitHub, you need to configure GitHub Secrets.

### Step 1: Add GitHub Secrets

1. Go to your GitHub repository: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/settings/secrets/actions

2. Click **"New repository secret"** and add these three secrets:

**Secret 1: VPS_HOST**
```
Name: VPS_HOST
Value: 156.232.88.156
```

**Secret 2: VPS_USERNAME**
```
Name: VPS_USERNAME
Value: root
```

**Secret 3: VPS_PASSWORD**
```
Name: VPS_PASSWORD
Value: Coms@0722!
```

### Step 2: Enable GitHub Actions

GitHub Actions is already configured in `.github/workflows/ci-cd.yml`. No additional setup needed!

**The workflow will:**
1. Run tests on every push/PR
2. Build Docker image for production
3. Deploy to VPS automatically when you push to `master` branch

---

## First Deployment

### Manual Deployment (Anytime)

SSH into your VPS and run:

```bash
cd /root/coms
./deploy.sh
```

**The deploy script will:**
1. Pull latest code from GitHub
2. Stop existing containers
3. Build new Docker images
4. Start containers with updated code
5. Run database migrations
6. Collect static files
7. Verify deployment health

### Automatic Deployment (via GitHub Actions)

Simply push your code to the `master` branch:

```bash
# On your local machine
git add .
git commit -m "Update application"
git push origin master
```

**GitHub Actions will automatically:**
1. Run tests
2. Build Docker image
3. Deploy to VPS
4. Verify deployment

**View deployment status:**
- Go to your repository on GitHub
- Click the **"Actions"** tab
- You'll see the workflow running

---

## Automatic Deployment

### How It Works

```
┌─────────────┐      ┌─────────────┐      ┌─────────────┐
│   You Push  │─────▶│   GitHub    │─────▶│  VPS Auto   │
│   to Master │      │   Actions   │      │   Deploy    │
└─────────────┘      └─────────────┘      └─────────────┘
                           │
                           ▼
                     Run Tests
                     Build Image
                     SSH to VPS
                     Run deploy.sh
                     Verify Health
```

### Workflow Triggers

The CI/CD workflow runs on:
- **Push to `main`**: Runs tests + deployment
- **Push to `develop`**: Runs tests only (no deployment)
- **Pull Requests**: Runs tests only

### Monitoring Deployments

**View logs in real-time:**

```bash
# SSH into VPS
ssh root@156.232.88.156

# View deployment logs
tail -f /var/log/coms-deploy.log

# View application logs
cd /root/coms
docker-compose -f docker-compose.prod.yml logs -f web

# View Nginx logs
docker-compose -f docker-compose.prod.yml logs -f nginx
```

---

## SSL Configuration

Enable HTTPS for secure connections.

### Option 1: Let's Encrypt (Free SSL)

**Requirements:**
- Domain name pointing to your VPS IP (156.232.88.156)
- Example: `coms.yourdomain.com` → `156.232.88.156`

**Steps:**

```bash
# SSH into VPS
ssh root@156.232.88.156

# Install Certbot
apt-get update
apt-get install -y certbot

# Stop Nginx temporarily
cd /root/coms
docker-compose -f docker-compose.prod.yml stop nginx

# Get SSL certificate
certbot certonly --standalone -d coms.yourdomain.com

# Certificate will be saved to:
# /etc/letsencrypt/live/coms.yourdomain.com/fullchain.pem
# /etc/letsencrypt/live/coms.yourdomain.com/privkey.pem

# Copy certificates to project
mkdir -p /root/coms/nginx/ssl
cp /etc/letsencrypt/live/coms.yourdomain.com/fullchain.pem /root/coms/nginx/ssl/cert.pem
cp /etc/letsencrypt/live/coms.yourdomain.com/privkey.pem /root/coms/nginx/ssl/key.pem

# Update nginx configuration to enable HTTPS
nano /root/coms/nginx/conf.d/coms.conf
# Uncomment the HTTPS server block (lines starting with #)

# Update .env.production
nano /root/coms/.env.production
# Change:
# SECURE_SSL_REDIRECT=True
# SESSION_COOKIE_SECURE=True
# CSRF_COOKIE_SECURE=True

# Restart containers
docker-compose -f docker-compose.prod.yml up -d

# Setup auto-renewal
crontab -e
# Add this line:
0 3 * * * certbot renew --quiet --post-hook "cp /etc/letsencrypt/live/coms.yourdomain.com/*.pem /root/coms/nginx/ssl/ && cd /root/coms && docker-compose -f docker-compose.prod.yml restart nginx"
```

### Option 2: Self-Signed Certificate (Testing Only)

```bash
# Create self-signed certificate
mkdir -p /root/coms/nginx/ssl
cd /root/coms/nginx/ssl

openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
  -keyout key.pem -out cert.pem \
  -subj "/C=KE/ST=Nairobi/L=Nairobi/O=COMS/CN=156.232.88.156"

# Edit nginx config and enable HTTPS (see Option 1)
```

---

## Maintenance

### Daily Operations

**View running containers:**
```bash
docker ps
```

**Restart a specific container:**
```bash
docker-compose -f docker-compose.prod.yml restart web
docker-compose -f docker-compose.prod.yml restart nginx
```

**View logs:**
```bash
# All logs
docker-compose -f docker-compose.prod.yml logs

# Specific container
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs nginx

# Follow logs (real-time)
docker-compose -f docker-compose.prod.yml logs -f web
```

### Database Backup

**Create backup:**
```bash
# Manual backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U coms_user coms_db > backup_$(date +%Y%m%d).sql

# Automated daily backups
crontab -e
# Add:
0 2 * * * cd /root/coms && docker-compose -f docker-compose.prod.yml exec -T db pg_dump -U coms_user coms_db > /root/backups/coms_db_$(date +\%Y\%m\%d).sql
```

**Restore backup:**
```bash
# Stop web container
docker-compose -f docker-compose.prod.yml stop web

# Restore database
cat backup_20260310.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U coms_user -d coms_db

# Start web container
docker-compose -f docker-compose.prod.yml start web
```

### Update Dependencies

**Update Python packages:**
```bash
# Update requirements.txt locally, then:
git add requirements.txt
git commit -m "Update dependencies"
git push origin master
# Auto-deploys via GitHub Actions

# Or manually on VPS:
cd /root/coms
git pull origin master
docker-compose -f docker-compose.prod.yml build --no-cache web
docker-compose -f docker-compose.prod.yml up -d
```

### System Updates

**Update Ubuntu:**
```bash
apt-get update
apt-get upgrade -y
apt-get autoremove -y
```

**Update Docker:**
```bash
apt-get update
apt-get install --only-upgrade docker-ce docker-ce-cli containerd.io
```

---

## Troubleshooting

### Application Not Starting

**Check container status:**
```bash
docker ps -a

# If containers are stopped, check logs:
docker-compose -f docker-compose.prod.yml logs web
```

**Common issues:**

1. **Database connection failed:**
```bash
# Check if PostgreSQL is running
docker-compose -f docker-compose.prod.yml ps db

# Restart database
docker-compose -f docker-compose.prod.yml restart db
```

2. **Migration errors:**
```bash
# Manually run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

3. **Static files not loading:**
```bash
# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput

# Restart Nginx
docker-compose -f docker-compose.prod.yml restart nginx
```

### Deployment Failed

**Check GitHub Actions logs:**
- Go to repository → Actions tab
- Click on the failed workflow
- Review error messages

**Common deployment errors:**

1. **SSH connection failed:**
   - Verify VPS is online: `ping 156.232.88.156`
   - Check GitHub Secrets are correct

2. **Git pull failed:**
```bash
# SSH to VPS
cd /root/coms
git status
# If conflicts exist:
git reset --hard origin/master
./deploy.sh
```

3. **Docker build failed:**
```bash
# Check Docker logs
docker-compose -f docker-compose.prod.yml logs

# Rebuild from scratch
docker-compose -f docker-compose.prod.yml down
docker system prune -a
./deploy.sh
```

### High Memory Usage

**Check memory usage:**
```bash
free -h
docker stats
```

**Optimize:**
```bash
# Reduce Gunicorn workers in Dockerfile.prod
# Change: --workers 4 → --workers 2

# Or increase VPS RAM if needed
```

### Firewall Issues

**Check firewall status:**
```bash
ufw status

# If needed, allow specific ports:
ufw allow 80/tcp
ufw allow 443/tcp
ufw reload
```

### Clean Up Docker Resources

**Remove old images and containers:**
```bash
# Remove stopped containers
docker container prune -f

# Remove unused images
docker image prune -a -f

# Remove unused volumes
docker volume prune -f

# Remove everything unused
docker system prune -a --volumes -f
```

---

## Performance Monitoring

### Basic Monitoring

**Check system resources:**
```bash
# CPU and memory
htop

# Disk usage
df -h

# Container resource usage
docker stats
```

### Application Monitoring

**Check application health:**
```bash
curl http://localhost/health/
```

**Monitor response times:**
```bash
# Install Apache Bench
apt-get install apache2-utils

# Test performance
ab -n 100 -c 10 http://localhost/
```

### Log Monitoring

**Monitor Nginx access logs:**
```bash
docker-compose -f docker-compose.prod.yml exec nginx tail -f /var/log/nginx/coms_access.log
```

**Monitor application errors:**
```bash
docker-compose -f docker-compose.prod.yml logs -f web | grep ERROR
```

---

## Security Checklist

- [x] Firewall enabled (UFW)
- [x] Non-root user for Django container
- [x] Strong database password
- [x] SECRET_KEY is random and secure
- [ ] SSL/TLS enabled (after domain setup)
- [ ] Regular backups configured
- [ ] Fail2ban installed (optional)
- [ ] Regular security updates
- [ ] Application monitoring setup

### Install Fail2ban (Optional)

Protects against brute force attacks:

```bash
apt-get install fail2ban -y

# Configure for SSH
cat > /etc/fail2ban/jail.local << EOF
[sshd]
enabled = true
port = 22
maxretry = 3
bantime = 3600
EOF

systemctl restart fail2ban
```

---

## Quick Reference Commands

### Deployment
```bash
# Manual deployment
cd /root/coms && ./deploy.sh

# View deployment logs
tail -f /var/log/coms-deploy.log
```

### Container Management
```bash
# View status
docker ps

# View all containers (including stopped)
docker ps -a

# Restart all containers
docker-compose -f docker-compose.prod.yml restart

# Stop all containers
docker-compose -f docker-compose.prod.yml down

# Start all containers
docker-compose -f docker-compose.prod.yml up -d
```

### Logs
```bash
# All logs
docker-compose -f docker-compose.prod.yml logs

# Specific container
docker-compose -f docker-compose.prod.yml logs nginx
docker-compose -f docker-compose.prod.yml logs web
docker-compose -f docker-compose.prod.yml logs db

# Follow logs (real-time)
docker-compose -f docker-compose.prod.yml logs -f
```

### Database
```bash
# Access PostgreSQL
docker-compose -f docker-compose.prod.yml exec db psql -U coms_user -d coms_db

# Backup
docker-compose -f docker-compose.prod.yml exec db pg_dump -U coms_user coms_db > backup.sql

# Restore
cat backup.sql | docker-compose -f docker-compose.prod.yml exec -T db psql -U coms_user -d coms_db
```

### Django Management
```bash
# Django shell
docker-compose -f docker-compose.prod.yml exec web python manage.py shell

# Create superuser
docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser

# Run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate

# Collect static files
docker-compose -f docker-compose.prod.yml exec web python manage.py collectstatic --noinput
```

---

## Support

### Documentation
- [Django Documentation](https://docs.djangoproject.com/)
- [Docker Documentation](https://docs.docker.com/)
- [Nginx Documentation](https://nginx.org/en/docs/)

### Repository
- Issues: https://github.com/onyangowanga/COMS-Construction-Operations-Management-System-/issues

---

**Your COMS application should now be successfully deployed and automatically updating from GitHub!** 🚀

Access your application at: **http://156.232.88.156**
