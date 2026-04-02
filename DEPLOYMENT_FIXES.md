# Deployment Fixes Applied

## Issues Fixed

### 1. ModuleNotFoundError: No module named 'apps.media'

**Problem:**
During Docker build, Django couldn't find the `apps.media` module even though it was in INSTALLED_APPS.

**Root Cause:**
The `apps/media/__init__.py` file was empty, so Django didn't recognize it as a proper app.

**Solution:**
Added `default_app_config` to `apps/media/__init__.py`:
```python
default_app_config = 'apps.media.apps.MediaConfig'
```

**File Changed:**
- `apps/media/__init__.py`

---

### 2. Database Not Ready During Migrations

**Problem:**
The deployment script tried to run migrations immediately after starting containers, but the database wasn't ready yet, causing the migration command to fail.

**Root Cause:**
The 10-second sleep wasn't enough for PostgreSQL to fully initialize and accept connections.

**Solution:**
Added a proper database readiness check that polls `pg_isready` up to 30 times (60 seconds max):

```bash
# Wait for database to be ready
print_status "Waiting for database to be ready..."
for i in {1..30}; do
    if docker-compose -f docker-compose.prod.yml exec -T db pg_isready -U coms_user 2>/dev/null; then
        print_status "Database is ready!"
        break
    fi
    echo -n "."
    sleep 2
done
```

**Files Changed:**
- `deploy.sh`
- `deploy_backend.sh`

---

### 3. Collectstatic Failing During Docker Build

**Problem:**
`RUN python manage.py collectstatic --noinput || true` in Dockerfile.prod was failing because:
1. Database wasn't available during build
2. Some apps require database connection to load

**Root Cause:**
Collectstatic was being run too early in the build process when Django couldn't fully initialize.

**Solution:**
Removed `collectstatic` from Dockerfile.prod since it's already run by the deployment script after all containers are up and database is ready.

**File Changed:**
- `Dockerfile.prod`

---

### 4. Logs Directory Permission Issues

**Problem:**
Django couldn't write to `/app/logs/coms.log` causing errors:
```
PermissionError: [Errno 13] Permission denied: '/app/logs/coms.log'
```

**Root Cause:**
The logs directory was created but didn't have proper write permissions for the `coms` user.

**Solution:**
Created logs directory with proper permissions in both Dockerfiles:
```dockerfile
RUN mkdir -p /app/staticfiles /app/media /app/logs && \
    chmod -R 777 /app/logs
```

**Files Changed:**
- `Dockerfile`
- `Dockerfile.prod`

---

## Summary of Changes

| File | Change | Reason |
|------|--------|--------|
| `apps/media/__init__.py` | Added default_app_config | Fix module import |
| `deploy.sh` | Added database readiness check | Ensure DB is ready before migrations |
| `deploy_backend.sh` | Added database readiness check | Ensure DB is ready before migrations |
| `Dockerfile.prod` | Removed collectstatic from build | Run it after containers start |
| `Dockerfile` | Added /app/logs with 777 permissions | Fix log file write errors |
| `Dockerfile.prod` | Added /app/logs with 777 permissions | Fix log file write errors |

---

## Testing the Fixes

### Full Deployment Test

```powershell
# Deploy everything
.\deploy_to_vps.ps1

# Expected result:
# - Build completes without errors
# - Database check waits and confirms ready
# - Migrations run successfully
# - Collectstatic runs successfully
# - All health checks pass
```

### Backend Only Test

```powershell
# Deploy backend only
.\deploy_backend_only.ps1

# Expected result:
# - Backend builds without errors
# - Database check confirms ready
# - Migrations run successfully
```

### Verify Logs Work

```bash
ssh root@156.232.88.156
cd /root/coms

# Check logs directory
docker-compose -f docker-compose.prod.yml exec web ls -la /app/logs

# Expected output:
# drwxrwxrwx ... logs/
# -rw-r--r-- ... coms.log

# Verify logs are being written
docker-compose -f docker-compose.prod.yml exec web tail -f /app/logs/coms.log
```

---

## What to Expect Now

### Build Process
1. ✅ Docker image builds without module errors
2. ✅ No collectstatic errors during build
3. ✅ Logs directory created with proper permissions

### Deployment Process
1. ✅ Containers start
2. ✅ Script waits for database (up to 60 seconds)
3. ✅ Migrations run after database is confirmed ready
4. ✅ Collectstatic runs successfully
5. ✅ Health checks pass

### Runtime
1. ✅ Django can write logs to /app/logs/coms.log
2. ✅ All apps load correctly including apps.media
3. ✅ Database connections work properly

---

## Troubleshooting

### If Migration Still Fails

```bash
# SSH to VPS
ssh root@156.232.88.156
cd /root/coms

# Check database status
docker-compose -f docker-compose.prod.yml exec db pg_isready -U coms_user

# Manually run migrations
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate --plan
docker-compose -f docker-compose.prod.yml exec web python manage.py migrate
```

### If Logs Still Have Permission Issues

```bash
# SSH to VPS
ssh root@156.232.88.156
cd /root/coms

# Check permissions
docker-compose -f docker-compose.prod.yml exec web ls -la /app/logs

# Fix if needed
docker-compose -f docker-compose.prod.yml exec web chmod -R 777 /app/logs
docker-compose -f docker-compose.prod.yml restart web
```

### If Module Import Errors Persist

```bash
# SSH to VPS
ssh root@156.232.88.156
cd /root/coms

# Test Django can load apps
docker-compose -f docker-compose.prod.yml exec web python manage.py check

# Check specific app
docker-compose -f docker-compose.prod.yml exec web python -c "import apps.media; print('OK')"
```

---

## Next Deployment

You can now deploy with confidence:

```powershell
# Full deployment
.\deploy_to_vps.ps1

# Or backend only
.\deploy_backend_only.ps1

# Or frontend only
.\deploy_frontend_only.ps1
```

All fixes are now in place! 🎉
