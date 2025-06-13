#!/bin/bash
# AI Project Management CLI (Enhanced with getopts)
# Modern CLI with flag support, colors, and improved user experience

set -euo pipefail

# API configuration
API_BASE_URL="http://localhost:8000/api"

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

# Helper functions
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1" >&2; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# API call function
api_call() {
    local method="$1" endpoint="$2" data="${3:-}"
    case "$method" in
        GET) curl -s "$API_BASE_URL$endpoint" ;;
        POST|PUT) curl -s -X "$method" "$API_BASE_URL$endpoint" \
                    -H "Content-Type: application/json" -d "$data" ;;
        DELETE) curl -s -X DELETE "$API_BASE_URL$endpoint" ;;
    esac
}

# Check dependencies
check_deps() {
    for cmd in curl jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "$cmd is required but not installed"
            exit 1
        fi
    done
    
    if ! curl -s "$API_BASE_URL/health" >/dev/null 2>&1; then
        print_error "API not available at $API_BASE_URL"
        print_info "Start services with: make ai-pm-start"
        exit 1
    fi
}

# Command functions
cmd_list_tasks() {
    local project_id="" verbose=false
    
    while getopts ":p:vh" opt; do
        case $opt in
            p) project_id="$OPTARG" ;;
            v) verbose=true ;;
            h) cat <<EOF
Usage: $0 list-tasks [-p PROJECT_ID] [-v] [-h]
  -p PROJECT_ID  Filter by project ID
  -v             Verbose output (detailed summary format with descriptions)
  -h             Show help

Regular output: Clean table format with ID, Project, Title, Status, Priority
Verbose output: Detailed summary format with full descriptions and timestamps
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
        esac
    done
    
    local endpoint="/tasks"
    [[ -n "$project_id" ]] && endpoint="/tasks?project_id=$project_id"
    
    local response=$(api_call GET "$endpoint")
    if [[ "$response" == "[]" ]]; then
        print_warning "No tasks found"
        return
    fi
    
    if [[ "$verbose" == true ]]; then
        # Verbose: use summary format instead of table
        echo
        echo -e "${BLUE}Task Summary:${NC}"
        echo "$response" | jq -r '.[] | 
            "
\u001b[0;33m► Task #\(.id): \(.title)\u001b[0m
  Project: \(.project_name // "Unknown")
  Status: \(.status) | Priority: \(.priority)
  Description: \(.description // "No description provided")
  Created: \(.created_at | split("T")[0]) | Updated: \(.updated_at | split("T")[0])
  "'
    else
        # Regular: clean tabular format
        printf "%-4s %-30s %-35s %-12s %-8s\n" "ID" "PROJECT" "TITLE" "STATUS" "PRIORITY"
        printf "%-4s %-30s %-35s %-12s %-8s\n" "──" "──────────────────────────────" "───────────────────────────────────" "────────────" "────────"
        
        echo "$response" | jq -r '.[] | "\(.id)\t\(.project_name // "Unknown")\t\(.title)\t\(.status)\t\(.priority)"' |
        while IFS=$'\t' read -r id project title status priority; do
            printf "%-4s %-30s %-35s %-12s %-8s\n" "$id" "${project:0:29}" "${title:0:34}" "$status" "$priority"
        done
    fi
}

cmd_add_task() {
    local project_id="" title="" description="" priority="medium"
    
    while getopts ":p:t:d:r:h" opt; do
        case $opt in
            p) project_id="$OPTARG" ;;
            t) title="$OPTARG" ;;
            d) description="$OPTARG" ;;
            r) priority="$OPTARG" ;;
            h) cat <<EOF
Usage: $0 add-task -p PROJECT_ID -t TITLE [-d DESCRIPTION] [-r PRIORITY] [-h]
  -p PROJECT_ID  Project ID (required)
  -t TITLE       Task title (required)
  -d DESCRIPTION Task description
  -r PRIORITY    Priority (low|medium|high|urgent)
  -h             Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
            :) print_error "Option -$OPTARG requires an argument"; return 1 ;;
        esac
    done
    
    if [[ -z "$project_id" || -z "$title" ]]; then
        print_error "Project ID and title are required"
        return 1
    fi
    
    local data=$(jq -n \
        --arg pid "$project_id" \
        --arg title "$title" \
        --arg desc "$description" \
        --arg priority "$priority" \
        '{project_id: ($pid|tonumber), title: $title, description: $desc, priority: $priority}')
    
    local response=$(api_call POST "/tasks" "$data")
    if echo "$response" | jq -e '.id' >/dev/null; then
        print_success "Task created successfully"
    else
        print_error "Failed to create task: $response"
        return 1
    fi
}

cmd_update_task() {
    local task_id="" status=""
    
    while getopts ":i:s:h" opt; do
        case $opt in
            i) task_id="$OPTARG" ;;
            s) status="$OPTARG" ;;
            h) cat <<EOF
Usage: $0 update-task -i TASK_ID -s STATUS [-h]
  -i TASK_ID  Task ID (required)
  -s STATUS   New status (todo|in_progress|review|done)
  -h          Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
            :) print_error "Option -$OPTARG requires an argument"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" || -z "$status" ]]; then
        print_error "Task ID and status are required"
        return 1
    fi
    
    local data=$(jq -n --arg status "$status" '{status: $status}')
    local response=$(api_call PUT "/tasks/$task_id" "$data")
    
    if echo "$response" | jq -e '.id' >/dev/null; then
        print_success "Task $task_id updated to '$status'"
    else
        print_error "Failed to update task: $response"
        return 1
    fi
}

cmd_delete_task() {
    local task_id=""
    
    while getopts ":i:h" opt; do
        case $opt in
            i) task_id="$OPTARG" ;;
            h) cat <<EOF
Usage: $0 delete-task -i TASK_ID [-h]
  -i TASK_ID  Task ID to delete (required)
  -h          Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
            :) print_error "Option -$OPTARG requires an argument"; return 1 ;;
        esac
    done
    
    if [[ -z "$task_id" ]]; then
        print_error "Task ID is required"
        return 1
    fi
    
    # Get task details first for confirmation
    local task_info=$(api_call GET "/tasks/$task_id")
    if ! echo "$task_info" | jq -e '.id' >/dev/null; then
        print_error "Task $task_id not found"
        return 1
    fi
    
    local title=$(echo "$task_info" | jq -r '.title // "Unknown"')
    print_warning "Deleting task $task_id: $title"
    
    local response=$(api_call DELETE "/tasks/$task_id")
    
    if [[ "$response" == "" ]] || echo "$response" | jq -e '.message' >/dev/null 2>&1; then
        print_success "Task $task_id deleted successfully"
    else
        print_error "Failed to delete task: $response"
        return 1
    fi
}

# Project management commands

cmd_list_projects() {
    local verbose=false
    
    while getopts ":vh" opt; do
        case $opt in
            v) verbose=true ;;
            h) cat <<EOF
Usage: $0 list-projects [-v] [-h]
  -v             Verbose output
  -h             Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
        esac
    done
    
    local response=$(api_call GET "/projects")
    if [[ "$response" == "[]" ]] || [[ "$response" == "null" ]] || [[ -z "$response" ]]; then
        print_warning "No projects found"
        return
    fi
    
    if [[ "$verbose" == true ]]; then
        echo "$response" | jq -r '.[] | "ID: \(.id) | \(.name) | \(.description // "No description")"'
    else
        printf "%-4s %-30s %-50s\n" "ID" "NAME" "DESCRIPTION"
        printf "%-4s %-30s %-50s\n" "──" "──────────────────────────────" "──────────────────────────────────────────────────"
        echo "$response" | jq -r '.[] | "\(.id)\t\(.name)\t\(.description // "")"' |
        while IFS=$'\t' read -r id name description; do
            printf "%-4s %-30s %-50s\n" "$id" "${name:0:29}" "${description:0:49}"
        done
    fi
}

cmd_add_project() {
    local name="" description=""
    
    while getopts ":n:d:h" opt; do
        case $opt in
            n) name="$OPTARG" ;;
            d) description="$OPTARG" ;;
            h) cat <<EOF
Usage: $0 add-project -n NAME [-d DESCRIPTION] [-h]
  -n NAME        Project name (required)
  -d DESCRIPTION Project description
  -h             Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
            :) print_error "Option -$OPTARG requires an argument"; return 1 ;;
        esac
    done
    
    if [[ -z "$name" ]]; then
        print_error "Project name is required"
        return 1
    fi
    
    local data=$(jq -n \
        --arg name "$name" \
        --arg desc "$description" \
        '{name: $name, description: $desc}')
    
    local response=$(api_call POST "/projects" "$data")
    if echo "$response" | jq -e '.id' >/dev/null; then
        local project_id=$(echo "$response" | jq -r '.id')
        print_success "Project '$name' created successfully with ID: $project_id"
    else
        print_error "Failed to create project: $response"
        return 1
    fi
}

cmd_delete_project() {
    local project_id=""
    
    while getopts ":i:h" opt; do
        case $opt in
            i) project_id="$OPTARG" ;;
            h) cat <<EOF
Usage: $0 delete-project -i PROJECT_ID [-h]
  -i PROJECT_ID  Project ID to delete (required)
  -h             Show help
EOF
               return ;;
            \?) print_error "Invalid option: -$OPTARG"; return 1 ;;
            :) print_error "Option -$OPTARG requires an argument"; return 1 ;;
        esac
    done
    
    if [[ -z "$project_id" ]]; then
        print_error "Project ID is required"
        return 1
    fi
    
    # Get project details first for confirmation
    local project_info=$(api_call GET "/projects/$project_id")
    if ! echo "$project_info" | jq -e '.id' >/dev/null; then
        print_error "Project $project_id not found"
        return 1
    fi
    
    local name=$(echo "$project_info" | jq -r '.name // "Unknown"')
    print_warning "Deleting project $project_id: $name"
    
    local response=$(api_call DELETE "/projects/$project_id")
    
    if [[ "$response" == "" ]] || echo "$response" | jq -e '.message' >/dev/null 2>&1; then
        print_success "Project $project_id deleted successfully"
    else
        print_error "Failed to delete project: $response"
        return 1
    fi
}

# Legacy support functions (for backward compatibility)
add_task() {
    print_warning "Legacy usage detected. Consider using: $0 add-task -p $1 -t \"$2\""
    cmd_add_task -p "$1" -t "$2" -d "$3" -r "${4:-medium}"
}

list_tasks() {
    print_warning "Legacy usage detected. Consider using: $0 list-tasks"
    cmd_list_tasks "$@"
}

update_task() {
    print_warning "Legacy usage detected. Consider using: $0 update-task -i $1 -s $2"
    cmd_update_task -i "$1" -s "$2"
}

# Legacy setup function
setup() {
    print_info "Database tables are automatically created by the API service"
    check_deps
    print_success "API is healthy and ready to use"
}

# Main command dispatcher
main() {
    if [[ $# -eq 0 ]]; then
        cat <<EOF
${BLUE}AI Project Management CLI v2.2 (Enhanced with Projects)${NC}

Usage: $0 <command> [options]

Project Commands:
  list-projects  List all projects
  add-project    Create a new project
  delete-project Delete a project

Task Commands:
  list-tasks     List tasks
  add-task       Add a new task  
  update-task    Update task status
  delete-task    Delete a task

System Commands:
  setup          Check API health
  help           Show this help

For command-specific help: $0 <command> -h

Examples:
  $0 list-tasks -v
  $0 add-task -p 1 -t "Fix bug" -r high
  $0 update-task -i 42 -s done
  $0 delete-task -i 42
  $0 list-projects
  $0 add-project -n "New Project" -d "Project description"
  $0 delete-project -i 1

Legacy format still supported:
  $0 add-task PROJECT_ID "Title" "Description" priority
  $0 update-task TASK_ID STATUS
EOF
        return
    fi
    
    local command="$1"
    shift
    
    # Reset getopts
    OPTIND=1
    
    case "$command" in
        list-tasks) check_deps; cmd_list_tasks "$@" ;;
        add-task) check_deps; cmd_add_task "$@" ;;
        update-task) check_deps; cmd_update_task "$@" ;;
        delete-task) check_deps; cmd_delete_task "$@" ;;
        list-projects) check_deps; cmd_list_projects "$@" ;;
        add-project) check_deps; cmd_add_project "$@" ;;
        delete-project) check_deps; cmd_delete_project "$@" ;;
        setup) setup ;;
        help) main ;;
        # Legacy support
        list_tasks) check_deps; list_tasks "$@" ;;
        update_task) check_deps; update_task "$@" ;;
        *) print_error "Unknown command: $command"; main; return 1 ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
