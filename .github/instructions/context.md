# Project Context

This file provides the canonical context for all agentic development sessions. Agents and contributors must reference this file at the start of every session.

---

## 1. Project Mission & Vision
Build a universal launcher for local AI tools that is 4x faster and uses 4x less memory than Python implementations.

## 2. Agent Behavior & Communication
- Be concise and direct in all responses.
- Provide clear, minimal examples when illustrating concepts.
- Avoid unnecessary verbosity, repetition, or filler text.
- Prioritize actionable steps and summaries over lengthy explanations.
- Confirm understanding with short recaps if needed.
- Maintain a friendly and constructive tone in all interactions.
- If the user suggests something that may not align with best practices, industry standards, or the project's use-case, the agent should respectfully challenge the idea and open a dialog.
- Feedback should be collaborative, focusing on what is best for the project, and should always be supported by reasoning and relevant standards.
- Example: If the user prefers a specific software stack but there is a more suitable option, the agent should explain the benefits of the alternative and invite discussion, rather than insisting on a single approach.
- Do not assume user intent—ask clarifying questions if anything is ambiguous.
- If an error or blocker is encountered, document it in the chat and propose next steps or escalate as needed.
- Before starting work, briefly recap your understanding of the context and plan to ensure alignment with the user.

### Example: Good Plan Proposal and Confirmation
> **Agent:** Here is a proposed plan for adding feature X:
> 1. Update the backend API to support Y.
> 2. Add a new UI component for Z.
> 3. Write tests for the new functionality.
>
> **Justification:** This approach keeps changes small and reviewable, and aligns with our architecture and testing standards.
>
> **Is this plan acceptable, or would you like to suggest changes before I proceed?**
>
> **User:** Please split step 1 and 2 into separate tasks.
> **Agent:** Understood. I will implement step 1 first, submit for review, and then proceed to step 2 after your approval.

## 2a. Temporary and Session-Specific Plans
> Temporary or session-specific plans, overviews, and brainstorming should remain in the chat.
> - Do not create new markdown files for these purposes.
> - Only add persistent, project-wide context or finalized plans to canonical documentation (e.g., `context.md`, ADRs).
> - Clean up any temporary files or notes at the end of the session.

## 2b. Planning, Confirmation, and Incremental Changes
- Before starting any implementation, agents must propose a clear, concise plan and wait for explicit user confirmation.
- If the user suggests changes, update the plan and confirm again before proceeding.
- Always keep implementation changes small and incremental, making it easy for the user to review and approve each step before moving on.
- Avoid large, sweeping changes in a single step—break work into reviewable units.
- When proposing a plan or direction, provide a brief example and a clear justification for why this approach is recommended.

## 2c. Version Control and Task Workflow
- Make frequent, logically grouped commits as soon as work is functional. Avoid large, monolithic commits.
- Follow best practices for commit messages and atomic changes (see `version-control.md`).
- Ensure all tests pass before committing any code. Do not commit code that causes test failures.
- Only work on one task at a time. Complete and review the current task before starting a new one.
- For any task in progress, ensure it is marked as 'in progress' in the project management tool before beginning work.
- Do not start work on new tasks until the current task is completed, reviewed, and merged if applicable.

### Quality & Review Checklist
- Continuously follow all coding, architecture, and security standards (see `coding-standards.md`, `architecture.md`, and `security.md`) while working on any task—not just during review.
- Run all relevant tests before committing or merging changes. Never merge failing code.
- Update documentation (including `context.md` or relevant READMEs) if your changes affect usage, architecture, or workflows.
- Before committing or pushing code, review for secrets, sensitive data, or security issues.
- Periodically ask the user for feedback on process and communication to improve collaboration.
- If a task is paused or handed off, summarize the current state and next steps in the chat for continuity.
- Consider accessibility and inclusivity in UI/UX and documentation where relevant.
- Always refer to the current git status and repository state. When a file is obsolete or superseded, remove it from the repository rather than marking it as deprecated in-place. The version history will provide all necessary context.

## 3. Core Requirements & Success Metrics
- Unified interface for managing multiple concurrent AI tool instances
- Performance: 4x faster startup, 4x less memory usage
- Cross-platform (Windows, macOS, Linux)
- Hot-swappable development environment
- Startup time < 2 seconds
- Memory usage < 100MB base
- Support for 5+ concurrent AI tool instances
- Zero-configuration setup for common tools

## 4. Current State & Active Components
- **AI Studio**: Desktop app (Wails + React) — MAIN PRODUCT
- **AI Project Manager**: Web-based dev tool — DEVELOPMENT ONLY
- **ComfyUI Components**: Legacy Python launcher — BEING DEPRECATED

## 5. Session Initialization Checklist
1. Confirm project management tool is running in the correct mode:
   - If working on the project management tool: `AI_PM_MODE=dev make ai-pm-start`
   - For all other work: `make ai-pm-start` (production mode)
2. Use the CLI to list current tasks:
   - `./scripts/project-manager.sh list-tasks`
3. Summarize active tasks and priorities for session context.
4. Confirm all required services are running and environment is ready.
5. Reference this file for all decisions and context.

## 6. Mode Selection Guidance
- Always ask the user (or check context): Are you working on the project management tool itself, or using it to manage other work?
- Set/check `AI_PM_MODE` accordingly before starting the project management tool.
- Recap the current mode at session start.

## 7. Project Management CLI Reference
- List tasks: `./scripts/project-manager.sh list-tasks --help`
- List projects: `./scripts/project-manager.sh list-projects --help`
- Add task: `./scripts/project-manager.sh add-task --help`
- Update task: `./scripts/project-manager.sh update-task --help`
- For help: `./scripts/project-manager.sh --help`

## 8. CLI Limitation Guidance
If the project management CLI does not support a required detail:
1. Notify the user of the limitation.
2. Propose or create a task to add the feature to the CLI.
3. Offer to implement the enhancement if within scope.
4. Suggest a manual workaround if needed, and document the limitation.

## 9. Periodic Context Refresh
Agents should periodically re-read and summarize this file, especially after long or complex tasks, or after any interruption.

## 10. Documentation Index
- `.github/instructions/context.md` — This file
- `coding-standards.md` — Code quality and security
- `architecture.md` — Architecture and design
- `testing.md` — Testing requirements
- `security.md` — Security policies
- `script-management.md` — Script guidelines
- `project-management.md` — Project management tool usage
- `environment-setup.md` — Environment configuration

## 11. Contact or Escalation
If context is missing or ambiguous, ask the user for clarification or escalate to a project maintainer.