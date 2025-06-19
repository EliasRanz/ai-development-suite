# Environment Setup Standards for Agentic Workflows

All agents must follow these standards to ensure reproducible, secure, and maintainable environments. Reference: [security.md], [script-management.md], [context.md].

## Authoritative Templates
- Use `.env.template` as the single source of truth for all environment variables.
- Service-specific `.env.example` files are allowed only within their respective directories and must be documented.
- Never create multiple root-level templates.

## Agentic Setup Process
1. **Automated Initialization**
   - Use onboarding scripts to copy `.env.template` to `.env` and service-specific examples as needed.
   - Agents must not manually edit or create environment files unless automation is unavailable.
2. **Customization**
   - Agents must update all required secrets, passwords, and tokens with secure, unique values.
   - Use `openssl rand -base64 32` or equivalent for secret generation.
   - All changes must be documented in the agent session context and, if relevant, in PRs.
3. **Validation**
   - Use scripts to validate that `.env` files are ignored by git and contain no sensitive defaults.
   - Run `git status` and `git check-ignore .env` as part of automated checks.
   - Agents are responsible for ensuring no sensitive data is committed.

## Best Practices for Agents
- Document all environment variables with clear comments and logical grouping.
- Use descriptive, consistent variable names and secure placeholder values.
- Validate environment setup before running any scripts or services.
- Reference `make help` for authoritative setup and validation commands.

## Anti-Patterns & Enforcement
- Never commit actual `.env` files or sensitive data.
- Never use weak or default passwords in production.
- Never create redundant or undocumented templates.
- Automated compliance scripts should audit for these anti-patterns regularly.

## Maintenance & Auditing
- Add or remove variables only through `.env.template` and update documentation.
- Agents must review environment templates quarterly for security and relevance.
- Use automated tools to check for unused or obsolete variables.

## Integration & Automation
- All scripts (see `script-management.md`) must source environment variables and validate required settings before execution.
- Docker Compose and other tools must use `.env` and support overrides for service-specific needs.
- CI/CD pipelines should validate environment configuration and block non-compliant changes.

---
This standard ensures all agents can reliably set up, validate, and maintain secure environments with minimal manual intervention, supporting automation, reproducibility, and compliance across the AI tools suite.
