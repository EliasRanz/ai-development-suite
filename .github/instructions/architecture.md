# Architecture Standards for Agentic Development

## 1. Core Architectural Principles (Language-Agnostic)
- **Modularity:** Design systems as independent, loosely coupled modules.
- **Separation of Concerns:** Each component or layer should have a single, well-defined responsibility.
- **Scalability:** Architect for growth in users, data, and features.
- **Maintainability:** Favor clear, simple designs that are easy to test, refactor, and extend.
- **Extensibility:** Use interfaces and abstractions to support new features and integrations.
- **Performance:** Meet or exceed business targets (e.g., 4x faster than Python baseline).
- **Security:** Incorporate security best practices at every layer.
- **Cross-Platform:** Design for deployment on all supported platforms (Windows, macOS, Linux).
- **AI Agent Discoverability:** Structure and document code so that both humans and AI agents can easily locate, understand, and extend functionality.

## 1a. Architecture Validation Criteria
- No circular dependencies between layers
- Domain layer has no external imports
- All external dependencies injected via interfaces
- Clear separation between business logic and infrastructure
- Each package has a single responsibility
- Interfaces are small and focused
- High test coverage in each layer
- No code duplication across domains
- New features can be added without modifying existing code
- Clear documentation for each domain

## 2. Project-Specific Stack & Patterns
- **Backend:** Go/Wails
- **Frontend:** React TypeScript
- **Architecture Pattern:** Clean Architecture (see below)

### Clean Architecture Layer Structure
```
Frontend (React/TS)
    ↓
Application Layer (Use cases, services)
    ↓
Domain Layer (Business logic, entities)
    ↓
Infrastructure Layer (Database, external APIs)
```

## 3. Implementation Rules
- Use feature flags for all work-in-progress or experimental features.
- Maintain strict separation of concerns between layers.
- Create adapters for new model types and integrations.
- Use interfaces for extensibility and testability.
- Document all significant architectural and API design decisions in ADRs (`ADRs/` directory), including:
  - Adding, changing, or exposing new API endpoints, components, or interfaces
  - Major changes to authentication, versioning, or data models
  - Any decision that affects public contracts or integrations
- Agents should always consider the API as a first-class concern—design for clarity, consistency, and extensibility, and document rationale for all API-related changes.
- Document all significant architectural decisions in ADRs (`ADRs/` directory).
- All recommendations and changes must be documented with clear rationale and references to best practices, standards, or similar solutions. Include links and supporting materials in ADRs, PRs, or task comments as appropriate.

## 4. Agentic & Collaborative Best Practices
- Propose and justify any architectural changes before implementation; discuss with the user and document rationale.
- Align all architectural decisions with business goals and performance targets.
- Reference industry standards and best practices (e.g., [Clean Architecture](https://8thlight.com/blog/uncle-bob/2012/08/13/the-clean-architecture.html), [12 Factor App](https://12factor.net/), [OWASP Top Ten](https://owasp.org/www-project-top-ten/)).
- Cross-reference `coding-standards.md` and `context.md` for workflow, review, and quality requirements.

## 5. Exceptions & Evolution
- If a different architecture or pattern is required, propose the change, justify it, and document in an ADR.
- Regularly review and refactor architecture to address technical debt and evolving requirements.

## 6. Additional Architectural Guidance
- **Architecture Diagrams:** Maintain up-to-date system, component, and data flow diagrams for visual clarity. Diagrams should follow industry best practices and be generated programmatically (e.g., Mermaid, PlantUML, Graphviz) to ensure reproducibility, version control, and agent accessibility. When providing diagrams, include instructions for users to render or view them visually (e.g., using online editors, VS Code extensions, or CLI tools), in addition to the text-based source. Avoid manual image creation when possible.
- **Non-Functional Requirements:** Explicitly document requirements for scalability, reliability, security, and performance.
- **Extensibility:** Provide clear guidance on how to add new modules, integrations, or model types.
- **Error Handling & Observability:** Document patterns for error handling, logging, and monitoring at the architectural level.
- **Data Management:** Summarize how data is stored, accessed, and migrated across components.
- **Deployment & Environment:** Briefly describe deployment architecture (desktop, cloud, hybrid) and environment configuration.
- **Security Architecture:** Summarize security boundaries, trust zones, and key security mechanisms.
- **Evolution & Refactoring:** Encourage regular architectural reviews and refactoring to address technical debt and adapt to new requirements.
- **Agentic/Collaborative Patterns:** Agents must always check for architectural constraints and propose changes collaboratively, referencing ADRs and best practices.
- **Continuous Improvement:** Agents and contributors should always be looking for ways to improve the architecture. Propose enhancements, refactor for clarity and maintainability, and share lessons learned. All improvements should be discussed collaboratively and documented as needed.
- **Continuous Deployment (CD) Readiness:** While the current focus is on maintainability and quality, architecture decisions should anticipate future adoption of automated Continuous Deployment pipelines. Design for testability, automation, and minimal manual intervention.

---

For more details, see:
- `context.md` — Project context and workflow
- `coding-standards.md` — Code quality, security, and workflow
- `adr-practices.md` — Documenting architectural decisions
- Example ADR: `ADRs/002-project-structure-architecture.md` — Use as a template for new decisions
