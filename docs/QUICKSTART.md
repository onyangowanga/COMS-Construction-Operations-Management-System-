# 🚀 COMS Quick Start Guide

Get COMS up and running in under 10 minutes!

## Prerequisites Check ✅

Before starting, ensure you have:
- [ ] Docker Desktop installed and running
- [ ] VS Code installed
- [ ] Dev Containers extension in VS Code
- [ ] Git installed

## Step-by-Step Setup

### 1. Open Project in VS Code

```powershell
# Navigate to project directory
cd "c:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS"

# Open in VS Code
code .
```

### 2. Open in Dev Container

**When VS Code opens, you'll see a notification:**
> "Folder contains a Dev Container configuration file. Reopen folder to develop in a container"

Click **"Reopen in Container"**

**Or manually:**
1. Press `Ctrl+Shift+P`
2. Type "Dev Containers: Reopen in Container"
3. Press Enter

**Wait for the container to build** (first time takes 2-5 minutes)

### 3. Initialize the Project

Once inside the container, open the integrated terminal and run:

```powershell
# Initialize project structure
.\init-project.ps1

# Or on Linux/Mac
chmod +x init-project.sh
./init-project.sh
```

This will:
- Create the Django project
- Create all app directories
- Set up folder structure
- Copy environment template

### 4. Configure Environment

```powershell
# The .env file should already exist from init script
# Verify it's there
Test-Path .env

# If not, copy from example
Copy-Item .env.example .env
```

**Default .env works for development!** No changes needed initially.

### 5. Run Database Migrations

```powershell
python manage.py migrate
```

Expected output:
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, sessions
Running migrations:
  Applying contenttypes.0001_initial... OK
  Applying auth.0001_initial... OK
  ...
```

### 6. Create Your Admin Account

```powershell
python manage.py createsuperuser
```

You'll be prompted for:
- Username: `admin` (or your choice)
- Email: `your@email.com`
- Password: (enter twice)

### 7. Start the Development Server

```powershell
python manage.py runserver
```

You should see:
```
Starting development server at http://0.0.0.0:8000/
Quit the server with CTRL-BREAK.
```

### 8. Access the Application

Open your browser and visit:

- **Main App**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin
- **API Docs**: http://localhost:8000/api/docs/ (after API setup)

**Login with the superuser credentials you created!**

## 🎉 You're All Set!

Your COMS development environment is ready. Here's what you can do now:

### Next Steps

1. **Explore the Admin**
   - Visit http://localhost:8000/admin
   - Log in with your superuser account
   - Explore Django's built-in admin interface

2. **Start Building Modules**
   - Begin with Week 1: Authentication module
   - Follow the roadmap in `docs/ROADMAP.md`

3. **Load Helper Commands**
   ```powershell
   # Load PowerShell commands
   . .\commands.ps1
   Invoke-Help
   ```

## 🔧 Common Commands

### Using PowerShell Helper (Recommended)

```powershell
# Load commands
. .\commands.ps1

# View all containers
Invoke-Up          # Start containers
Invoke-Down        # Stop containers
Invoke-Logs        # View logs

# Database
Invoke-Migrate     # Run migrations
Invoke-DBShell     # Open database shell

# Development
Invoke-Shell       # Django shell
Invoke-Test        # Run tests
```

### Manual Commands

```powershell
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver

# Django shell
python manage.py shell

# Run tests
pytest
```

## 🐛 Troubleshooting

### Issue: Container won't build
**Solution:**
```powershell
# Rebuild without cache
docker-compose build --no-cache
```

### Issue: Port 8000 already in use
**Solution:**
```powershell
# Find and stop the process using port 8000
Get-Process -Id (Get-NetTCPConnection -LocalPort 8000).OwningProcess | Stop-Process

# Or change port in docker-compose.yml
# ports:
#   - "8001:8000"  # Use 8001 instead
```

### Issue: Database connection refused
**Solution:**
```powershell
# Restart database container
docker-compose restart db

# Check database is running
docker-compose ps
```

### Issue: Permission denied on init-project.sh
**Solution:**
```bash
# Make script executable
chmod +x init-project.sh
```

### Issue: Module not found errors
**Solution:**
```powershell
# Reinstall dependencies
pip install -r requirements.txt
```

## 📚 Useful Resources

- **README**: [README.md](../README.md)
- **Architecture**: [docs/ARCHITECTURE.md](ARCHITECTURE.md)
- **Roadmap**: [docs/ROADMAP.md](ROADMAP.md)
- **Django Documentation**: https://docs.djangoproject.com/
- **DRF Documentation**: https://www.django-rest-framework.org/

## 🎯 Development Workflow

### Daily Workflow

1. **Start your day**
   ```powershell
   . .\commands.ps1
   Invoke-Up
   ```

2. **Make changes to code**
   - Django auto-reloads on file changes
   - No need to restart server

3. **Run tests**
   ```powershell
   Invoke-Test
   ```

4. **Commit changes**
   ```powershell
   git add .
   git commit -m "Descriptive message"
   git push
   ```

5. **End of day**
   ```powershell
   Invoke-Down
   ```

### Before Every Commit

```powershell
# Format code
Invoke-Format

# Run tests
Invoke-Test

# Check for errors
Invoke-Lint
```

## 🔐 Security Notes

- **Never commit `.env` file** (already in .gitignore)
- **Change SECRET_KEY in production**
- **Use strong passwords**
- **Keep DEBUG=False in production**

## 🆘 Getting Help

If you run into issues:

1. Check this guide first
2. Review error messages carefully
3. Check Docker container logs
4. Consult Django documentation
5. Search GitHub issues (if repository exists)

## 🎊 Ready to Build!

You now have a fully functional development environment. Start with **Week 1** of the roadmap and build amazing features!

**Happy Coding! 🚀**

---

**Need to start fresh?**

```powershell
# Complete reset (WARNING: Deletes all data!)
Invoke-Clean
.\init-project.ps1
python manage.py migrate
python manage.py createsuperuser
```
