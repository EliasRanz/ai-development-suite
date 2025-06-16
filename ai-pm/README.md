# AI Project Manager

A modern, AI-driven project management system designed for development workflows.

> **🤖 AI-Assisted Development**: This project management system is built using human-AI collaboration, demonstrating modern AI-assisted development practices.

## Features

- ✅ Task and project tracking with soft delete
- 🔄 Workflow status management (todo, in_progress, validation, done, blocked)
- 🏷️ Task type classification (feature, bug, maintenance, research)
- 📊 Real-time dashboard and analytics
- 🔗 CLI integration for AI agents
- 🐳 Docker-based infrastructure

## Quick Start

### Development Setup (Recommended)
```bash
# Start development environment with hot reloading
AI_PM_MODE=dev make ai-pm-start

# Access the application
# - Frontend: http://localhost:3002 (hot reload)
# - API: http://localhost:8001/api (hot reload)
```

### Production Setup
```bash
# Start production environment
make ai-pm-start

# Access the application  
# - Frontend: http://localhost:3000
# - API: http://localhost:8000/api
```

### Environment Management
```bash
# Check what's running (shows both dev and prod status)
make ai-pm-status

# Switch between environments (preserves database and data)
AI_PM_MODE=dev make ai-pm-switch    # Switch to development
make ai-pm-switch                   # Switch to production

# Stop environments (database preserved by default)
make ai-pm-stop-dev                 # Stop development only
make ai-pm-stop-prod                # Stop production only  
make ai-pm-stop                     # Stop both environments
```

### CLI Usage
```bash
# Use the project management CLI
./scripts/project-manager.sh list-tasks
./scripts/project-manager.sh add-task -p 1 -t "New Task" -r high
```

## Architecture

- **Backend**: Go API service with PostgreSQL
- **Frontend**: React + TypeScript UI
- **Infrastructure**: Docker Compose with PostgreSQL database
- **CLI**: Bash script for automation

See [documentation](docs/) for detailed information:

- **[Development Setup](docs/DEVELOPMENT_SETUP.md)** - Complete development environment guide
- **[Data Management](DATA_MANAGEMENT.md)** - Backup and data persistence guide
- **API Documentation** - Will be automatically generated via OpenAPI/Swagger (planned)
