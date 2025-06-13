# AI Project Manager

A modern, AI-driven project management system designed for development workflows.

## Features

- ✅ Task and project tracking with soft delete
- 🔄 Workflow status management (todo, in_progress, validation, done, blocked)
- 🏷️ Task type classification (feature, bug, maintenance, research)
- 📊 Real-time dashboard and analytics
- 🔗 CLI integration for AI agents
- 🐳 Docker-based infrastructure

## Quick Start

```bash
# Setup the system
./scripts/setup.sh

# Use the CLI
./scripts/project-manager.sh list-tasks
```

## Architecture

- **Backend**: Go API service with PostgreSQL
- **Frontend**: React + TypeScript UI
- **Infrastructure**: Docker Compose with Redis caching
- **CLI**: Bash script for automation

See [documentation](docs/) for detailed information.
