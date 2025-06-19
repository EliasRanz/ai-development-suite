# Script Management Guidelines

All agents must follow these guidelines to prevent bloat, maintain clean tooling, and ensure traceability. Reference: [coding-standards.md], [testing.md], [project-management.md], [environment-setup.md], [security.md], [copilot-instructions.md].

## Overview
This document establishes guidelines for managing scripts in the AI Development Suite to prevent bloat and maintain clean, organized tooling.

## Current Script Inventory

### Active Scripts (DO NOT DUPLICATE)
- `scripts/project-manager.sh` - **PRIMARY** project management CLI (see `project-management.md`)
- `scripts/security-monitor.sh` - **PRIMARY** security monitoring and task creation
- `ai-pm/scripts/setup.sh` - AI PM service setup
- `ai-pm/scripts/backup.sh` - Database backup utility  
- `ai-pm/scripts/restore.sh` - Database restore utility

**Before creating any new script, check this inventory and consider enhancing existing scripts.**

### Script Locations
- **Root `/scripts/`** - Global utility scripts used across the entire monorepo
- **Service-specific `/service/scripts/`** - Scripts specific to individual services (ai-pm, ai-studio, etc.)

## Guidelines

### 1. No Duplicate Scripts
- **Never create multiple versions** of the same script (e.g., `-v2`, `-new`, `-enhanced` suffixes)
- **Update in place** rather than creating new versions
- **Use git history** for version tracking, not filename versioning

### 2. Script Naming Convention
- Use descriptive, kebab-case names: `script-name.sh`
- No version suffixes: ❌ `script-v2.sh`, ✅ `script.sh`
- No duplicate functionality: ❌ `script-simple.sh` + `script-enhanced.sh`

### 3. Before Adding New Scripts
1. **Check existing scripts** - Does this functionality already exist?
2. **Review current inventory** - See the Active Scripts list above
3. **Consider enhancement** - Can we improve an existing script instead?
4. **Follow coding standards** - See `coding-standards.md` for comprehensive code quality, security, and workflow requirements
5. **Document purpose** - Add clear comments explaining what the script does
6. **Single responsibility** - Each script should have one clear purpose

### 4. Script Organization
```
scripts/                    # Global utilities
├── project-manager.sh      # Main project management CLI
├── security-monitor.sh     # Security monitoring
└── other-global-tools.sh

service/scripts/            # Service-specific scripts  
├── setup.sh               # Service setup
├── backup.sh              # Service backup
└── service-specific.sh    # Other service tools
```

### 5. Documentation Requirements
- **Header comment** explaining purpose and usage
- **Dependencies** clearly stated
- **Examples** in usage comments
- **Update documentation** when modifying scripts

### 6. Cleanup Process
When cleaning up script bloat:
1. Identify the **canonical version** (usually the one referenced in docs)
2. **Merge useful features** from duplicates into the canonical version
3. **Update all references** to point to the canonical version
4. **Remove duplicates** and commit with clear message
5. **Update documentation** to reflect changes

## Additional Best Practices

- **Shebang and Executable Permissions:**
  - All scripts must start with the appropriate shebang (e.g., `#!/bin/bash`).
  - Set executable permissions (`chmod +x script.sh`) for all scripts.
- **Shellcheck and Linting:**
  - Run `shellcheck` or equivalent linters on all shell scripts to catch errors and enforce style.
- **Error Handling and Exit Codes:**
  - Use robust error handling (e.g., `set -euo pipefail` for bash).
  - Scripts must return meaningful exit codes.
- **Logging and Output:**
  - Standardize logging/output format, including timestamps and log levels if appropriate.
- **Parameter Validation:**
  - Validate all input parameters and provide clear usage/help messages.
- **Input Handling:**
  - Scripts must support multi-line strings, special characters, and whitespace in input parameters where applicable.
  - Validate and properly escape or quote all user input to prevent errors and security issues.
- **Script Versioning (in comments):**
  - Track major changes in header comments, not filenames.
- **Script Dependency Management:**
  - Document and check for required dependencies at the start of each script.
  - When adding a new dependency, update the relevant setup script to validate its installation or install it automatically.

## Anti-Patterns to Avoid
- ❌ Creating `-v2` or `-new` versions instead of updating original
- ❌ Keeping "backup" versions of scripts in the repo
- ❌ Having multiple scripts that do similar things
- ❌ Scripts in multiple locations doing the same job
- ❌ Undocumented or poorly named scripts

## Recovery from Script Bloat
If we find ourselves with duplicate scripts again:
1. **Stop** - Don't add more scripts until cleanup is complete
2. **Inventory** - List all scripts and their purposes
3. **Identify canonical versions** - Which ones are actually being used?
4. **Consolidate** - Merge functionality into canonical versions
5. **Remove duplicates** - Clean up the excess
6. **Update documentation** - Ensure all references are correct

## Examples

### ✅ Good Script Management
```bash
# Adding new functionality to existing script
scripts/project-manager.sh add-task --priority high "New task"

# Enhancing existing script with new flags
scripts/security-monitor.sh --verbose --dry-run
```

### ❌ Bad Script Management  
```bash
# Creating duplicates instead of updating
scripts/project-manager.sh
scripts/project-manager-enhanced.sh
scripts/project-manager-v2.sh
scripts/project-manager-simple.sh
```

## Lessons Learned
- **Data loss incident**: Duplicate scripts led to confusion about which version to use, contributing to operational errors
- **Maintenance burden**: Multiple versions mean multiple places to update when changes are needed
- **Developer confusion**: Team members unsure which script is the "right" one to use

## Regular Maintenance
- **Monthly audit** of script directory
- **Remove unused scripts** promptly
- **Consolidate similar functionality** before it becomes bloat
- **Update this document** when adding new categories of scripts

## Integration with Development Workflow

### Task Tracking for Script Changes
When modifying or creating scripts, create a task in the project management system. See [project-management.md] for task creation and tracking commands.

### Security Considerations
Scripts often handle sensitive data and system operations. See [coding-standards.md] and [security.md] for security and quality requirements.

### Testing Script Changes
All scripts should be tested before deployment. See [testing.md] for script testing requirements.

### Environment Setup
Scripts may depend on environment configuration. See [environment-setup.md] for standardized environment setup.

### Orchestration & Enforcement
Agents must enforce these script management standards as part of the overall workflow. See [copilot-instructions.md] for orchestration and enforcement requirements.

## Related Documentation
- **Project Management**: [project-management.md]
- **Coding Standards**: [coding-standards.md]
- **Testing**: [testing.md]
- **Environment Setup**: [environment-setup.md]
- **Repository Structure**: [../../REPOSITORY_STRUCTURE.md]
- **Contributing Guidelines**: [../../CONTRIBUTING.md]

---
All script changes must be reviewed, tested, and documented according to these standards and cross-referenced with the latest project requirements.
