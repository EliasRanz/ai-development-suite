# API Documentation

The AI Project Manager API provides RESTful endpoints for managing projects, tasks, and notes.

## Base Configuration

- **Base URL**: `http://localhost:8001/api` (development)
- **Base URL**: `http://localhost:8000/api` (production)
- **Content-Type**: `application/json`
- **CORS**: Enabled for all origins in development

## Health Check

### GET /api/health
Check if the API service is running.

**Response:**
```json
{
  "service": "ai-project-manager",
  "status": "healthy",
  "timestamp": "2025-06-16T16:51:06.734731938Z",
  "version": {
    "version": "dev-hotreload",
    "build_time": "dynamic",
    "environment": "development",
    "source": "environment"
  }
}
```

## Dashboard

### GET /api/dashboard
Get overview statistics and recent tasks.

**Response:**
```json
{
  "total_projects": 3,
  "tasks_by_status": {
    "deleted": 1,
    "done": 9,
    "review": 1,
    "todo": 35
  },
  "recent_tasks": [...]
}
```

## Projects

### GET /api/projects
List all projects.

**Response:**
```json
[
  {
    "id": 1,
    "name": "Project Management System",
    "description": "Web-based project management for AI development",
    "status": "active",
    "created_at": "2025-06-13T17:37:27.254271Z",
    "updated_at": "2025-06-13T17:37:27.254271Z"
  }
]
```

### POST /api/projects
Create a new project.

**Request Body:**
```json
{
  "name": "New Project",
  "description": "Project description",
  "status": "active"
}
```

**Response:** Returns created project with ID.

### GET /api/projects/{id}
Get specific project details.

### PUT /api/projects/{id}
Update project details.

**Request Body:**
```json
{
  "name": "Updated Name",
  "description": "Updated description",
  "status": "active"
}
```

### DELETE /api/projects/{id}
Soft delete a project (sets deleted_at timestamp).

## Tasks

### GET /api/tasks
List all active tasks.

**Query Parameters:**
- `project_id` (optional): Filter by project ID

**Response:**
```json
[
  {
    "id": 43,
    "project_id": 1,
    "project_name": "Project Management System",
    "title": "Review and Update Documentation",
    "description": "Comprehensive review and update of all documentation...",
    "status": "review",
    "priority": "urgent",
    "is_blocked": false,
    "blocked_reason": null,
    "created_at": "2025-06-14T04:13:15.261117Z",
    "updated_at": "2025-06-16T15:46:59.584624Z",
    "deleted_at": null,
    "deletion_reason": null,
    "notes": [...]
  }
]
```

### POST /api/tasks
Create a new task.

**Request Body:**
```json
{
  "project_id": 1,
  "title": "Task Title",
  "description": "Task description",
  "priority": "medium"
}
```

**Status Values:** `todo`, `in_progress`, `review`, `done`, `blocked`
**Priority Values:** `low`, `medium`, `high`, `urgent`

### GET /api/tasks/{id}
Get specific task details including notes.

### PUT /api/tasks/{id}
Update task details.

**Request Body:**
```json
{
  "title": "Updated Title",
  "description": "Updated description",
  "status": "in_progress",
  "priority": "high"
}
```

### DELETE /api/tasks/{id}
Soft delete a task (moves to deleted status).

**Request Body:**
```json
{
  "deletion_reason": "No longer needed"
}
```

## Deleted Tasks

### GET /api/tasks/deleted
List all soft-deleted tasks.

**Response:** Same format as GET /api/tasks but only deleted tasks.

### POST /api/tasks/{id}/recover
Recover a soft-deleted task.

**Response:** Returns recovered task.

## Task Blocking

### POST /api/tasks/{id}/block
Block a task with reason.

**Request Body:**
```json
{
  "blocked_reason": "Waiting for dependencies"
}
```

### POST /api/tasks/{id}/unblock
Unblock a task.

**Response:** Returns unblocked task.

## Notes

### GET /api/notes
List all notes.

**Query Parameters:**
- `task_id` (optional): Filter by task ID
- `project_id` (optional): Filter by project ID

**Response:**
```json
[
  {
    "id": 47,
    "project_id": 1,
    "task_id": 43,
    "content": "Progress update: Infrastructure cleanup complete",
    "created_at": "2025-06-16T16:55:20.715974Z"
  }
]
```

### POST /api/notes
Create a new note.

**Request Body:**
```json
{
  "project_id": 1,
  "task_id": 43,
  "content": "Note content"
}
```

**Note:** Either `project_id` or `task_id` is required, not both.

### DELETE /api/notes/{id}
Delete a note.

## Metadata

### GET /api/status-values
Get available task status values.

**Response:**
```json
["todo", "in_progress", "review", "done", "blocked"]
```

### GET /api/priority-values
Get available priority values.

**Response:**
```json
["low", "medium", "high", "urgent"]
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid request format",
  "details": "Missing required field: title"
}
```

### 404 Not Found
```json
{
  "error": "Resource not found",
  "details": "Task with ID 999 not found"
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "details": "Database connection failed"
}
```

## CLI Integration

The project includes a CLI script that interacts with these APIs:

```bash
# Health check
./scripts/project-manager.sh setup

# List tasks (uses GET /api/tasks)
./scripts/project-manager.sh list-tasks

# Create task (uses POST /api/tasks)
./scripts/project-manager.sh add-task -p 1 -t "Title" -r high

# Update task status (uses PUT /api/tasks/{id})
./scripts/project-manager.sh update-task -i 42 -s done

# Add note (uses POST /api/notes)
./scripts/project-manager.sh add-note -t 42 -c "Note content"
```

## Development Examples

### Using curl

```bash
# Health check
curl http://localhost:8001/api/health

# Get dashboard
curl http://localhost:8001/api/dashboard | jq .

# Create task
curl -X POST http://localhost:8001/api/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "project_id": 1,
    "title": "Test Task",
    "description": "Test description",
    "priority": "medium"
  }'

# Update task
curl -X PUT http://localhost:8001/api/tasks/43 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "done"
  }'

# Get deleted tasks
curl http://localhost:8001/api/tasks/deleted | jq .

# Recover task
curl -X POST http://localhost:8001/api/tasks/43/recover
```

### Using JavaScript (Frontend)

```javascript
// Configuration
const API_BASE = 'http://localhost:8001/api';

// Get dashboard data
const dashboard = await fetch(`${API_BASE}/dashboard`).then(r => r.json());

// Create task
const task = await fetch(`${API_BASE}/tasks`, {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    project_id: 1,
    title: 'New Task',
    description: 'Task description',
    priority: 'high'
  })
}).then(r => r.json());

// Update task status
await fetch(`${API_BASE}/tasks/${taskId}`, {
  method: 'PUT',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ status: 'done' })
});
```

## Authentication

Currently, the API does not require authentication. This is suitable for development and single-user environments.

For production deployment, consider adding:
- JWT token authentication
- Role-based access control
- API rate limiting
- Request logging and monitoring

## Rate Limiting

No rate limiting is currently implemented. For production use, consider implementing rate limiting to prevent abuse.

## API Versioning

The current API is version 1 (implied). Future versions may include versioning in the URL path (e.g., `/api/v2/tasks`).
