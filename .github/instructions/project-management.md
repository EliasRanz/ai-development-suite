# Project Management Instructions

## AI Project Manager System (Development Tool)

This project uses a custom AI-driven project management system designed exclusively for development use. This tool manages development of the AI tools launcher but is not included in the production application.

**For AI agent workflow and task principles, see `copilot-instructions.md`**

## Quick Start for AI Agents

**Before using any project management commands, ensure services are running.**

**See "Environment Selection Rules" section below to choose the appropriate startup mode.**

Once services are running:
```bash
# Check current tasks and projects
./scripts/project-manager.sh list-projects
./scripts/project-manager.sh list-tasks
```

## CLI Command Reference

### Get Help and Current Values
```bash
# Check available commands and syntax
./scripts/project-manager.sh help

# Get specific command help (shows current valid values)
./scripts/project-manager.sh update-task -h
./scripts/project-manager.sh add-task -h
```

### Task Lifecycle Commands

#### 1. Task Creation
```bash
# Check current state
./scripts/project-manager.sh list-tasks

# Create task for new work  
./scripts/project-manager.sh add-task -p [PROJECT_ID] -t "[TITLE]" -d "[DESCRIPTION]" -r [PRIORITY]

# Move to in-progress
./scripts/project-manager.sh update-task -i [TASK_ID] -s "in_progress"
```

#### 2. Task Updates
```bash
# Add progress notes
./scripts/project-manager.sh add-note -t [TASK_ID] -c "[PROGRESS_UPDATE]"

# Update status as needed
./scripts/project-manager.sh update-task -i [TASK_ID] -s [STATUS]
```

#### 3. Task Completion
```bash
# Mark complete
./scripts/project-manager.sh update-task -i [TASK_ID] -s "done"

# Add completion notes
./scripts/project-manager.sh add-note -t [TASK_ID] -c "Completed: [SUMMARY]"
```

## Status Values
Use the help command to get current valid status values:
```bash
./scripts/project-manager.sh update-task -h
```

## Priority Levels
Use the help command to get current valid priority values:
```bash
./scripts/project-manager.sh add-task -h
```

## Version Control vs Database Operations

**Database Operations (No commit needed):**
- Adding/updating tasks and notes
- Project management data operations
- Data persists automatically in PostgreSQL

**Source Code Changes (Commit required):**
- Modifying .go, .js, .ts, .py, .sh files
- Configuration changes
- Documentation updates
- Any file system modifications

**Rule**: Only commit when you modify files, not when you manage project data.

## Environment Selection Rules

**The project management system should ALWAYS be running for task tracking. The startup mode is automatically selected based on work context:**

### Unified Commands with Automatic Profile Selection

**All commands automatically choose the correct profile based on `AI_PM_MODE` environment variable:**

```bash
# For Project Management tool development (hot reload mode)
AI_PM_MODE=dev make ai-pm-start

# For all other development work (stable mode) - DEFAULT
make ai-pm-start
```

### Service Commands (Work with Both Modes)
```bash
# Start services (auto-selects development or production profile)
make ai-pm-start

# Check service status
make ai-pm-status

# View logs
make ai-pm-logs

# Stop services
make ai-pm-stop

# Restart services (maintains current mode)
make ai-pm-restart
```

### Access Points by Mode
- **Development Mode** (`AI_PM_MODE=dev`): Frontend at http://localhost:3002, API at http://localhost:8001 (hot reload)
- **Production Mode** (default): Frontend at http://localhost:3000, API at http://localhost:8000 (stable)

### Why This Approach Works
- **Single command set** - No more duplicate commands to remember
- **Automatic selection** - Environment variable determines the mode
- **Task tracking works in both modes** - Create/update tasks regardless of mode
- **Resource efficient** - Hot reload only when needed for PM tool development
- **Clear decision tree** - Set `AI_PM_MODE=dev` only when modifying PM tool code
