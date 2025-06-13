Conventional commits: `type(scope): description`.

Feature branches, atomic commits, clean history, thorough testing before merge.

Feature flags for work-in-progress to prevent regressions.

Never force push to shared branches.

## GitHub CLI Setup

**Configure pager to avoid terminal issues:**
```bash
gh config set pager cat
```

**Common GitHub CLI Commands:**
- `gh pr list` - List all pull requests
- `gh pr view <number>` - View PR details
- `gh pr merge <number> --squash --delete-branch` - Squash merge PR
- `gh pr merge <number> --squash --auto` - Auto-merge when checks pass

**Dependabot PR Workflow:**
1. Check security alerts: `gh pr list` 
2. Review changes: `gh pr view <number>`
3. Merge safely: `gh pr merge <number> --squash --delete-branch`

**Repository uses squash merging only** - ensures clean git history with single commits per feature.
