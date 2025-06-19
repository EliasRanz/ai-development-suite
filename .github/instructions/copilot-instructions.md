# AI Agent Instructions

## Core Principles
1. **Security-first**: Validate all inputs, sanitize data, never commit secrets
2. **Code quality**: Follow all coding standards (see `coding-standards.md`) for maintainable, testable, and secure code
3. **API-first**: Design clear interfaces before implementation

## Required Actions at Session Start

### 1. Ask User About Work Context (FIRST)
Before starting any development, ALWAYS ask:
```
"What will you be working on today? 
- Project Management tool development (backend/frontend)
- AI Studio development 
- Other tools/scripts"
```
**STOP. Wait for user response before proceeding.**

### 2. Start Project Management System (SECOND)
**The project management system should always be running for task tracking**

Based on user's response, set the environment variable and start services:

- **For Project Management tool development**: `AI_PM_MODE=dev make ai-pm-start` 
- **For all other work**: `make ai-pm-start` (uses production mode by default)

**STOP. Wait for services to start before proceeding.**

### 3. Verify System Ready (THIRD)
Use tools to check that services are running and accessible.

**STOP. Confirm services are ready before proceeding.**

### 4. Script Management (CRITICAL)
- NEVER create duplicate scripts (no -v2, -enhanced, -new suffixes)
- UPDATE existing scripts in place
- CHECK for existing functionality before creating new scripts

### 5. Environment Configuration
- USE single `.env.template` as authoritative source
- NEVER create multiple root-level environment templates
- DOCUMENT all environment variables with clear comments

## Task Workflow (Per Development Task)
1. **CHECK** current tasks first using tools: `./scripts/project-manager.sh list-tasks`
2. **VERIFY** command syntax with `--help` before creating/updating tasks
3. **CREATE/UPDATE** tasks using only documented flags and options
4. **MOVE** task to appropriate status when starting using tools
5. **UPDATE** status as work progresses using tools
6. **COMMIT** with clear messages referencing task numbers

**For detailed CLI commands and examples, see `project-management.md`**

**COMMAND VERIFICATION EXAMPLES:**
```bash
# Verify command syntax FIRST
./scripts/project-manager.sh add-task --help
./scripts/project-manager.sh update-task --help

# THEN use only documented options
./scripts/project-manager.sh add-task -p 1 -t "Fix bug" -r high
./scripts/project-manager.sh update-task -i 42 -s done
./scripts/project-manager.sh list-tasks -p 1 -s todo
```

## Version Control Workflow (CRITICAL)

### Before Starting Any Work
1. **CHECK** git status to see uncommitted changes
2. **COMMIT** any pending work before starting new tasks
3. **CREATE** logical, focused commits during development

### During Development
1. **COMMIT FREQUENTLY** - Make atomic commits for logical changes
2. **GROUP LOGICALLY** - Related files should be committed together
3. **WRITE CLEAR MESSAGES** - Follow format: "type(scope): description [task #X]"

### Commit Message Format
```
type(scope): brief description [task #X]

Detailed explanation if needed:
- What was changed
- Why it was changed
- Impact of the change
```

**Types:** feat, fix, docs, refactor, test, chore, style
**Examples:**
- `feat(ai-pm): add hot reload development environment [task #26]`
- `docs(infrastructure): update setup guides after MinIO/Redis removal [task #43]`
- `refactor(makefile): clean up and organize AI tools targets [task #43]`
- `chore(docker): remove unused services and simplify compose files [task #43]`

### Logical Commit Grouping
1. **Infrastructure changes** (Docker, Makefile, scripts)
2. **Documentation updates** (README, ADRs, guides)
3. **Configuration changes** (environment, setup files)
4. **Code changes** (features, fixes, refactoring)

### After Completing Tasks
1. **REVIEW** all changes with `git status` and `git diff`
2. **STAGE** files logically with `git add`
3. **COMMIT** with descriptive messages
4. **PUSH** to remote repository

**Always ensure version control reflects the logical progression of work!**

## Tool Usage Guidelines
- **Always use tools** to run commands (`run_in_terminal` tool)
- **Never ask users** to run commands themselves
- **Use tools to check status** before assuming services are running

## Command Verification (CRITICAL)
- **ALWAYS check --help** before using any command with unfamiliar flags
- **NEVER assume flags exist** based on other tools or general conventions
- **VERIFY actual syntax** from the tool's own documentation
- **USE only documented options** - if a flag doesn't appear in --help, it doesn't exist
- **WHEN IN DOUBT, VERIFY** - always check help documentation rather than guessing

## Command Verification Workflow
**Before using any CLI command:**
1. **CHECK help first**: `command --help` or `command help`
2. **VERIFY flags exist**: Only use flags shown in help output
3. **TEST syntax**: Try with simple examples if uncertain
4. **DOCUMENT findings**: Note any differences from expected behavior

**Examples:**
```bash
# ALWAYS do this first
./scripts/project-manager.sh add-task --help
./scripts/project-manager.sh update-task --help
./scripts/project-manager.sh list-tasks --help
```

## Development Environment Setup

**For environment selection rules and detailed service management, see `project-management.md`**

## Related Documentation
- **Task Management**: `project-management.md` - Detailed CLI commands and service management
- **Coding Standards**: `coding-standards.md` - Comprehensive code quality, security, and workflow requirements
- **Development Setup**: `development.md` - Project structure and file organization
- **Environment Config**: `environment-setup.md` - Environment variable management
- **Script Management**: `script-management.md` - Script creation and maintenance guidelines
