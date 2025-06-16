# Architecture Decision Records (ADR) Guidelines

## Format Requirements
Document significant decisions as numbered ADRs: `001-decision-title.md`

## Required Sections
- **Status**: Proposed, Accepted, Deprecated, Superseded
- **Context**: What forces are at play? What problem are we solving?
- **Decision**: What architectural direction are we taking?
- **Consequences**: What trade-offs and impacts result from this decision?

## ADR Lifecycle
- ADRs are **immutable** once accepted
- Create new ADRs to supersede previous decisions
- Use clear numbering: `001-`, `002-`, etc.
- Reference related ADRs in the Context section

## When to Create ADRs
- Technology stack changes
- Major architectural patterns
- Security policy decisions
- Development process changes
- Tool selection decisions

## Integration with Project Management
When implementing ADR decisions, create tasks in the project management system to track progress.

**For task creation commands, see `project-management.md`**
