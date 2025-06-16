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

### Service Commands (Intelligent Environment Management)

```bash
# Start services (auto-selects development or production profile)
# Automatically handles environment conflicts and preserves database
make ai-pm-start

# Check service status (shows both environments and database status)
make ai-pm-status

# Clean switch between environments (preserves database and data)
AI_PM_MODE=dev make ai-pm-switch    # Switch to development mode
make ai-pm-switch                   # Switch to production mode

# View logs from currently active environment
make ai-pm-logs

# Stop services (granular control, preserves database by default)
make ai-pm-stop          # Stop both environments, preserve database
make ai-pm-stop-prod     # Stop only production environment
make ai-pm-stop-dev      # Stop only development environment  
make ai-pm-stop-all      # ⚠️ Stop ALL including database (use with caution)

# Restart services (maintains current mode, preserves database)
make ai-pm-restart
```

### Database and Data Safety Features

**All environment operations preserve the database and your data by default:**

- ✅ **Database Preservation**: Database container runs continuously across mode switches
- ✅ **Zero Data Loss**: No risk of losing tasks, projects, or notes during switches
- ✅ **Fast Switching**: No database restart delays (saves 5-10 seconds per switch)
- ✅ **Conflict Resolution**: Automatically stops conflicting environments
- ⚠️ **Explicit Database Control**: Use `make ai-pm-stop-all` only when full shutdown needed

### Access Points by Mode
- **Development Mode** (`AI_PM_MODE=dev`): Frontend at http://localhost:3002, API at http://localhost:8001 (hot reload enabled)
- **Production Mode** (default): Frontend at http://localhost:3000, API at http://localhost:8000 (stable, optimized)

### Advanced Environment Management

**Smart Conflict Resolution:**
- Starting an environment automatically stops the conflicting one
- Database remains running and connected throughout all operations
- Clear status indicators show which environment is active (🔧 dev / 🏭 prod)
- Warning messages when both environments detected running simultaneously

**Environment Switching Examples:**
```bash
# Currently in production, switch to development for PM tool work
AI_PM_MODE=dev make ai-pm-switch
# ✅ Stops production containers, starts development containers, database preserved

# Return to production mode
make ai-pm-switch  
# ✅ Stops development containers, starts production containers, database preserved

# Check what's running
make ai-pm-status
# Shows: Database ✅, Production ❌/✅, Development ❌/✅, Active mode indicator
```

### Why This Approach Works
- **Single command set** - No more duplicate commands to remember
- **Automatic conflict resolution** - Environments never conflict or compete for resources
- **Database safety** - Zero risk of data loss during environment operations  
- **Fast operations** - No unnecessary database restarts (5-10 second time savings)
- **Clear decision tree** - Set `AI_PM_MODE=dev` only when modifying PM tool code
- **Visual feedback** - Status command shows exactly what's running with clear indicators
- **Granular control** - Stop specific environments without affecting others
- **Safe defaults** - Database preserved unless explicitly requested to stop
