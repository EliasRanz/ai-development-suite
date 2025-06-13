Security-first development with comprehensive input validation.

Code quality, maintainability, and extensible design patterns.

SOLID, DRY, KISS principles and API-first architecture.

⚠️ **CRITICAL**: Follow script management guidelines in `.github/instructions/script-management.md`
- NO duplicate scripts (no -v2, -enhanced, -new suffixes)
- Update existing scripts in place rather than creating new versions
- Check for existing functionality before adding new scripts

📋 **ENVIRONMENT**: Follow environment setup guidelines in `.github/instructions/environment-setup.md`
- Use single `.env.template` as the authoritative source
- Never create multiple root-level environment templates
- Document all environment variables with clear comments

Use project management CLI for task tracking: `./scripts/project-manager.sh list-tasks`
