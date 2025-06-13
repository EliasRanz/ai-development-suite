# Project Management Instructions

## AI Project Manager System (Development Tool)

This project uses a custom AI-driven project management system **designed exclusively for development use**. This tool helps manage the development of the AI tools launcher but is not included in the production application.

**Key Principle**: This is a development-only tool that runs independently alongside your main application development.

### Quick Start for AI Agents

**ALWAYS start your session by ensuring the AI Project Manager is running:**

```bash
# FIRST: Start the AI Project Manager services (required)
make ai-pm-start

# Wait for services to be ready, then check status
make ai-pm-status

# Now check what's currently happening
./scripts/project-manager.sh list-projects
./scripts/project-manager.sh list-tasks
```

**Note**: The AI Project Manager services must be running before you can use any project management commands. If services aren't running, all project management commands will fail.

## 🚨 MANDATORY AI Agent Workflow 🚨

**ALL AI agents MUST follow this workflow for any implementation work:**

### 1. Pre-Implementation Requirements

**Before starting ANY development work:**

1. **Create/Update Tasks**: Always create tasks in the project management system BEFORE starting work
2. **Present Clear Plan**: Provide a detailed implementation plan with:
   - Clear objective and scope
   - Breakdown of components/features to implement
   - Time estimates
   - Implementation approach
   - Questions for shared decisions
3. **Get Agreement**: Wait for user agreement on the plan before proceeding
4. **Track Progress**: Update task status as work progresses

### 2. Enforcement Rules

- **No work without tasks**: Every implementation effort must be tracked as a task
- **No implementation without approval**: Never proceed without explicit user agreement
- **Always update status**: Keep task management current throughout development
- **Document decisions**: Add notes to tasks explaining implementation choices

### 3. Task Management Standards

```bash
# Always check current state first
./scripts/project-manager.sh list-tasks

# Create tasks for new work
./scripts/project-manager.sh add-task [project_id] "[title]" "[description]" "[status]" "[priority]"

# Update progress
./scripts/project-manager.sh update-task [task_id] "[new_status]"
```

### 4. Implementation Planning Template

When proposing new work, use this structure:

```markdown
## Implementation Plan: [Feature Name]

### Current State
- ✅ **Completed**: [What's already done]
- 🔄 **In Progress**: [Current active work]

### Next Phase: [Phase Name]
**Objective**: [Clear goal]
**Components**: [List of what will be built]
**Features**: [Specific functionality]
**Questions for Decision**: [Options requiring user input]
**Task Updates**: [How work will be tracked]
```

### 5. Communication Standards

- **Be explicit**: Don't assume understanding
- **Ask questions**: When multiple approaches are possible  
- **Wait for approval**: Never proceed without clear agreement
- **Update proactively**: Keep project management current

## 🏷️ Task Type Classification

### Task Types & When to Use

**🚀 feature**: New functionality or capabilities
- Adding new API endpoints
- Implementing new UI components
- Creating new user workflows

**🐛 bug**: Defects, errors, or broken functionality  
- API returning wrong data
- UI not displaying correctly
- CLI commands failing
- Live updating broken

**⚡ enhancement**: Improvements to existing features
- Performance optimizations
- Better user experience
- Additional options/configuration

**🔧 technical_debt**: Code quality and maintenance
- Refactoring monolithic files
- Improving error handling
- Adding proper logging
- Database optimization

**📚 documentation**: Documentation and instructions
- Updating README files
- API documentation
- Development guidelines
- User guides

**🛠️ maintenance**: Routine maintenance and housekeeping
- Dependency updates
- Configuration changes
- Environment setup
- Cleanup tasks

### Task Type Guidelines

```bash
# Create tasks with types
./scripts/project-manager.sh add-task 1 "Fix broken live updating" "Description..." high bug
./scripts/project-manager.sh add-task 1 "Add new API endpoint" "Description..." medium feature
./scripts/project-manager.sh add-task 1 "Refactor main.go file" "Description..." high technical_debt
```

### Priority Guidelines by Type

**Bugs**: Usually high priority, especially if blocking other work
**Features**: Priority based on user value and roadmap
**Technical Debt**: Medium priority, but schedule regularly
**Enhancements**: Lower priority unless significantly improves workflow
**Documentation**: Medium priority, important for maintainability
**Maintenance**: Schedule proactively, don't let accumulate

## 🔄 Task Workflow & Collaborative Review Process

### Status Definitions

**todo** → **in_progress** → **validation** → **done**

#### Core Workflow
- **todo**: Task is planned but not started
- **in_progress**: Active development work (AI-assisted implementation)
- **validation**: Collaborative review, testing, and refinement
- **done**: Complete, tested, reviewed, and approved

#### Additional Statuses
- **blocked**: Waiting for external dependency or decision
- **needs_discussion**: Requires architectural or approach decisions before proceeding
- **refactoring**: Code improvement work without new features

### Validation Stage Requirements

**All tasks entering validation must include:**
1. ✅ **Functionality Testing**: Feature works as specified
2. ✅ **Integration Testing**: Works with existing system
3. ✅ **Error Handling**: Graceful failures with helpful messages
4. ✅ **Documentation**: Instructions/comments updated
5. ✅ **Code Quality**: Clean, readable, maintainable code

### Collaborative Review Process

**When moving to validation:**
```bash
# Move task to validation and add review notes
./scripts/project-manager.sh update-task <id> validation
./scripts/project-manager.sh edit-task <id> --description "Original description + 

REVIEW NOTES:
- Functionality: [tested scenarios]
- Integration: [compatibility verified]
- Error handling: [edge cases covered]
- Questions: [what could be improved?]
- Alternatives: [other approaches considered?]"
```

**Review Discussion Points:**
- **Alternative Approaches**: Could this be implemented differently?
- **Performance**: Are there efficiency improvements?
- **Maintainability**: Will this be easy to modify later?
- **Reusability**: Can patterns/code be reused elsewhere?
- **Architecture**: Does this fit well with overall system design?

**Moving to Done:**
Only after collaborative discussion and any agreed improvements are implemented.

### Workflow Guidelines

**For Small Tasks** (< 2 hours):
- May skip validation if self-contained and low-risk
- Use judgment: simple bug fixes vs. architectural changes

**For Medium/Large Tasks** (> 2 hours):
- Always use validation stage
- Document review findings in task description
- Discuss improvement opportunities

**For Architecture/Design Tasks**:
- Use "needs_discussion" status early
- Get alignment before implementation
- Extra thorough validation

## 🛑 Session Shutdown Procedure

**ALWAYS follow this procedure when ending a development session:**

### 1. Update Task Status
```bash
# Update any tasks that were completed or progressed
./scripts/project-manager.sh update-task [task_id] "[new_status]"

# Check final status
./scripts/project-manager.sh list-tasks
```

### 2. Verify Board Accuracy
- Ensure all completed work is marked as "done"
- Update any tasks that progressed during the session
- Add any new tasks discovered during development

### 3. Clean Shutdown Services
```bash
# Stop development UI server (if running)
# Press Ctrl+C in terminal running `make ai-pm-dev-ui`

# Stop all AI Project Manager services
make ai-pm-stop
```

### 4. Session Summary
Before signing off, provide:
- **Completed Work**: What was accomplished
- **Updated Tasks**: Which tasks changed status
- **Next Steps**: What should be prioritized next
- **Issues Found**: Any problems discovered that need tasks

### 5. Verification
```bash
# Verify clean shutdown
docker ps | grep ai-tools
# Should return no results

# Data safety check - volumes remain
docker volume ls | grep ai-tools
# Should show persistent volumes for data safety
```

**Note**: All project data is safely stored in Docker volumes and will persist between sessions.

## 🔄 Session Restart Procedure

**When starting a new session:**

```bash
# STEP 1: Start AI Project Manager services (REQUIRED FIRST)
make ai-pm-start

# STEP 2: Wait for services to initialize, then check status
make ai-pm-status

# STEP 3: Review current work
./scripts/project-manager.sh list-tasks
./scripts/project-manager.sh list-projects
```

**Important**: Always start the AI Project Manager services first. Without these running, you cannot access project data or use project management commands.

## 🔧 Troubleshooting

### Docker Issues

If you get "docker command not found" or connection errors:

```bash
# Check if Docker Desktop is running
docker ps
# If this fails, start Docker Desktop first

# On WSL, ensure Docker integration is enabled
# In Docker Desktop: Settings > Resources > WSL Integration
```

### AI Project Manager Won't Start

If `make ai-pm-start` fails:

```bash
# Check Docker is running
docker ps

# Check for port conflicts
docker compose -f docker-compose.ai-pm.yml ps

# View logs for debugging
make ai-pm-logs

# Clean restart if needed
make ai-pm-stop
make ai-pm-start
```

### Services Not Auto-Starting

The AI Project Manager services will auto-start with Docker Desktop **only after** they've been started at least once with `make ai-pm-start`. The `restart: unless-stopped` policy requires existing containers.

**Important Notes:**
- **All project management commands require the AI Project Manager services to be running**
- **Always run `make ai-pm-start` at the beginning of each development session**
- **Services will auto-restart with Docker Desktop after the first manual start**

## 📝 Version Control vs Database Operations

### Critical Distinction: Code vs Data

**Understanding what requires Git commits vs what doesn't:**

### ❌ **DO NOT COMMIT** - Database Operations
These operations persist automatically in the database and do NOT require version control:

```bash
# Task Management (data operations)
./scripts/project-manager.sh add-task [...]
./scripts/project-manager.sh update-task [...]
./scripts/project-manager.sh delete-task [...]

# Note Management (data operations)  
./scripts/project-manager.sh add-note [...]
./scripts/project-manager.sh list-notes [...]
./scripts/project-manager.sh delete-note [...]

# Project Management (data operations)
./scripts/project-manager.sh add-project [...]
./scripts/project-manager.sh update-project [...]
./scripts/project-manager.sh delete-project [...]
```

**Why no commit needed:**
- Data persists automatically in PostgreSQL database
- Database operations are backed up through database mechanisms
- Committing these would create unnecessary noise in git history
- Project management data ≠ source code changes

### ✅ **DO COMMIT** - Source Code Changes
These modifications require Git commits:

```bash
# Code file modifications
- *.go, *.js, *.ts, *.py, *.sh files
- Configuration files (docker-compose.yml, package.json, etc.)
- Documentation files (*.md, *.txt)
- Environment files (.env.example)
- CI/CD configurations (.github/*)

# Examples of when to commit:
git add ai-pm/backend/main.go          # Modified Go source code
git add scripts/project-manager.sh     # Updated CLI script
git add README.md                      # Documentation updates
git add docker-compose.yml             # Configuration changes
```

**Why commit needed:**
- Source code needs version control for collaboration
- Enables rollbacks, change tracking, and code reviews
- Required for deploying changes to production
- Essential for maintaining project history

### 🔍 **Quick Decision Guide**

**Ask yourself:**
- "Am I modifying a file in the filesystem?" → **Commit required**
- "Am I adding/updating project data through the CLI?" → **No commit needed**

**Examples:**
- ❌ Adding task #15 about refactoring main.go → **No commit** (data operation)
- ✅ Actually refactoring main.go file → **Commit required** (code change)
- ❌ Adding notes to tasks → **No commit** (data operation)  
- ✅ Adding notes field to Task struct → **Commit required** (code change)
- ❌ Creating new projects in the PM system → **No commit** (data operation)
- ✅ Creating new project directories/files → **Commit required** (code change)

### 💡 **Best Practices**

1. **Separate concerns**: Keep project management data operations separate from code changes
2. **Clean git history**: Only commit actual file modifications
3. **Database persistence**: Trust the database to maintain project data
4. **Focus commits**: Each commit should represent a logical code change
5. **Clear boundaries**: Database operations ≠ File system operations

**Remember**: The AI Project Manager is a tool that manages data independently from your source code. Use it freely without worrying about Git - only commit when you're actually changing files.
