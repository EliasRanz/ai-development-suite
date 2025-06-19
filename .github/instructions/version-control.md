# Version Control Standards for Agentic Workflows

All agents must follow these standards to ensure a clean, auditable, and collaborative codebase. Reference: [coding-standards.md], [project-management.md], [context.md].

## Agent Commit Practices
- Use **Conventional Commits**: `type(scope): description` (see [https://www.conventionalcommits.org/]).
- Every commit must include a rationale and reference the agent session context or relevant task.
- Document any agent-to-agent context transfer in the commit or PR description.
- Never commit generated, build, or secret files.
- Each commit should be atomic and reproducible by other agents.

## Branching & Merging
- Agents must use feature branches for all work. Name branches clearly (e.g., `feature/xyz`, `fix/bug-123`).
- Never force-push to shared branches (e.g., `main`, `develop`).
- Use **feature flags** for incomplete or experimental work to prevent regressions.
- All merges must be via **squash merge** to maintain a linear, readable history.
- Automated checks must pass before merging. Agents are responsible for ensuring all tests and linters succeed.

## Pull Request Workflow
- Open a pull request (PR) for all changes. Link to relevant issues and agent session context.
- PR descriptions must include:
  - Rationale for the change
  - Reference to agent session context or task
  - Any context required for downstream agents
- Review PRs for code quality, security, and adherence to standards. Agents must confirm compliance before approval.
- Use the GitHub CLI for efficiency:
  - `gh pr list` — List all pull requests
  - `gh pr view <number>` — View PR details
  - `gh pr merge <number> --squash --delete-branch` — Squash merge and delete branch
  - `gh pr merge <number> --squash --auto` — Auto-merge when checks pass
- For Dependabot or automated PRs:
  1. Review security alerts: `gh pr list`
  2. Review changes: `gh pr view <number>`
  3. Merge safely: `gh pr merge <number> --squash --delete-branch`

## GitHub CLI Setup
- Configure pager to avoid terminal issues:
  ```bash
  gh config set pager cat
  ```

## Agentic Principles
- Maintain a clean, auditable history. Rebase or squash local commits before PR if needed.
- Automate repetitive tasks and minimize manual intervention.
- Agents are responsible for propagating relevant context and rationale for all changes.
- Regularly review commit history and PRs for compliance and opportunities to improve agent workflows.
- For authoritative development commands, always use `make help` (see [context.md]).

## Advanced Agentic Automation & Compliance

- **Automated Context Propagation:**
  - Integrate bots or scripts to automatically append relevant session context or task references to PRs and commit messages.
  - Agents should use or maintain these tools to minimize manual context entry.

- **Agent Identity and Attribution:**
  - All agent actions (commits, PRs, merges) must be clearly attributed, using bot accounts or commit trailers (e.g., `Agent-Session: <session-id>`).

- **Context Validation Hooks:**
  - Implement pre-commit and pre-merge hooks to ensure all commits and PRs include required context, rationale, and references to session or task IDs.
  - Reject commits/PRs that do not meet these requirements.

- **Automated Compliance Reporting:**
  - Use scripts or CI jobs to regularly audit the repository for compliance with agentic standards (e.g., missing context, improper commit messages, unreviewed PRs).
  - Agents must address compliance issues promptly.

- **Continuous Agent Training:**
  - Periodically review and update agent instructions based on workflow bottlenecks, audit findings, or new best practices.
  - Agents should propose improvements as part of regular retrospectives.

- **Onboarding Automation:**
  - Provide scripts or onboarding bots to set up agent environments, configure GitHub CLI, and enforce initial compliance.

---
These advanced practices ensure robust, scalable, and fully auditable agent-driven development workflows.
