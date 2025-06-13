#!/bin/bash

# Plane API Interface for AI Agents
# Usage: ./scripts/plane-api.sh <action> [parameters]

source .env 2>/dev/null || true

PLANE_URL="${PLANE_URL:-http://localhost:8000}"
API_TOKEN="${PLANE_API_TOKEN:-}"

if [ -z "$API_TOKEN" ]; then
    echo "Error: PLANE_API_TOKEN not set in .env file"
    exit 1
fi

case "$1" in
    "list-issues")
        curl -s -H "Authorization: Bearer $API_TOKEN" \
             "$PLANE_URL/api/v1/workspaces/$2/projects/$3/issues/"
        ;;
    "create-issue")
        curl -s -X POST \
             -H "Authorization: Bearer $API_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{\"name\":\"$4\", \"description\":\"$5\", \"priority\":\"medium\"}" \
             "$PLANE_URL/api/v1/workspaces/$2/projects/$3/issues/"
        ;;
    "update-issue")
        curl -s -X PATCH \
             -H "Authorization: Bearer $API_TOKEN" \
             -H "Content-Type: application/json" \
             -d "{\"state\":\"$5\"}" \
             "$PLANE_URL/api/v1/workspaces/$2/projects/$3/issues/$4/"
        ;;
    "list-workspaces")
        curl -s -H "Authorization: Bearer $API_TOKEN" \
             "$PLANE_URL/api/v1/workspaces/"
        ;;
    *)
        echo "Usage: $0 {list-issues|create-issue|update-issue|list-workspaces} [workspace_id] [project_id] [issue_id] [title] [description]"
        echo ""
        echo "Examples:"
        echo "  $0 list-workspaces"
        echo "  $0 list-issues workspace_id project_id"
        echo "  $0 create-issue workspace_id project_id 'New Feature' 'Description here'"
        echo "  $0 update-issue workspace_id project_id issue_id completed"
        exit 1
        ;;
esac
