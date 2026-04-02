# Deploy COMS frontend: local Docker build → VPS deployment

> Purpose: build frontend locally in Docker, copy to VPS, run production docker-compose.
> Scope: no `git` push/pull on VPS required.

## 1) Preconditions

- Local machine with Node 18+ + npm and Docker.
- VPS accessible with SSH and Docker Compose.
- Project path (example):
  - `C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS`
- VPS path:
  - `/home/user/coms`
- Confirm repo branch is main locally and code changes are up-to-date.

## 2) Build frontend locally (inside local Docker)

### Option A: Host node build (recommended)
```powershell
cd "C:\programing\Realtime projects\COMS\COMS PROJECT IMPLEMENTATTION\COMS\frontend"
npm ci
npm run lint
npm run build