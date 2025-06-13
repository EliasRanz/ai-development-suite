# Project Management Instructions

## AI Project Manager System

This project uses a custom AI-driven project management system built on solid infrastructure components.

### Quick Start for AI Agents

**ALWAYS start your session by checking the current project status:**

```bash
# Check what's currently happening
./scripts/project-manager.sh list-projects
./scripts/project-manager.sh list-tasks

# Check infrastructure status
make ai-pm-status
```

### Core Commands

#### Project Management
```bash
# Add a new project
./scripts/project-manager.sh add-project "Project Name" "Description"

# List all projects
./scripts/project-manager.sh list-projects

# Add a task to a project
./scripts/project-manager.sh add-task <project_id> "Task Title" "Description" [priority]

# List tasks (all or by project)
./scripts/project-manager.sh list-tasks [project_id]

# Update task status
./scripts/project-manager.sh update-task <task_id> <status>

# Add notes/comments
./scripts/project-manager.sh add-note <project_id> <task_id> "Note content"
```

#### Infrastructure Management
```bash
# Start AI Project Manager
make ai-pm-start

# Check status
make ai-pm-status

# Stop services
make ai-pm-stop

# Initial setup (run once)
make ai-pm-setup
```

### Task Statuses
- `todo` - Not started
- `in_progress` - Currently being worked on
- `review` - Ready for review
- `done` - Completed

### Task Priorities
- `low` - Nice to have
- `medium` - Standard priority
- `high` - Important
- `urgent` - Critical

### Infrastructure Components

#### Working Services ✅
- **Database** (`ai-tools-pm-database`): PostgreSQL on port 5432
- **Cache** (`ai-tools-pm-cache`): Redis for caching
- **Storage** (`ai-tools-pm-storage`): MinIO on ports 9000 & 9090

#### Services with Platform Issues ⚠️
- **API** (`ai-tools-pm-api`): Backend API (platform compatibility issues)
- **Web** (`ai-tools-pm-web`): Web interface (platform compatibility issues)

### Access Points
- **Database**: Direct CLI access via `./scripts/project-manager.sh`
- **MinIO Console**: http://localhost:9090 (storage management)
- **Database Port**: localhost:5432 (direct SQL access)

### AI Agent Workflow

1. **Session Start**: Always check project status first
2. **Task Management**: Use CLI for all project tracking
3. **Progress Updates**: Update task status as you work
4. **Documentation**: Add notes for important decisions/progress
5. **ADRs**: Create ADRs for significant architectural decisions

### File Locations
- CLI Tool: `./scripts/project-manager.sh`
- Docker Compose: `./docker-compose.ai-pm.yml`
- Environment: `./.env` (AI_PM_* variables)
- ADRs: `./ADRs/` directory

### Integration with Development

The project management system integrates with:
- **Version Control**: Git for code changes
- **Documentation**: ADRs for decisions
- **Build System**: Makefile for automation
- **Development**: Wails for application development

### Security Notes
- Database credentials in `.env` file (not committed)
- MinIO storage with authentication
- Local development environment (not production-ready)

## Example Session

```bash
# Start session - check current state
./scripts/project-manager.sh list-tasks

# Work on a task
./scripts/project-manager.sh update-task 1 "in_progress"

# Add progress note
./scripts/project-manager.sh add-note 1 1 "Started implementing feature X"

# Complete task
./scripts/project-manager.sh update-task 1 "done"

# Add new task if needed
./scripts/project-manager.sh add-task 1 "Next Task" "Description" "medium"
```
