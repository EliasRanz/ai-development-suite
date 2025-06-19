# AI Agent Orchestration & Enforcement Instructions

All agents must act as orchestrators, enforcing and coordinating all internal standards. Reference and enforce:
- [coding-standards.md]
- [version-control.md]
- [environment-setup.md]
- [security.md], [security-sensitive-data.md]
- [script-management.md]
- [project-management.md]
- [context.md]

## Core Agentic Principles
1. **Security-first**: Validate all inputs, sanitize data, never commit secrets (see `security.md`)
2. **Code quality**: Enforce all coding standards for maintainable, testable, and secure code
3. **API-first**: Design clear interfaces before implementation
4. **Automation**: Minimize manual steps; use tools and scripts for all actions
5. **Context propagation**: Always document and share session context, rationale, and agent-to-agent notes (see `context.md`)

## Session Orchestration Workflow
1. **Gather Work Context**: Prompt user for project/task context at session start. Wait for response before proceeding.
2. **Start Project Management System**: Ensure task tracking is active. Start required services using authoritative commands (`make help`).
3. **Verify System Readiness**: Use tools to confirm all services are running and accessible before proceeding.
4. **Environment Setup**: Enforce use of `.env.template` and validate environment configuration (see `environment-setup.md`).
5. **Script Management**: Prevent script duplication, enforce updates in place, and check for existing functionality (see `script-management.md`).
6. **Task Workflow**: Use project management tools to check, create, update, and track tasks. Reference `project-management.md` for all commands and status updates.
7. **Version Control**: Enforce all version control standards, including commit/review workflow, atomic commits, rationale, and context references (see `version-control.md`).
8. **Command Verification**: Always verify command syntax with `--help` before use. Use only documented options. Never assume flags exist—verify from tool documentation.
9. **Tool Usage**: Always use tools to run commands and check status. Never ask users to run commands manually.
10. **Compliance Checks**: Regularly validate compliance with all standards. Use automated scripts and CI/CD checks where possible.

## Error Handling & Escalation
- Agents must document and escalate blockers, ambiguous requirements, or compliance failures in the session context and notify responsible parties.
- All unresolved issues should be logged in the project management system for visibility and follow-up.

## Session Logging & Traceability
- Agents must log key decisions, context changes, and workflow transitions in a session log or project management tool.
- Ensure all actions are traceable and auditable for future reference.

## Continuous Improvement Loop
- Agents must participate in periodic reviews of orchestration processes and propose improvements to standards and workflows.
- Document all improvement proposals and outcomes in the session context or project management system.

## Onboarding Checklist (for New Agents)
- Ensure access to all required tools, repositories, and documentation.
- Review all instruction files and standards.
- Set up environment and validate configuration using onboarding scripts.
- Confirm ability to run, validate, and document workflows as described above.

## Glossary
- **Session Context**: The current state, rationale, and notes relevant to the agent’s work, shared across tasks and agents.
- **Agent-to-Agent Transfer**: The process of passing context, rationale, or tasks between agents, documented in session context and PRs.
- **Compliance Check**: Automated or manual validation that all standards and workflows are being followed.

## Agent-to-Agent Collaboration
- Document all context transfers, rationale, and decisions in session context and PRs.
- Share relevant notes for downstream agents and future sessions.
- Reference `context.md` for context sharing protocols.

## Commit & PR Standards
- All commits and PRs must reference relevant tasks, session context, and rationale.
- Follow Conventional Commits and logical grouping (see `version-control.md`).
- Review, stage, and commit changes as described in the commit & review workflow.

## Enforcement & Automation
- Use onboarding and compliance scripts to enforce environment, version control, and security standards.
- Integrate bots or hooks for context validation, commit message checks, and compliance reporting.
- Propose improvements to standards as part of regular retrospectives.

## Related Documentation
- All agents must cross-reference and enforce the latest standards in all work.
- For authoritative commands and workflows, always use `make help` and reference the relevant instruction files.

---
This file is the single source of truth for orchestrating agentic workflows, enforcing standards, and ensuring reproducibility, security, and compliance across all development activities.
