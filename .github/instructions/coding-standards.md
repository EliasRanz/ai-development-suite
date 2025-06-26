# Coding Standards for Agentic Development

## 1. Core Coding Standards (Language-Agnostic)
- Apply SOLID, DRY, and KISS principles in all code, regardless of language.
- Design APIs and interfaces before implementation (API-first).
- Keep files small and modular: refactor at 300+ lines and never exceed 500 lines per file (except for generated code—files created automatically by tools, such as API stubs, ORM models, or build outputs, which are exempt from these limits).
- Use descriptive, consistent naming for variables, functions, and files.
- Handle errors explicitly and fail fast; never ignore errors.
- Validate all inputs and never hardcode secrets or credentials.
- Write clear, minimal comments; prefer self-documenting code.
- Ensure all code is covered by automated tests; aim for high coverage.
- Tests should be properly packaged and organized, with clear names indicating their purpose.
- All changes must be reviewed before merging.
- Refactor functions/methods at 40+ lines; never exceed 50 lines. Each function should have a single responsibility.
- Code reviews must reject changes that violate these limits.

## 2. Security & Privacy
- Follow least privilege and secure-by-default principles.
- Never commit secrets, credentials, or sensitive data.
- Sanitize and validate all external input.
- Review for security issues before committing or merging.

## 3. Documentation & Readability
- Keep documentation concise and relevant.
- Update documentation if code changes affect usage, architecture, or workflows.
- Prefer clarity and maintainability over cleverness.

## 4. Agentic Coding Best Practices
- Propose a plan and wait for user confirmation before implementation.
- Keep changes small, incremental, and reviewable.
- Ask clarifying questions if requirements are ambiguous.
- Reference the “Quality & Review Checklist” in `context.md` for every task.

## 5. Language-Specific Guidance
- Reference official style guides and use linters/formatters for each language:
  - Go: [Effective Go](https://go.dev/doc/effective_go.html)
  - Python: [PEP 8](https://peps.python.org/pep-0008/)
  - TypeScript/JavaScript: [Airbnb Style Guide](https://github.com/airbnb/javascript)
  - Shell: [Google Shell Style Guide](https://google.github.io/styleguide/shellguide.html)
- Add language-specific notes in project or module READMEs as needed.

## 6. Linting & Formatting
- All code must pass automated linting and be auto-formatted before review. Use project-standard tools for each language.

## 7. Dependency Management
- Use the latest stable versions of dependencies unless there is a documented reason to pin to an older version.
- Regularly review and update dependencies to ensure security and compatibility.
- Document and justify any new third-party dependency or version pinning in the PR or commit message. Avoid unnecessary dependencies.

## 8. Comments & Public APIs
- All public functions, classes, and exported APIs must have clear docstrings or comments describing their purpose and usage.

## 9. Refactoring & Technical Debt
- Flag and, when possible, address technical debt or code smells as part of your workflow. Leave TODOs with context if immediate refactor is not possible.

## 10. Accessibility & Internationalization (if relevant)
- For UI code, follow accessibility (WCAG) and i18n/l10n best practices where applicable.

## 11. Performance
- Consider performance and resource usage, especially for critical paths. Optimize only when necessary and justified.

## 12. Commit Messages
- Use clear, conventional commit messages. Example:
  - `feat(api): add user authentication endpoint`
  - `fix(ui): correct button alignment on mobile`
  - `refactor(core): split monolithic file into modules`

## 13. Branching & Feature Flags
- Use feature branches for all new work. Never commit directly to the main branch.
- All work-in-progress or experimental features must be protected by feature flags to prevent unfinished code from affecting production.
- For full details on branching strategy, commit workflow, and feature flagging, see `version-control.md`.

## 14. Automated Enforcement & Tooling
- Use pre-commit hooks (lint, test, format) to catch issues before code review.
- Integrate CI/CD pipelines to enforce standards and run automated checks on every PR.
- Reference or provide editorconfig, linter, and formatter configs in the repo for consistency.

## 15. Backward Compatibility
- Consider and document backward compatibility for all public APIs and data models. Avoid breaking changes unless necessary and well-communicated.

## 16. Legacy Code
- When working in legacy code, leave it better than you found it. Refactor or add tests incrementally where possible.

## 17. Code Ownership & Review Rotation
- Encourage shared code ownership and rotate code review responsibilities to spread knowledge and avoid silos.

## 18. Security Reviews
- For sensitive or critical code, require a dedicated security review or checklist in addition to standard review.

## 19. Open Source Readiness (if applicable)
- Ensure all code, dependencies, and documentation are ready for public release. Follow licensing and third-party code requirements.

## 20. Continuous Improvement
- Contributors and agents are encouraged to propose improvements to these coding standards as the project evolves.

---

For more details, see:
- `context.md` — Workflow and review checklist
- `security.md` — Security policies
- `testing.md` — Testing requirements
- `architecture.md` — Architecture and design
- `version-control.md` — Commit and branching standards
