#!/bin/bash
# AI Project Management CLI using the API

# API configuration
API_BASE_URL="http://localhost:8000/api"

# Function to make API calls
api_call() {
    local method="$1"
    local endpoint="$2"
    local data="$3"
    
    if [ "$method" = "GET" ]; then
        curl -s "$API_BASE_URL$endpoint"
    elif [ "$method" = "POST" ]; then
        curl -s -X POST "$API_BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    elif [ "$method" = "PUT" ]; then
        curl -s -X PUT "$API_BASE_URL$endpoint" \
            -H "Content-Type: application/json" \
            -d "$data"
    fi
}

# Function to check if API is available
check_api() {
    if ! curl -s "$API_BASE_URL/health" > /dev/null 2>&1; then
        echo "Error: AI Project Manager API is not available at $API_BASE_URL"
        echo "Please start the services with: make ai-pm-start"
        exit 1
    fi
}

# Function to check if jq is available
check_jq() {
    if ! command -v jq >/dev/null 2>&1; then
        echo "Error: jq is required for JSON parsing"
        echo "Please install jq: apt install jq"
        exit 1
    fi
}

# Function to setup (check API health)
create_tables() {
    echo "Database tables are automatically created by the API service."
    echo "No manual setup required!"
    check_api
    echo "API is healthy and ready to use."
}

# Function to add a project
add_project() {
    check_api
    local name="$1"
    local description="$2"
    
    if [ -z "$name" ]; then
        echo "Error: Project name is required"
        exit 1
    fi
    
    local data="{\"name\":\"$name\",\"description\":\"$description\"}"
    local response=$(api_call "POST" "/projects" "$data")
    
    if echo "$response" | grep -q '"id"'; then
        echo "Project '$name' added successfully!"
    else
        echo "Error adding project: $response"
        exit 1
    fi
}

# Function to add a task
add_task() {
    check_api
    local project_id="$1"
    local title="$2"
    local description="$3"
    local priority="${4:-medium}"
    
    if [ -z "$project_id" ] || [ -z "$title" ]; then
        echo "Error: Project ID and title are required"
        exit 1
    fi
    
    local data="{\"project_id\":$project_id,\"title\":\"$title\",\"description\":\"$description\",\"priority\":\"$priority\"}"
    local response=$(api_call "POST" "/tasks" "$data")
    
    if echo "$response" | grep -q '"id"'; then
        echo "Task '$title' added successfully!"
    else
        echo "Error adding task: $response"
        exit 1
    fi
}

# Function to list projects
list_projects() {
    check_api
    check_jq
    echo "Current Projects:"
    local response=$(api_call "GET" "/projects")
    
    if [ "$response" = "[]" ] || [ -z "$response" ]; then
        echo "No projects found."
        return
    fi
    
    echo "$response" | jq -r '
        ["ID", "NAME", "STATUS", "CREATED"] as $headers |
        $headers,
        ["---", "----", "------", "-------"],
        (.[] | [(.id|tostring), .name, .status, (.created_at[:10])])
        | @tsv' | column -t -s $'\t'
}

# Function to list tasks
list_tasks() {
    check_api
    check_jq
    local project_id="$1"
    local endpoint="/tasks"
    
    if [ -n "$project_id" ]; then
        endpoint="/tasks?project_id=$project_id"
        echo "Tasks for project $project_id:"
    else
        echo "All tasks:"
    fi
    
    local response=$(api_call "GET" "$endpoint")
    
    if [ "$response" = "[]" ] || [ -z "$response" ]; then
        echo "No tasks found."
        return
    fi
    
    echo "$response" | jq -r '
        ["ID", "TITLE", "STATUS", "PRIORITY", "CREATED"] as $headers |
        $headers,
        ["---", "-----", "------", "--------", "-------"],
        (.[] | [(.id|tostring), .title, .status, .priority, (.created_at[:10])])
        | @tsv' | column -t -s $'\t'
}

# Function to update task status
update_task_status() {
    check_api
    local task_id="$1"
    local status="$2"
    
    if [ -z "$task_id" ] || [ -z "$status" ]; then
        echo "Error: Task ID and status are required"
        exit 1
    fi
    
    local data="{\"status\":\"$status\"}"
    local response=$(api_call "PUT" "/tasks/$task_id" "$data")
    
    if echo "$response" | grep -q '"id"'; then
        echo "Task $task_id status updated to '$status'!"
    else
        echo "Error updating task: $response"
        exit 1
    fi
}

# Function to add a note (placeholder)
add_note() {
    check_api
    echo "Note: Notes functionality not yet implemented in the API."
    echo "You can add notes manually to task descriptions."
    echo "Requested note: $3"
}

# Function to show dashboard
show_dashboard() {
    check_api
    check_jq
    echo "Project Management Dashboard:"
    local response=$(api_call "GET" "/dashboard")
    
    echo "$response" | jq -r '
        "Total Projects: " + (.total_projects|tostring),
        "",
        "Tasks by Status:",
        (.tasks_by_status | to_entries[] | "  " + .key + ": " + (.value|tostring)),
        "",
        "Recent Tasks:",
        (.recent_tasks[:5][] | "  [" + .status + "] " + .title + " (Project: " + (.project_name // "N/A") + ")")
    '
}

# Help function
show_help() {
    echo "AI Project Management CLI (API-based)"
    echo "Usage: $0 <command> [args...]"
    echo ""
    echo "Commands:"
    echo "  setup                           - Check API service status"
    echo "  dashboard                       - Show project dashboard"
    echo "  add-project <name> <desc>       - Add a new project"
    echo "  add-task <proj_id> <title> <desc> [priority] - Add a task"
    echo "  list-projects                   - List all projects"
    echo "  list-tasks [project_id]         - List tasks (all or by project)"
    echo "  update-task <task_id> <status>  - Update task status"
    echo "  add-note <proj_id> <task_id> <content> - Add a note (placeholder)"
    echo "  help                           - Show this help"
    echo ""
    echo "Task statuses: todo, in_progress, review, done"
    echo "Priorities: low, medium, high, urgent"
    echo ""
    echo "API Endpoint: $API_BASE_URL"
    echo "Requirements: curl, jq"
}

# Main command dispatcher
case "$1" in
    "setup")
        create_tables
        ;;
    "dashboard")
        show_dashboard
        ;;
    "add-project")
        add_project "$2" "$3"
        ;;
    "add-task")
        add_task "$2" "$3" "$4" "$5"
        ;;
    "list-projects")
        list_projects
        ;;
    "list-tasks")
        list_tasks "$2"
        ;;
    "update-task")
        update_task_status "$2" "$3"
        ;;
    "add-note")
        add_note "$2" "$3" "$4"
        ;;
    "help"|"")
        show_help
        ;;
    *)
        echo "Unknown command: $1"
        show_help
        exit 1
        ;;
esac
