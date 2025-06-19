# Architecture Decision Records (ADR) Guidelines

## 1. Purpose & Scope
- ADRs document all significant architectural, technical, or process decisions for traceability and future reference.
- All agents and contributors must follow these guidelines for any decision affecting architecture, security, workflow, or major dependencies.

## 2. Format Requirements
- Use numbered files: `001-decision-title.md`, `002-another-decision.md`, etc.
- Each ADR must include:
  - **Status**: Proposed, Accepted, Deprecated, Superseded
  - **Context**: What forces are at play? What problem are we solving?
  - **Decision**: What architectural or process direction are we taking?
  - **Consequences**: What trade-offs and impacts result from this decision?
  - **Rationale**: Why are we making this decision? What are the expected benefits? Reference best practices, standards, or similar solutions.
  - **References**: Links to relevant documentation, industry resources, or code examples. Cross-reference related ADRs, `architecture.md`, `coding-standards.md`, and `context.md` as appropriate. Always include supporting documentation, articles, or resources that help explain or justify the decision, to encourage learning and knowledge sharing.

## 2a. ADR Template (Copy & Use)
```markdown
# ADR-XXX: Title

- **Status:** Proposed | Accepted | Deprecated | Superseded
- **Date:** YYYY-MM-DD
- **Deciders:** Names or roles
- **Supersedes:** (if any)
- **Tags:** #architecture #security #process (optional)

## Context
_What problem are we solving? What forces are at play?_

## Decision
_What architectural or process direction are we taking?_

## Consequences
_What trade-offs and impacts result from this decision?_

## Rationale
_Why are we making this decision? Reference best practices, standards, or similar solutions._

## References
- Links to documentation, code, related ADRs, PRs, or issues

```

## 3. ADR Lifecycle & Maintenance
- ADRs are **immutable** once accepted. Never edit accepted ADRs—supersede with a new ADR if changes are needed, and always reference the superseding ADR in both documents.
- Use clear numbering: `001-`, `002-`, etc.
- Reference related ADRs in the Context or References section.
- Regularly review ADRs for relevance and update project documentation to reflect accepted decisions.

## 4. When to Create ADRs
- Technology stack changes
- Major architectural patterns or refactors
- Security policy decisions
- Development process or workflow changes
- Tool selection or deprecation
- Any decision with long-term impact or affecting public contracts/APIs

## 4a. Review & Approval
- ADRs should be reviewed and discussed by relevant agents and users. Acceptance requires consensus or explicit approval by project leads or designated reviewers.

## 4b. Linking to Implementation
- Link ADRs to related pull requests, issues, or implementation tasks for traceability and context.

## 5. Integration with Project Management
- When implementing ADR decisions, create and track tasks in the project management system.
- For task creation commands, see `project-management.md`.

## 6. Agentic & Continuous Improvement Practices
- Agents and contributors should propose ADRs collaboratively, justify all decisions, and document rationale with references.
- Regularly review and improve ADR practices for clarity, enforceability, and alignment with project standards.

---

For more details, see:
- `architecture.md` — Architecture and design standards
- `coding-standards.md` — Code quality, security, and workflow
- `context.md` — Project context and workflow
- Example ADR: `ADRs/002-project-structure-architecture.md` — Use as a template for new decisions
