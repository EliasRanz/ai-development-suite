#!/bin/bash
# AI Project Management CLI (API-based)

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
    if ! command -v jq > /dev/null 2>&1; then
        echo "Error: jq is required for JSON parsing"
        echo "Please install jq: sudo apt-get install jq"
        exit 1
    fi
}

# Function to create project management tables (now handled by API service)
setup() {
    echo "Database tables are automatically created by the API service."
    echo "No manual setup required!"
    check_api
    echo "✓ API is healthy and ready to use."
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
        echo "✓ Project '$name' added successfully!"
    else
        echo "✗ Error adding project: $response"
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
        echo "✓ Task '$title' added successfully!"
    else
        echo "✗ Error adding task: $response"
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
    
    # Simple table format with jq
    echo
    printf "%-4s %-25s %-10s %-12s\n" "ID" "NAME" "STATUS" "CREATED"
    printf "%-4s %-25s %-10s %-12s\n" "──" "────────────────────────" "──────────" "────────────"
    echo "$response" | jq -r '.[] | "\(.id)\t\(.name)\t\(.status)\t\(.created_at | split("T")[0])"' |
    while IFS=$'\t' read -r id name status created; do
        printf "%-4s %-25s %-10s %-12s\n" "$id" "${name:0:24}" "$status" "$created"
    done
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
    
    # Simple table format with jq
    echo
    printf "%-4s %-35s %-10s %-8s %-12s\n" "ID" "TITLE" "STATUS" "PRIORITY" "CREATED"
    printf "%-4s %-35s %-10s %-8s %-12s\n" "──" "───────────────────────────────────" "──────────" "────────" "────────────"
    echo "$response" | jq -r '.[] | "\(.id)\t\(.title)\t\(.status)\t\(.priority)\t\(.created_at | split("T")[0])"' |
    while IFS=$'\t' read -r id title status priority created; do
        printf "%-4s %-35s %-10s %-8s %-12s\n" "$id" "${title:0:34}" "$status" "$priority" "$created"
    done
}

# Function to update task status
update_task() {
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
        echo "✓ Task $task_id status updated to '$status'!"
    else
        echo "✗ Error updating task: $response"
        exit 1
    fi
}

# Function to add a note (placeholder - would need API endpoint)
add_note() {
    check_api
    echo "Note: Notes functionality not yet implemented in the API."
    echo "You can add notes manually to task descriptions for now."
    echo "Requested note: $3"
}

# Function to show dashboard
dashboard() {
    check_api
    check_jq
    echo "Project Management Dashboard:"
    local response=$(api_call "GET" "/dashboard")
    
    if echo "$response" | jq -e '.total_projects' > /dev/null 2>&1; then
        echo
        echo "📊 Total Projects: $(echo "$response" | jq -r '.total_projects')"
        echo
        echo "📋 Tasks by Status:"
        echo "$response" | jq -r '.tasks_by_status | to_entries[] | "  \(.key): \(.value)"'
        echo
        echo "🕒 Recent Tasks:"
        echo "$response" | jq -r '.recent_tasks[:5][] | "  [\(.status)] \(.title) (Project: \(.project_name // "N/A"))"'
    else
        echo "✗ Error parsing dashboard data"
    fi
}

# Function to get a single task
get_task() {
    check_api
    check_jq
    local task_id="$1"
    
    if [ -z "$task_id" ]; then
        echo "Error: Task ID is required"
        exit 1
    fi
    
    local response=$(api_call "GET" "/tasks/$task_id")
    
    if echo "$response" | jq -e '.' > /dev/null 2>&1; then
        echo "Task Details:"
        echo "─────────────"
        echo "$response" | jq -r '"ID: " + (.id | tostring)'
        echo "$response" | jq -r '"Project: " + .project_name'
        echo "$response" | jq -r '"Title: " + .title'
        echo "$response" | jq -r '"Description: " + (.description // "No description")'
        echo "$response" | jq -r '"Status: " + .status'
        echo "$response" | jq -r '"Priority: " + .priority'
        echo "$response" | jq -r '"Created: " + (.created_at | split("T")[0])'
        echo "$response" | jq -r '"Updated: " + (.updated_at | split("T")[0])'
    else
        echo "✗ Error getting task: $response"
        exit 1
    fi
}

# Function to get a single project
get_project() {
    check_api
    check_jq
    local project_id="$1"
    
    if [ -z "$project_id" ]; then
        echo "Error: Project ID is required"
        exit 1
    fi
    
    local response=$(api_call "GET" "/projects/$project_id")
    
    if echo "$response" | jq -e '.' > /dev/null 2>&1; then
        echo "Project Details:"
        echo "────────────────"
        echo "$response" | jq -r '"ID: " + (.id | tostring)'
        echo "$response" | jq -r '"Name: " + .name'
        echo "$response" | jq -r '"Description: " + (.description // "No description")'
        echo "$response" | jq -r '"Status: " + .status'
        echo "$response" | jq -r '"Created: " + (.created_at | split("T")[0])'
        echo "$response" | jq -r '"Updated: " + (.updated_at | split("T")[0])'
    else
        echo "✗ Error getting project: $response"
        exit 1
    fi
}

# Function to edit a task
edit_task() {
    check_api
    local task_id="$1"
    shift
    
    if [ -z "$task_id" ]; then
        echo "Error: Task ID is required"
        echo "Usage: edit-task <task_id> [--title \"new title\"] [--description \"new desc\"] [--priority high|medium|low]"
        exit 1
    fi
    
    local updates="{}"
    while [ $# -gt 0 ]; do
        case "$1" in
            --title)
                updates=$(echo "$updates" | jq --arg title "$2" '. + {title: $title}')
                shift 2
                ;;
            --description)
                updates=$(echo "$updates" | jq --arg desc "$2" '. + {description: $desc}')
                shift 2
                ;;
            --priority)
                updates=$(echo "$updates" | jq --arg priority "$2" '. + {priority: $priority}')
                shift 2
                ;;
            --status)
                updates=$(echo "$updates" | jq --arg status "$2" '. + {status: $status}')
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    if [ "$updates" = "{}" ]; then
        echo "Error: No updates specified"
        echo "Usage: edit-task <task_id> [--title \"new title\"] [--description \"new desc\"] [--priority high|medium|low] [--status todo|in_progress|review|done]"
        exit 1
    fi
    
    local response=$(api_call "PUT" "/tasks/$task_id" "$updates")
    
    if echo "$response" | grep -q '"id"'; then
        echo "✓ Task $task_id updated successfully!"
    else
        echo "✗ Error updating task: $response"
        exit 1
    fi
}

# Function to edit a project
edit_project() {
    check_api
    local project_id="$1"
    shift
    
    if [ -z "$project_id" ]; then
        echo "Error: Project ID is required"
        echo "Usage: edit-project <project_id> [--name \"new name\"] [--description \"new desc\"] [--status active|inactive]"
        exit 1
    fi
    
    local updates="{}"
    while [ $# -gt 0 ]; do
        case "$1" in
            --name)
                updates=$(echo "$updates" | jq --arg name "$2" '. + {name: $name}')
                shift 2
                ;;
            --description)
                updates=$(echo "$updates" | jq --arg desc "$2" '. + {description: $desc}')
                shift 2
                ;;
            --status)
                updates=$(echo "$updates" | jq --arg status "$2" '. + {status: $status}')
                shift 2
                ;;
            *)
                echo "Unknown option: $1"
                exit 1
                ;;
        esac
    done
    
    if [ "$updates" = "{}" ]; then
        echo "Error: No updates specified"
        echo "Usage: edit-project <project_id> [--name \"new name\"] [--description \"new desc\"] [--status active|inactive]"
        exit 1
    fi
    
    local response=$(api_call "PUT" "/projects/$project_id" "$updates")
    
    if echo "$response" | grep -q '"id"'; then
        echo "✓ Project $project_id updated successfully!"
    else
        echo "✗ Error updating project: $response"
        exit 1
    fi
}

# Function to delete a task with confirmation
delete_task() {
    check_api
    local task_id="$1"
    local reason="$2"
    local force="$3"
    
    if [ -z "$task_id" ]; then
        echo "Error: Task ID is required"
        echo "Usage: delete-task <task_id> \"reason\" [--force]"
        exit 1
    fi
    
    if [ -z "$reason" ]; then
        echo "Error: Deletion reason is required"
        echo "Usage: delete-task <task_id> \"reason\" [--force]"
        exit 1
    fi
    
    # Get task details for confirmation
    local task_info=$(api_call "GET" "/tasks/$task_id")
    if ! echo "$task_info" | jq -e '.' > /dev/null 2>&1; then
        echo "✗ Task not found: $task_id"
        exit 1
    fi
    
    local task_title=$(echo "$task_info" | jq -r '.title')
    
    # Show confirmation unless --force is used
    if [ "$force" != "--force" ]; then
        echo "⚠️  WARNING: You are about to delete task #$task_id"
        echo "   Title: $task_title"
        echo "   Reason: $reason"
        echo ""
        read -p "Are you sure? (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Deletion cancelled."
            exit 0
        fi
    fi
    
    local delete_data="{\"reason\":\"$reason\"}"
    local response=$(curl -s -X DELETE "$API_BASE_URL/tasks/$task_id" \
        -H "Content-Type: application/json" \
        -d "$delete_data")
    
    # Check if deletion was successful (no content response)
    if [ -z "$response" ]; then
        echo "✓ Task $task_id deleted successfully!"
    else
        echo "✗ Error deleting task: $response"
        exit 1
    fi
}

# Function to delete a project with confirmation
delete_project() {
    check_api
    local project_id="$1"
    local reason="$2"
    local force="$3"
    
    if [ -z "$project_id" ]; then
        echo "Error: Project ID is required"
        echo "Usage: delete-project <project_id> \"reason\" [--force]"
        exit 1
    fi
    
    if [ -z "$reason" ]; then
        echo "Error: Deletion reason is required"
        echo "Usage: delete-project <project_id> \"reason\" [--force]"
        exit 1
    fi
    
    # Get project details for confirmation
    local project_info=$(api_call "GET" "/projects/$project_id")
    if ! echo "$project_info" | jq -e '.' > /dev/null 2>&1; then
        echo "✗ Project not found: $project_id"
        exit 1
    fi
    
    local project_name=$(echo "$project_info" | jq -r '.name')
    
    # Show confirmation unless --force is used
    if [ "$force" != "--force" ]; then
        echo "⚠️  WARNING: You are about to delete project #$project_id and ALL its tasks"
        echo "   Name: $project_name"
        echo "   Reason: $reason"
        echo ""
        read -p "Are you sure? This will delete ALL tasks in this project! (y/N): " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            echo "Deletion cancelled."
            exit 0
        fi
    fi
    
    local delete_data="{\"reason\":\"$reason\"}"
    local response=$(curl -s -X DELETE "$API_BASE_URL/projects/$project_id" \
        -H "Content-Type: application/json" \
        -d "$delete_data")
    
    # Check if deletion was successful (no content response)
    if [ -z "$response" ]; then
        echo "✓ Project $project_id and all its tasks deleted successfully!"
    else
        echo "✗ Error deleting project: $response"
        exit 1
    fi
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
    echo "  get-task <task_id>              - Get details of a specific task"
    echo "  get-project <project_id>        - Get details of a specific project"
    echo "  edit-task <task_id> [options]   - Edit a task (title, description, priority, status)"
    echo "  edit-project <project_id> [options] - Edit a project (name, description, status)"
    echo "  delete-task <task_id> \"reason\" [--force] - Delete a task"
    echo "  delete-project <project_id> \"reason\" [--force] - Delete a project"
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
        setup
        ;;
    "dashboard")
        dashboard
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
        update_task "$2" "$3"
        ;;
    "add-note")
        add_note "$2" "$3" "$4"
        ;;
    "get-task")
        get_task "$2"
        ;;
    "get-project")
        get_project "$2"
        ;;
    "edit-task")
        edit_task "$2" "${@:3}"
        ;;
    "edit-project")
        edit_project "$2" "${@:3}"
        ;;
    "delete-task")
        delete_task "$2" "$3" "$4"
        ;;
    "delete-project")
        delete_project "$2" "$3" "$4"
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
