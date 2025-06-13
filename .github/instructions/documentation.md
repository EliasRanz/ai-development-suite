Minimal, essential documentation focused on AI-driven development.

## Documentation Policy

### Essential Files Only
- Keep documentation focused and avoid bloat
- No unnecessary README files or status documents
- Maintain project status in chat context, not separate files
- Each tool gets ONE README maximum

### What to Document
- Core project setup and usage (`README.md`)
- Tool-specific setup instructions (individual tool READMEs)
- Architecture decisions (`ADRs/` folder)
- AI development methodology (`AI_DEVELOPMENT_APPROACH.md`)
- Security and sensitive data handling (`.github/instructions/`)

### What NOT to Document
- Temporary project status (use chat context)
- Detailed development logs (use git history)
- Multiple readiness checklists
- Duplicate information across files

### AI Agent Guidelines
Keep `.github/instructions/` updated as problems are encountered - any AI agent should start where the previous one left off.

Check AI Project Manager (formerly Plane) for current tasks and status at session start.

Use AI Project Manager for task tracking and project status.

Significant decisions go in `ADRs/` folder.

Self-documenting code over extensive comments.
