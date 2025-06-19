# Security Standards for Agentic Workflows

All agents must enforce security at every stage of development and automation. Reference: [coding-standards.md], [environment-setup.md], [version-control.md], [security-sensitive-data.md], [copilot-instructions.md].

## Core Security Principles
- **Security-First**: All code and workflows must prioritize security, quality, and compliance.
- **Automation**: Use automated tools and scripts for validation, scanning, and reporting wherever possible.
- **Context & Traceability**: Document all security decisions, incidents, and escalations in the session context and project management system.

## Agent Security Responsibilities
1. **Input Validation**: Use centralized, approved validation utilities for all user and system inputs (see `coding-standards.md`).
2. **No Hardcoded Secrets**: Store all credentials in `.env` files; never commit secrets or credentials to version control.
3. **Path Security**: Validate and sanitize all file paths to prevent traversal and injection attacks.
4. **SQL Injection Prevention**: Use parameterized queries and ORM best practices for all database access.
5. **Error Handling**: Never expose sensitive information in error messages or logs.
6. **Dependency Security**: Run automated dependency checks (e.g., `go mod verify`, `npm audit`) before deployment and on a regular schedule.
7. **Environment Security**: Enforce strict file permissions, security headers, and production-only secrets in production environments.

## Automated Security Checks
- Integrate dependency scanning, static analysis, and secret detection into CI/CD pipelines.
- Use scripts to validate environment files for missing or weak secrets.
- Agents must address all security warnings and document actions taken in the session context.

## Security Review & Escalation
- Use the Security Review Checklist before merging or deploying:
  - [ ] All inputs validated using utility functions
  - [ ] No hardcoded credentials or secrets
  - [ ] Parameterized database queries
  - [ ] Error messages do not leak sensitive data
  - [ ] Security headers implemented for HTTP responses
- Escalate unresolved security issues or ambiguous requirements in the session context and notify responsible parties.
- Log all incidents and decisions for traceability.

## Incident Response Protocol
- In the event of a suspected or confirmed security incident, agents must:
  1. Immediately escalate the issue in the session context and notify responsible parties.
  2. Log all relevant details, actions taken, and outcomes in the project management system for internal review and traceability.
  3. Do not disclose incident details externally; follow internal documentation and escalation procedures.

## Security Metrics & Reporting
- Agents must regularly report security metrics (e.g., vulnerabilities found, time to resolution) as part of periodic audits.
- Use automated tools to generate and track these metrics where possible.

## Third-Party Service Security
- Before integrating any third-party service, API, or dependency, agents must:
  - Review and validate its security posture.
  - Document the review and approval in the session context and project management system.
  - Monitor for new vulnerabilities and update as needed.

## Glossary
- **Incident**: Any event that may compromise the confidentiality, integrity, or availability of systems or data.
- **Escalation**: The process of raising an issue to responsible parties for further investigation or action.
- **Session Context**: The current state, rationale, and notes relevant to the agent’s work, shared across tasks and agents.

## Continuous Improvement
- Agents must participate in periodic security reviews and propose improvements to standards and automation.
- Update documentation and onboarding as new threats or best practices emerge.

---
For detailed implementation examples and requirements, see `coding-standards.md` and related standards. Security is a shared, continuous responsibility for all agents.
