#!/bin/bash

# Simplified AI Project Management CLI
# Focused on core functionality with clean, maintainable code

set -euo pipefail

# Script directory and environment helper
readonly SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Source simplified environment helper
# shellcheck source=./env-helper.sh
source "$SCRIPT_DIR/env-helper.sh"

# Colors for output
readonly RED='\033[0;31m'
readonly GREEN='\033[0;32m'
readonly YELLOW='\033[1;33m'
readonly BLUE='\033[0;34m'
readonly NC='\033[0m' # No Color

# Global options
ENVIRONMENT=""
API_BASE_URL=""
INTERACTIVE=true
VERBOSE=false

# Output functions
error() { echo -e "${RED}✗${NC} $*" >&2; }
success() { echo -e "${GREEN}✓${NC} $*"; }
warning() { echo -e "${YELLOW}⚠${NC} $*"; }
info() { echo -e "${BLUE}ℹ${NC} $*"; }
debug() { [[ "$VERBOSE" == "true" ]] && echo -e "${BLUE}DEBUG:${NC} $*" >&2 || true; }

# Initialize environment
init_env() {
    if [[ -n "$API_BASE_URL" ]]; then
        debug "Using explicit API URL: $API_BASE_URL"
        return 0
    fi
    
    local env_info
    if ! env_info=$(get_env_info "$ENVIRONMENT" "$INTERACTIVE"); then
        error "Failed to initialize environment"
        return 1
    fi
    
    local env_type="${env_info%%:*}"
    API_BASE_URL="${env_info#*:}"
    
    debug "Initialized environment: $env_type -> $API_BASE_URL"
}

# Make API call with error handling
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="${3:-}"
    
    local url="${API_BASE_URL}${endpoint}"
    local curl_args=("-s" "-X" "$method")
    
    # Add authentication if configured
    load_env_config
    [[ -n "${AI_PM_API_TOKEN:-}" ]] && curl_args+=("-H" "Authorization: Bearer $AI_PM_API_TOKEN")
    
    # Add data for POST/PUT requests
    if [[ -n "$data" ]]; then
        curl_args+=("-H" "Content-Type: application/json" "-d" "$data")
    fi
    
    debug "API call: $method $url"
    [[ -n "$data" ]] && debug "Data: $data"
    
    # Use curl to get both response and HTTP status code
    local temp_file response http_code
    temp_file=$(mktemp)
    
    if http_code=$(curl "${curl_args[@]}" -w "%{http_code}" -o "$temp_file" "$url" 2>/dev/null); then
        response=$(cat "$temp_file")
        rm -f "$temp_file"
        
        # Check if HTTP status code indicates success (2xx)
        if [[ "$http_code" =~ ^2[0-9][0-9]$ ]]; then
            echo "$response"
        else
            error "API call failed with HTTP $http_code: $response"
            return 1
        fi
    else
        rm -f "$temp_file"
        error "API call failed: $method $url"
        return 1
    fi
}

# Check required dependencies
check_deps() {
    command_exists curl || { error "curl is required but not installed"; return 1; }
    command_exists jq || { error "jq is required but not installed"; return 1; }
    
    # Test API connectivity
    if ! test_api "$API_BASE_URL" 5; then
        error "API is not responding at $API_BASE_URL"
        return 1
    fi
}

# Format task output
format_task() {
    local task="$1"
    
    # Use jq to properly parse JSON
    local id title status priority
    id=$(echo "$task" | jq -r '.id // ""')
    title=$(echo "$task" | jq -r '.title // ""')
    status=$(echo "$task" | jq -r '.status // ""')
    priority=$(echo "$task" | jq -r '.priority // ""')
    
    printf "%-4s %-30s %-12s %s\n" "$id" "${title:0:30}" "$status" "$priority"
}

# Command implementations
cmd_list_tasks() {
    local project_id=""
    local status=""
    local verbose_output=false
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--project) project_id="$2"; shift 2 ;;
            -s|--status) status="$2"; shift 2 ;;
            -v|--verbose) verbose_output=true; shift ;;
            -h|--help)
                echo "Usage: list-tasks [-p PROJECT_ID] [-s STATUS] [-v]"
                echo "  -p, --project    Filter by project ID"
                echo "  -s, --status     Filter by status"
                echo "  -v, --verbose    Show additional details"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    local endpoint="/tasks"
    local params=()
    
    [[ -n "$project_id" ]] && params+=("project_id=$project_id")
    [[ -n "$status" ]] && params+=("status=$status")
    
    if [[ ${#params[@]} -gt 0 ]]; then
        endpoint+="?$(IFS='&'; echo "${params[*]}")"
    fi
    
    local response
    if ! response=$(api_call "GET" "$endpoint"); then
        return 1
    fi
     # Simple JSON array parsing
    if [[ "$response" == "[]" ]]; then
        info "No tasks found"
        return 0
    fi

    # Calculate optimal column widths
    local terminal_width
    terminal_width=$(tput cols 2>/dev/null || echo "80")
    
    # Parse all tasks first to determine max title length
    local max_title_length=5  # minimum for "TITLE" header
    local task_data=()
    
    # First pass: collect data and find max title length
    while read -r line; do
        local id title status priority
        # Parse the tab-separated values from jq output
        IFS=$'\t' read -r id title status priority <<< "$line"
        
        task_data+=("$id|$title|$status|$priority")
        local title_length=${#title}
        if [[ $title_length -gt $max_title_length ]]; then
            max_title_length=$title_length
        fi
    done < <(echo "$response" | jq -r '.[] | [.id // "", .title // "", .status // "", .priority // ""] | @tsv')
    
    # Calculate column widths (ID: 4, STATUS: 12, PRIORITY: 8, remainder for TITLE)
    local id_width=4
    local status_width=12
    local priority_width=8
    local available_for_title=$((terminal_width - id_width - status_width - priority_width - 6))  # 6 for spacing
    
    # Use smaller of max_title_length or available space, but at least 20 chars
    local title_width=$max_title_length
    if [[ $available_for_title -lt $max_title_length ]] && [[ $available_for_title -ge 20 ]]; then
        title_width=$available_for_title
    elif [[ $available_for_title -lt 20 ]]; then
        title_width=20
    fi
    
    # Print header
    printf "%-${id_width}s %-${title_width}s %-${status_width}s %-${priority_width}s\n" "ID" "TITLE" "STATUS" "PRIORITY"
    printf '%*s\n' "$((id_width + title_width + status_width + priority_width + 3))" | tr ' ' '─'
    
    # Print tasks
    for task_line in "${task_data[@]}"; do
        IFS='|' read -r id title status priority <<< "$task_line"
        # Truncate title if needed
        if [[ ${#title} -gt $title_width ]]; then
            title="${title:0:$((title_width - 3))}..."
        fi
        printf "%-${id_width}s %-${title_width}s %-${status_width}s %-${priority_width}s\n" "$id" "$title" "$status" "$priority"
    done
}

cmd_add_task() {
    local project_id="" title="" description="" priority="medium"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -p|--project) project_id="$2"; shift 2 ;;
            -t|--title) title="$2"; shift 2 ;;
            -d|--description) description="$2"; shift 2 ;;
            -r|--priority) priority="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: add-task -p PROJECT_ID -t TITLE [-d DESCRIPTION] [-r PRIORITY]"
                echo "  -p, --project      Project ID (required)"
                echo "  -t, --title        Task title (required)"
                echo "  -d, --description  Task description"
                echo "  -r, --priority     Priority (low|medium|high, default: medium)"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$project_id" || -z "$title" ]]; then
        error "Project ID and title are required"
        return 1
    fi
    
    # Validate priority
    case "$priority" in
        low|medium|high) ;;
        *) error "Priority must be: low, medium, or high"; return 1 ;;
    esac
    
    local json_data
    json_data=$(cat <<EOF
{
    "project_id": $project_id,
    "title": "$title",
    "description": "$description",
    "priority": "$priority",
    "status": "todo"
}
EOF
)
    
    if response=$(api_call "POST" "/tasks" "$json_data"); then
        local task_id
        task_id=$(echo "$response" | jq -r '.id')
        success "Task '$title' added successfully with ID: $task_id"
    else
        error "Failed to add task"
        return 1
    fi
}

cmd_update_task() {
    local task_id="" status="" title="" description=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--id) task_id="$2"; shift 2 ;;
            -s|--status) status="$2"; shift 2 ;;
            -t|--title) title="$2"; shift 2 ;;
            -d|--description) description="$2"; shift 2 ;;
            -h|--help)
                local valid_statuses
                valid_statuses=$(get_valid_statuses | tr '\n' '|' | sed 's/|$//' | sed 's/|/, /g')
                echo "Usage: update-task -i TASK_ID [-s STATUS] [-t TITLE] [-d DESCRIPTION]"
                echo "  -i, --id           Task ID (required)"
                echo "  -s, --status       New status ($valid_statuses)"
                echo "  -t, --title        New title"
                echo "  -d, --description  New description"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" ]]; then
        error "Task ID is required"
        return 1
    fi
    
    # Validate status if provided
    if [[ -n "$status" ]]; then
        if ! validate_status "$status"; then
            return 1
        fi
    fi
    
    # Build JSON data with only provided fields
    local json_parts=()
    [[ -n "$status" ]] && json_parts+=("\"status\": \"$status\"")
    [[ -n "$title" ]] && json_parts+=("\"title\": \"$title\"")
    [[ -n "$description" ]] && json_parts+=("\"description\": \"$description\"")
    
    if [[ ${#json_parts[@]} -eq 0 ]]; then
        error "At least one field to update is required"
        return 1
    fi
    
    local json_data="{$(IFS=','; echo "${json_parts[*]}")}"
    
    if api_call "PUT" "/tasks/$task_id" "$json_data" >/dev/null; then
        success "Task $task_id updated successfully"
    else
        error "Failed to update task"
        return 1
    fi
}

cmd_delete_task() {
    local task_id=""
    local reason="Deleted via CLI"
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--id) task_id="$2"; shift 2 ;;
            -r|--reason) reason="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: delete-task -i TASK_ID [-r REASON]"
                echo "  -i, --id       Task ID (required)"
                echo "  -r, --reason   Deletion reason (default: 'Deleted via CLI')"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" ]]; then
        error "Task ID is required"
        return 1
    fi
    
    local json_data
    json_data=$(jq -n --arg reason "$reason" '{reason: $reason}')
    
    if api_call "DELETE" "/tasks/$task_id" "$json_data" >/dev/null; then
        success "Task $task_id deleted successfully"
    else
        error "Failed to delete task"
        return 1
    fi
}

cmd_list_projects() {
    local response
    if ! response=$(api_call "GET" "/projects"); then
        return 1
    fi
    
    if [[ "$response" == "[]" ]]; then
        info "No projects found"
        return 0
    fi
    
    printf "%-4s %-30s %s\n" "ID" "NAME" "DESCRIPTION"
    echo "────────────────────────────────────────────────────────────"
    
    # Use jq to parse JSON array and format each project
    echo "$response" | jq -r '.[] | "\(.id // "")\t\(.name // "")\t\(.description // "")"' | \
    while IFS=$'\t' read -r id name description; do
        printf "%-4s %-30s %s\n" "$id" "${name:0:30}" "${description:0:50}"
    done
}

cmd_health() {
    if test_api "$API_BASE_URL"; then
        success "API is healthy at $API_BASE_URL"
    else
        error "API health check failed"
        return 1
    fi
}

cmd_add_note() {
    local task_id="" content=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--task) task_id="$2"; shift 2 ;;
            -c|--content) content="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: add-note -t TASK_ID -c CONTENT"
                echo "  -t, --task       Task ID (required)"
                echo "  -c, --content    Note content (required)"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" || -z "$content" ]]; then
        error "Task ID and content are required"
        return 1
    fi
    
    local json_data
    json_data=$(jq -n --arg task_id "$task_id" --arg content "$content" \
        '{task_id: ($task_id | tonumber), content: $content}')
    
    if response=$(api_call "POST" "/notes" "$json_data"); then
        local note_id
        note_id=$(echo "$response" | jq -r '.id')
        success "Note #$note_id added to task $task_id"
    else
        error "Failed to add note"
        return 1
    fi
}

cmd_list_notes() {
    local task_id=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -t|--task) task_id="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: list-notes -t TASK_ID"
                echo "  -t, --task    Task ID (required)"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" ]]; then
        error "Task ID is required"
        return 1
    fi
    
    local response
    if ! response=$(api_call "GET" "/notes?task_id=$task_id"); then
        return 1
    fi
    
    if [[ "$response" == "[]" ]]; then
        info "No notes found for task $task_id"
        return 0
    fi
    
    printf "%-4s %-50s %-16s\n" "ID" "CONTENT" "CREATED"
    echo "────────────────────────────────────────────────────────────────────"
    
    echo "$response" | jq -r '.[] | "\(.id)\t\(.content)\t\(.created_at)"' | while IFS=$'\t' read -r id content created_at; do
        # Truncate content if too long
        if [[ ${#content} -gt 48 ]]; then
            content="${content:0:45}..."
        fi
        # Format date (simple format)
        created_date="${created_at:0:16}"
        printf "%-4s %-50s %-16s\n" "$id" "$content" "$created_date"
    done
}

cmd_delete_note() {
    local note_id=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--id) note_id="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: delete-note -i NOTE_ID"
                echo "  -i, --id    Note ID (required)"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$note_id" ]]; then
        error "Note ID is required"
        return 1
    fi
    
    if [[ "$INTERACTIVE" == "true" ]]; then
        warning "This will permanently delete note $note_id"
        echo "Are you sure? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            info "Delete cancelled"
            return 0
        fi
    fi
    
    if api_call "DELETE" "/notes/$note_id" >/dev/null; then
        success "Note $note_id deleted successfully"
    else
        error "Failed to delete note"
        return 1
    fi
}

cmd_add_project() {
    local name="" description=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -n|--name) name="$2"; shift 2 ;;
            -d|--description) description="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: add-project -n NAME [-d DESCRIPTION]"
                echo "  -n, --name         Project name (required)"
                echo "  -d, --description  Project description"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$name" ]]; then
        error "Project name is required"
        return 1
    fi
    
    local json_data
    json_data=$(jq -n --arg name "$name" --arg desc "$description" \
        '{name: $name, description: $desc}')
    
    if response=$(api_call "POST" "/projects" "$json_data"); then
        local project_id
        project_id=$(echo "$response" | jq -r '.id')
        success "Project '$name' created successfully with ID: $project_id"
    else
        error "Failed to create project"
        return 1
    fi
}

cmd_delete_project() {
    local project_id=""
    
    while [[ $# -gt 0 ]]; do
        case $1 in
            -i|--id) project_id="$2"; shift 2 ;;
            -h|--help)
                echo "Usage: delete-project -i PROJECT_ID"
                echo "  -i, --id    Project ID (required)"
                return 0
                ;;
            *) error "Unknown option: $1"; return 1 ;;
        esac
    done
    
    if [[ -z "$project_id" ]]; then
        error "Project ID is required"
        return 1
    fi
    
    if [[ "$INTERACTIVE" == "true" ]]; then
        warning "This will permanently delete project $project_id and all its tasks"
        echo "Are you sure? [y/N]"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            info "Delete cancelled"
            return 0
        fi
    fi
    
    if api_call "DELETE" "/projects/$project_id" >/dev/null; then
        success "Project $project_id deleted successfully"
    else
        error "Failed to delete project"
        return 1
    fi
}

cmd_config() {
    show_config
}

# Fetch valid status values from API
get_valid_statuses() {
    local response
    if response=$(api_call "GET" "/status-values" 2>/dev/null); then
        echo "$response" | jq -r '.[].key' 2>/dev/null
    else
        # Fallback to hardcoded values if API is not available
        echo -e "todo\nin_progress\nreview\ndone"
    fi
}

# Validate status against API values
validate_status() {
    local status="$1"
    local valid_statuses
    valid_statuses=$(get_valid_statuses)
    
    if echo "$valid_statuses" | grep -q "^${status}$"; then
        return 0
    else
        local status_list
        status_list=$(echo "$valid_statuses" | tr '\n' '|' | sed 's/|$//')
        error "Status must be one of: ${status_list//|/, }"
        return 1
    fi
}

# Help function
show_help() {
    echo -e "${BLUE}AI Project Management CLI v3.0 (Simplified)${NC}"
    echo
    echo "Usage: $0 [GLOBAL OPTIONS] <command> [options]"
    echo

    echo "GLOBAL OPTIONS:"
    echo "  --env <env>          Force environment (dev|prod)"
    echo "  --api-url <url>      Use specific API URL"
    echo "  --non-interactive    Disable interactive prompts"
    echo "  --verbose, -v        Enable verbose output"
    echo "  --help, -h           Show this help"
    echo
    echo "COMMANDS:"
    echo "  list-tasks           List tasks with filtering options"
    echo "  add-task             Add a new task"
    echo "  update-task          Update task properties"
    echo "  delete-task          Delete a task"
    echo "  list-projects        List all projects"
    echo "  health               Check API health"
    echo "  help                 Show this help"
    echo "  add-note             Add a note to a task"
    echo "  list-notes           List notes for a task"
    echo "  delete-note          Delete a note"
    echo "  add-project          Create a new project"
    echo "  delete-project       Delete a project"
    echo "  config               Show current configuration"
    echo
    echo "For command-specific help: $0 <command> --help"
    echo
    echo "EXAMPLES:"
    echo "  $0 list-tasks -p 1 -s todo"
    echo "  $0 add-task -p 1 -t \"Fix bug\" -r high"
    echo "  $0 update-task -i 42 -s done"
    echo "  $0 delete-task -i 42"
    echo "  $0 --env dev list-projects"
}

# Main command dispatcher
main() {
    # Parse global arguments directly
    while [[ $# -gt 0 ]]; do
        case $1 in
            --env) ENVIRONMENT="$2"; shift 2 ;;
            --api-url) API_BASE_URL="$2"; shift 2 ;;
            --non-interactive) INTERACTIVE=false; shift ;;
            --verbose|-v) VERBOSE=true; shift ;;
            --help|-h) show_help; return 0 ;;
            *) break ;; # First non-global arg is the command
        esac
    done
    
    if [[ $# -eq 0 ]]; then
        show_help
        return 0
    fi
    
    local command="$1"
    shift
    
    # Initialize environment for commands that need it
    case "$command" in
        help) show_help; return 0 ;;
        *) init_env && check_deps ;;
    esac
    
    # Execute command
    case "$command" in
        list-tasks) cmd_list_tasks "$@" ;;
        add-task) cmd_add_task "$@" ;;
        update-task) cmd_update_task "$@" ;;
        delete-task) cmd_delete_task "$@" ;;
        list-projects) cmd_list_projects "$@" ;;
        health) cmd_health ;;
        add-note) cmd_add_note "$@" ;;
        list-notes) cmd_list_notes "$@" ;;
        delete-note) cmd_delete_note "$@" ;;
        add-project) cmd_add_project "$@" ;;
        delete-project) cmd_delete_project "$@" ;;
        config) cmd_config ;;
        *) error "Unknown command: $command"; show_help; return 1 ;;
    esac
}

# Run if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
