# Development Setup Guide

This guide provides clear instructions for setting up the AI Project Manager development environment.

## Quick Start (Development Mode)

For most development work, use the **development mode** with hot reloading:

```bash
# 1. Start development environment with hot reloading
AI_PM_MODE=dev make ai-pm-start

# 2. Access the application
# - Frontend (with hot reload): http://localhost:3002
# - API (with hot reload): http://localhost:8001
# - API Health Check: http://localhost:8001/api/health
# - Database: localhost:5432
```

## Environment Modes

### Development Mode (Recommended for Development)
- **Purpose**: Active development with hot reloading
- **Command**: `AI_PM_MODE=dev make ai-pm-start`
- **Ports**:
  - Frontend: `http://localhost:3002` (hot reload enabled)
  - API: `http://localhost:8001` (hot reload with Air)
  - Database: `localhost:5432`
- **Features**:
  - Frontend: Vite HMR (Hot Module Replacement)
  - Backend: Air hot reloading for Go code changes
  - Volume mounts for source code
  - Development optimized builds

### Production Mode
- **Purpose**: Production-like testing
- **Command**: `make ai-pm-start` (default)
- **Ports**:
  - Frontend: `http://localhost:3000`
  - API: `http://localhost:8000`
  - Database: `localhost:5432`
- **Features**:
  - Optimized builds
  - No hot reloading
  - Production Docker images

## Development Workflow

### 1. Initial Setup
```bash
# Clone and navigate to project
cd ai-pm

# Verify Docker is running
docker --version

# Start development environment
AI_PM_MODE=dev make ai-pm-start
```

### 2. Verify Setup
```bash
# Check service status (shows database, dev, and prod environments)
make ai-pm-status

# Check logs
make ai-pm-logs

# Test API health
curl http://localhost:8001/api/health

# Test frontend access
curl -I http://localhost:3002
```

### 3. Environment Management
```bash
# Switch between environments (preserves database automatically)
AI_PM_MODE=dev make ai-pm-switch    # Switch to development
make ai-pm-switch                   # Switch to production

# Granular environment control
make ai-pm-stop-dev                 # Stop development only
make ai-pm-stop-prod                # Stop production only
make ai-pm-stop                     # Stop both (preserves database)
make ai-pm-stop-all                 # ⚠️ Stop everything including database

# Status shows clear indicators
make ai-pm-status
# Output shows:
# Database: ✅ Running
# Production (ports 8000/3000): ❌ Stopped  
# Development (ports 8001/3002): ✅ Running
# 🔧 Development environment active
```

### 4. Development Process
```bash
# Make code changes (automatic hot reload)
# - Frontend changes: Instant HMR in browser
# - Backend changes: Auto-rebuild with Air

# View logs in real-time
make ai-pm-logs

# Switch modes as needed (database preserved)
make ai-pm-switch

# Stop services when done (database preserved for next session)
make ai-pm-stop
```

## API Endpoints Reference

Key development endpoints (full API documentation will be available via OpenAPI):

### Essential Endpoints
```bash
# Health check
GET http://localhost:8001/api/health

# Dashboard data
GET http://localhost:8001/api/dashboard

# Projects and tasks
GET http://localhost:8001/api/projects
GET http://localhost:8001/api/tasks
GET http://localhost:8001/api/tasks/deleted

# Quick test examples
curl http://localhost:8001/api/health
curl http://localhost:8001/api/dashboard | jq .
```

> **Note**: Comprehensive API documentation will be available via OpenAPI/Swagger UI at `/api/docs` (planned feature).

## Infrastructure Details

### Services
The development environment runs these services:
- **ai-tools-pm-database**: PostgreSQL database
- **ai-tools-pm-api-dev**: Go API with Air hot reloading
- **ai-tools-pm-ui-dev**: React UI with Vite HMR

### Data Persistence
- Database data: `./data/postgres/` (persisted between restarts)
- No cache services (Redis removed for simplicity)
- No file storage services (MinIO removed for simplicity)

### Docker Compose Profiles
```yaml
# Development services (AI_PM_MODE=dev)
services with profile: ["development", "dev"]

# Production services (default)
services with profile: ["production", "prod"]
```

## Troubleshooting

### Common Issues

#### Port Conflicts
```bash
# Check what's using ports
lsof -i :3002  # Frontend dev
lsof -i :8001  # API dev
lsof -i :5432  # Database

# Stop conflicting services
make ai-pm-stop
```

#### Container Issues
```bash
# Clean restart
make ai-pm-stop
docker system prune -f
AI_PM_MODE=dev make ai-pm-start

# Check container logs
docker logs ai-tools-pm-api-dev
docker logs ai-tools-pm-ui-dev
docker logs ai-tools-pm-database
```

#### Database Issues
```bash
# Reset database (WARNING: destroys data)
make ai-pm-stop
sudo rm -rf ai-pm/data/postgres
AI_PM_MODE=dev make ai-pm-start
```

#### Hot Reload Not Working
```bash
# Frontend: Check Vite config
# Backend: Check Air config in backend/.air.toml
# Verify volume mounts in docker-compose.yml

# Restart development services
make ai-pm-stop
AI_PM_MODE=dev make ai-pm-start
```

### Debugging Steps

1. **Check Service Status**:
   ```bash
   make ai-pm-status
   docker ps | grep ai-tools-pm
   ```

2. **Check Logs**:
   ```bash
   make ai-pm-logs
   # Or specific service:
   docker logs ai-tools-pm-api-dev
   ```

3. **Verify Network Connectivity**:
   ```bash
   curl http://localhost:8001/api/health
   curl -I http://localhost:3002
   ```

4. **Check File Mounts** (development mode):
   ```bash
   # Verify source code is mounted
   docker exec ai-tools-pm-api-dev ls -la /app
   docker exec ai-tools-pm-ui-dev ls -la /app/src
   ```

## CLI Integration

The CLI script works with both development and production modes:

```bash
# List tasks (works with any mode)
./scripts/project-manager.sh list-tasks

# Add task
./scripts/project-manager.sh add-task -p 1 -t "New Task" -r high

# Check API health
./scripts/project-manager.sh setup
```

## Development Best Practices

### Code Changes
- **Frontend**: Changes auto-refresh in browser (HMR)
- **Backend**: Changes auto-rebuild and restart (Air)
- **Database**: Schema changes require manual migration

### Testing Changes
```bash
# After making changes, verify:
curl http://localhost:8001/api/health
# Should return: {"service":"ai-project-manager","status":"healthy",...}

# Test frontend
open http://localhost:3002
# Should load without errors
```

### Performance
- Development mode prioritizes fast iteration over performance
- Use production mode for performance testing
- Database queries are not optimized for development

## Advanced Configuration

### Environment Variables
```bash
# Development mode uses these defaults:
AI_PM_DB_HOST=ai-pm-database
AI_PM_DB_PORT=5432
AI_PM_DB_USER=aipm
AI_PM_DB_PASSWORD=aipm123
AI_PM_DB_NAME=ai_project_manager

# Frontend API URL (development)
VITE_API_BASE_URL=http://localhost:8001/api
```

### Custom Docker Compose
For advanced use cases, you can override settings:
```bash
# Use custom compose file
docker-compose -f docker-compose.yml -f docker-compose.override.yml up
```

This setup provides a robust development environment optimized for rapid iteration and debugging.
