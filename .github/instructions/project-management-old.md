Project management uses Plane (open source) for AI agent integration.

Setup: `make plane-setup` starts Plane at http://localhost:3000.

AI agents can interact via `./scripts/plane-api.sh`:
- `plane-api.sh list-workspaces` - Get workspace IDs
- `plane-api.sh list-issues workspace_id project_id` - View current tasks
- `plane-api.sh create-issue workspace_id project_id "title" "description"` - Add tasks
- `plane-api.sh update-issue workspace_id project_id issue_id completed` - Mark done

Requires PLANE_API_TOKEN in .env file (generate from Plane Settings > API Tokens).
