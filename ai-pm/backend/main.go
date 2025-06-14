package main

import (
	"database/sql"
	"encoding/json"
	"fmt"
	"log"
	"net/http"
	"os"
	"strconv"
	"strings"
	"time"

	"github.com/gorilla/mux"
	_ "github.com/lib/pq"
	"github.com/rs/cors"
)

type Project struct {
	ID             int        `json:"id"`
	Name           string     `json:"name"`
	Description    string     `json:"description"`
	Status         string     `json:"status"`
	CreatedAt      time.Time  `json:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at"`
	DeletedAt      *time.Time `json:"deleted_at,omitempty"`
	DeletionReason *string    `json:"deletion_reason,omitempty"`
}

type Task struct {
	ID             int        `json:"id"`
	ProjectID      int        `json:"project_id"`
	ProjectName    string     `json:"project_name,omitempty"`
	Title          string     `json:"title"`
	Description    string     `json:"description"`
	Status         string     `json:"status"`
	Priority       string     `json:"priority"`
	IsBlocked      bool       `json:"is_blocked"`
	BlockedReason  *string    `json:"blocked_reason,omitempty"`
	CreatedAt      time.Time  `json:"created_at"`
	UpdatedAt      time.Time  `json:"updated_at"`
	DeletedAt      *time.Time `json:"deleted_at,omitempty"`
	DeletionReason *string    `json:"deletion_reason,omitempty"`
	Notes          []Note     `json:"notes,omitempty"`
}

type Note struct {
	ID        int       `json:"id"`
	ProjectID int       `json:"project_id"`
	TaskID    *int      `json:"task_id"`
	Content   string    `json:"content"`
	CreatedAt time.Time `json:"created_at"`
}

type StatusValue struct {
	ID          int       `json:"id"`
	Key         string    `json:"key"`
	Label       string    `json:"label"`
	Description string    `json:"description"`
	Color       string    `json:"color"`
	SortOrder   int       `json:"sort_order"`
	IsActive    bool      `json:"is_active"`
	CreatedAt   time.Time `json:"created_at"`
}

type PriorityValue struct {
	ID          int       `json:"id"`
	Key         string    `json:"key"`
	Label       string    `json:"label"`
	Description string    `json:"description"`
	Color       string    `json:"color"`
	Icon        string    `json:"icon"`
	Level       int       `json:"level"`
	IsActive    bool      `json:"is_active"`
	CreatedAt   time.Time `json:"created_at"`
}

type DashboardData struct {
	TotalProjects int            `json:"total_projects"`
	TasksByStatus map[string]int `json:"tasks_by_status"`
	RecentTasks   []Task         `json:"recent_tasks"`
}

type ProjectManager struct {
	db *sql.DB
}

func NewProjectManager() *ProjectManager {
	dbHost := getEnv("AI_PM_DB_HOST", "localhost")
	dbPort := getEnv("AI_PM_DB_PORT", "5432")
	dbUser := getEnv("AI_PM_DB_USER", "aipm")
	dbPassword := getEnv("AI_PM_DB_PASSWORD", "aipm123")
	dbName := getEnv("AI_PM_DB_NAME", "ai_project_manager")

	connStr := fmt.Sprintf("host=%s port=%s user=%s password=%s dbname=%s sslmode=disable",
		dbHost, dbPort, dbUser, dbPassword, dbName)

	db, err := sql.Open("postgres", connStr)
	if err != nil {
		log.Fatal("Failed to connect to database:", err)
	}

	if err = db.Ping(); err != nil {
		log.Fatal("Failed to ping database:", err)
	}

	log.Println("Connected to database successfully")
	return &ProjectManager{db: db}
}

func getEnv(key, defaultValue string) string {
	if value := os.Getenv(key); value != "" {
		return value
	}
	return defaultValue
}

func (pm *ProjectManager) GetProjects(w http.ResponseWriter, r *http.Request) {
	rows, err := pm.db.Query("SELECT id, name, description, status, created_at, updated_at FROM projects WHERE deleted_at IS NULL ORDER BY created_at DESC")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var projects []Project
	for rows.Next() {
		var p Project
		err := rows.Scan(&p.ID, &p.Name, &p.Description, &p.Status, &p.CreatedAt, &p.UpdatedAt)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		projects = append(projects, p)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(projects)
}

func (pm *ProjectManager) CreateProject(w http.ResponseWriter, r *http.Request) {
	var p Project
	if err := json.NewDecoder(r.Body).Decode(&p); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if p.Name == "" {
		http.Error(w, "Project name is required", http.StatusBadRequest)
		return
	}

	err := pm.db.QueryRow(
		"INSERT INTO projects (name, description) VALUES ($1, $2) RETURNING id, created_at, updated_at",
		p.Name, p.Description,
	).Scan(&p.ID, &p.CreatedAt, &p.UpdatedAt)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	p.Status = "active"
	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(p)
}

func (pm *ProjectManager) GetProject(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	projectID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid project ID", http.StatusBadRequest)
		return
	}

	var p Project
	err = pm.db.QueryRow("SELECT id, name, description, status, created_at, updated_at FROM projects WHERE id = $1 AND deleted_at IS NULL", projectID).
		Scan(&p.ID, &p.Name, &p.Description, &p.Status, &p.CreatedAt, &p.UpdatedAt)

	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Project not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(p)
}

func (pm *ProjectManager) GetTasks(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")
	status := r.URL.Query().Get("status")

	query := `
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.is_blocked, t.blocked_reason, t.created_at, t.updated_at, p.name
		FROM tasks t 
		JOIN projects p ON t.project_id = p.id 
		WHERE t.deleted_at IS NULL AND p.deleted_at IS NULL
	`
	args := []interface{}{}
	conditions := []string{}

	if projectID != "" {
		conditions = append(conditions, fmt.Sprintf("t.project_id = $%d", len(args)+1))
		args = append(args, projectID)
	}

	if status != "" {
		conditions = append(conditions, fmt.Sprintf("t.status = $%d", len(args)+1))
		args = append(args, status)
	}

	if len(conditions) > 0 {
		for _, condition := range conditions {
			query += " AND " + condition
		}
	}

	query += " ORDER BY t.created_at DESC"

	rows, err := pm.db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var tasks []Task
	for rows.Next() {
		var t Task
		var isBlocked sql.NullBool
		err := rows.Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &isBlocked, &t.BlockedReason, &t.CreatedAt, &t.UpdatedAt, &t.ProjectName)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// Handle nullable boolean - default to false if null
		if isBlocked.Valid {
			t.IsBlocked = isBlocked.Bool
		} else {
			t.IsBlocked = false
		}

		// Fetch notes for this task
		notes, err := pm.getNotesForTask(t.ID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		t.Notes = notes

		tasks = append(tasks, t)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(tasks)
}

func (pm *ProjectManager) CreateTask(w http.ResponseWriter, r *http.Request) {
	var t Task
	if err := json.NewDecoder(r.Body).Decode(&t); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if t.ProjectID == 0 || t.Title == "" {
		http.Error(w, "Project ID and title are required", http.StatusBadRequest)
		return
	}

	if t.Priority == "" {
		t.Priority = "medium"
	}

	err := pm.db.QueryRow(
		"INSERT INTO tasks (project_id, title, description, priority) VALUES ($1, $2, $3, $4) RETURNING id, status, created_at, updated_at",
		t.ProjectID, t.Title, t.Description, t.Priority,
	).Scan(&t.ID, &t.Status, &t.CreatedAt, &t.UpdatedAt)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(t)
}

func (pm *ProjectManager) GetTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	var t Task
	err = pm.db.QueryRow(`
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.created_at, t.updated_at, p.name
		FROM tasks t 
		JOIN projects p ON t.project_id = p.id 
		WHERE t.id = $1 AND t.deleted_at IS NULL AND p.deleted_at IS NULL`, taskID).
		Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &t.CreatedAt, &t.UpdatedAt, &t.ProjectName)

	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Task not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(t)
}

func (pm *ProjectManager) UpdateTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	var updates map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&updates); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Build dynamic update query
	setParts := []string{}
	args := []interface{}{}
	argCount := 1

	// Handle soft deletion
	isDeleting := false
	if status, ok := updates["status"].(string); ok && status == "deleted" {
		isDeleting = true
		setParts = append(setParts, fmt.Sprintf("status = $%d", argCount))
		args = append(args, status)
		argCount++

		setParts = append(setParts, fmt.Sprintf("deleted_at = $%d", argCount))
		args = append(args, time.Now())
		argCount++

		if deletionReason, ok := updates["deletion_reason"].(string); ok && deletionReason != "" {
			setParts = append(setParts, fmt.Sprintf("deletion_reason = $%d", argCount))
			args = append(args, deletionReason)
			argCount++
		}
	}

	// Handle regular field updates (skip if we're deleting)
	if !isDeleting {
		for field, value := range updates {
			switch field {
			case "title", "description", "status", "priority":
				setParts = append(setParts, fmt.Sprintf("%s = $%d", field, argCount))
				args = append(args, value)
				argCount++
			}
		}
	}

	if len(setParts) == 0 {
		http.Error(w, "No valid fields to update", http.StatusBadRequest)
		return
	}

	setParts = append(setParts, "updated_at = CURRENT_TIMESTAMP")
	args = append(args, taskID)

	query := fmt.Sprintf("UPDATE tasks SET %s WHERE id = $%d RETURNING id, project_id, title, description, status, priority, is_blocked, blocked_reason, created_at, updated_at, deleted_at, deletion_reason",
		strings.Join(setParts, ", "), argCount)

	var t Task
	var isBlocked sql.NullBool
	var deletedAt sql.NullTime
	var deletionReason sql.NullString
	err = pm.db.QueryRow(query, args...).Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &isBlocked, &t.BlockedReason, &t.CreatedAt, &t.UpdatedAt, &deletedAt, &deletionReason)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Task not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	// Handle nullable boolean - default to false if null
	if isBlocked.Valid {
		t.IsBlocked = isBlocked.Bool
	} else {
		t.IsBlocked = false
	}

	// Handle nullable timestamp
	if deletedAt.Valid {
		t.DeletedAt = &deletedAt.Time
	}

	// Handle nullable deletion reason
	if deletionReason.Valid {
		t.DeletionReason = &deletionReason.String
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(t)
}

func (pm *ProjectManager) BlockTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	var requestBody struct {
		Reason string `json:"reason"`
	}
	if err := json.NewDecoder(r.Body).Decode(&requestBody); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if requestBody.Reason == "" {
		http.Error(w, "Reason is required for blocking a task", http.StatusBadRequest)
		return
	}

	query := `UPDATE tasks SET is_blocked = TRUE, blocked_reason = $1, updated_at = CURRENT_TIMESTAMP 
			  WHERE id = $2 RETURNING id, project_id, title, description, status, priority, is_blocked, blocked_reason, created_at, updated_at`

	var t Task
	err = pm.db.QueryRow(query, requestBody.Reason, taskID).Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &t.IsBlocked, &t.BlockedReason, &t.CreatedAt, &t.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Task not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(t)
}

func (pm *ProjectManager) UnblockTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	query := `UPDATE tasks SET is_blocked = FALSE, blocked_reason = NULL, updated_at = CURRENT_TIMESTAMP 
			  WHERE id = $1 RETURNING id, project_id, title, description, status, priority, is_blocked, blocked_reason, created_at, updated_at`

	var t Task
	err = pm.db.QueryRow(query, taskID).Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &t.IsBlocked, &t.BlockedReason, &t.CreatedAt, &t.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Task not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(t)
}

func (pm *ProjectManager) UpdateProject(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	projectID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid project ID", http.StatusBadRequest)
		return
	}

	var updates map[string]interface{}
	if err := json.NewDecoder(r.Body).Decode(&updates); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Build dynamic update query
	setParts := []string{}
	args := []interface{}{}
	argCount := 1

	for field, value := range updates {
		switch field {
		case "name", "description", "status":
			setParts = append(setParts, fmt.Sprintf("%s = $%d", field, argCount))
			args = append(args, value)
			argCount++
		}
	}

	if len(setParts) == 0 {
		http.Error(w, "No valid fields to update", http.StatusBadRequest)
		return
	}

	setParts = append(setParts, "updated_at = CURRENT_TIMESTAMP")
	query := fmt.Sprintf("UPDATE projects SET %s WHERE id = $%d AND deleted_at IS NULL RETURNING id, name, description, status, created_at, updated_at",
		strings.Join(setParts, ", "), argCount)
	args = append(args, projectID)

	var p Project
	err = pm.db.QueryRow(query, args...).Scan(&p.ID, &p.Name, &p.Description, &p.Status, &p.CreatedAt, &p.UpdatedAt)
	if err != nil {
		if err == sql.ErrNoRows {
			http.Error(w, "Project not found", http.StatusNotFound)
		} else {
			http.Error(w, err.Error(), http.StatusInternalServerError)
		}
		return
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(p)
}

// DeleteProject soft deletes a project
func (pm *ProjectManager) DeleteProject(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	projectID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid project ID", http.StatusBadRequest)
		return
	}

	var deleteRequest struct {
		Reason string `json:"reason"`
	}
	if err := json.NewDecoder(r.Body).Decode(&deleteRequest); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if deleteRequest.Reason == "" {
		http.Error(w, "Deletion reason is required", http.StatusBadRequest)
		return
	}

	// Soft delete the project and all its tasks
	tx, err := pm.db.Begin()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer tx.Rollback()

	// Update project
	_, err = tx.Exec("UPDATE projects SET deleted_at = CURRENT_TIMESTAMP, deletion_reason = $1 WHERE id = $2 AND deleted_at IS NULL",
		deleteRequest.Reason, projectID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Update all tasks in the project
	_, err = tx.Exec("UPDATE tasks SET deleted_at = CURRENT_TIMESTAMP, deletion_reason = $1 WHERE project_id = $2 AND deleted_at IS NULL",
		"Project deleted: "+deleteRequest.Reason, projectID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if err = tx.Commit(); err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// DeleteTask soft deletes a task
func (pm *ProjectManager) DeleteTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	var deleteRequest struct {
		Reason string `json:"reason"`
	}
	if err := json.NewDecoder(r.Body).Decode(&deleteRequest); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if deleteRequest.Reason == "" {
		http.Error(w, "Deletion reason is required", http.StatusBadRequest)
		return
	}

	result, err := pm.db.Exec("UPDATE tasks SET deleted_at = CURRENT_TIMESTAMP, deletion_reason = $1 WHERE id = $2 AND deleted_at IS NULL",
		deleteRequest.Reason, taskID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if rowsAffected == 0 {
		http.Error(w, "Task not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

// GetNotes retrieves notes, optionally filtered by task_id
func (pm *ProjectManager) GetNotes(w http.ResponseWriter, r *http.Request) {
	taskID := r.URL.Query().Get("task_id")

	query := `
		SELECT n.id, n.project_id, n.task_id, n.content, n.created_at
		FROM notes n
		WHERE 1=1
	`
	args := []interface{}{}

	if taskID != "" {
		query += " AND n.task_id = $1"
		args = append(args, taskID)
	}

	query += " ORDER BY n.created_at DESC"

	rows, err := pm.db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var notes []Note = make([]Note, 0) // Initialize empty slice instead of nil
	for rows.Next() {
		var note Note
		err := rows.Scan(&note.ID, &note.ProjectID, &note.TaskID, &note.Content, &note.CreatedAt)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		notes = append(notes, note)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(notes)
}

// CreateNote creates a new note
func (pm *ProjectManager) CreateNote(w http.ResponseWriter, r *http.Request) {
	var note Note
	if err := json.NewDecoder(r.Body).Decode(&note); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	if note.Content == "" {
		http.Error(w, "Content is required", http.StatusBadRequest)
		return
	}

	// If task_id is provided, get the project_id from the task
	if note.TaskID != nil {
		err := pm.db.QueryRow("SELECT project_id FROM tasks WHERE id = $1 AND deleted_at IS NULL", *note.TaskID).Scan(&note.ProjectID)
		if err != nil {
			if err == sql.ErrNoRows {
				http.Error(w, "Task not found", http.StatusNotFound)
			} else {
				http.Error(w, err.Error(), http.StatusInternalServerError)
			}
			return
		}
	} else if note.ProjectID == 0 {
		http.Error(w, "Either task_id or project_id is required", http.StatusBadRequest)
		return
	}

	err := pm.db.QueryRow(
		"INSERT INTO notes (project_id, task_id, content) VALUES ($1, $2, $3) RETURNING id, created_at",
		note.ProjectID, note.TaskID, note.Content,
	).Scan(&note.ID, &note.CreatedAt)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	w.Header().Set("Content-Type", "application/json")
	w.WriteHeader(http.StatusCreated)
	json.NewEncoder(w).Encode(note)
}

// DeleteNote deletes a note
func (pm *ProjectManager) DeleteNote(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	noteID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid note ID", http.StatusBadRequest)
		return
	}

	result, err := pm.db.Exec("DELETE FROM notes WHERE id = $1", noteID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if rowsAffected == 0 {
		http.Error(w, "Note not found", http.StatusNotFound)
		return
	}

	w.WriteHeader(http.StatusNoContent)
}

func (pm *ProjectManager) GetDashboard(w http.ResponseWriter, r *http.Request) {
	var dashboard DashboardData
	dashboard.TasksByStatus = make(map[string]int)

	// Get total projects
	err := pm.db.QueryRow("SELECT COUNT(*) FROM projects WHERE deleted_at IS NULL").Scan(&dashboard.TotalProjects)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Get tasks by status
	rows, err := pm.db.Query("SELECT status, COUNT(*) FROM tasks WHERE deleted_at IS NULL GROUP BY status")
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	for rows.Next() {
		var status string
		var count int
		if err := rows.Scan(&status, &count); err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		dashboard.TasksByStatus[status] = count
	}

	// Get recent tasks
	taskRows, err := pm.db.Query(`
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.created_at, t.updated_at, p.name
		FROM tasks t 
		JOIN projects p ON t.project_id = p.id 
		WHERE t.deleted_at IS NULL AND p.deleted_at IS NULL
		ORDER BY t.updated_at DESC 
		LIMIT 10
	`)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer taskRows.Close()

	for taskRows.Next() {
		var t Task
		err := taskRows.Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &t.CreatedAt, &t.UpdatedAt, &t.ProjectName)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		dashboard.RecentTasks = append(dashboard.RecentTasks, t)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(dashboard)
}

func (pm *ProjectManager) HealthCheck(w http.ResponseWriter, r *http.Request) {
	versionInfo := getVersionInfo()

	response := map[string]interface{}{
		"status":    "healthy",
		"timestamp": time.Now(),
		"service":   "ai-project-manager",
		"version":   versionInfo,
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(response)
}

// Version information structure
type VersionInfo struct {
	Version     string `json:"version"`
	BuildTime   string `json:"build_time,omitempty"`
	Environment string `json:"environment"`
	Source      string `json:"source"`
}

// getVersionInfo dynamically determines the version information
func getVersionInfo() VersionInfo {
	version := VersionInfo{
		Environment: getEnvironment(),
	}

	// Try to get version from environment variable first (for Docker builds)
	if envVersion := os.Getenv("APP_VERSION"); envVersion != "" {
		version.Version = envVersion
		version.Source = "environment"
		if buildTime := os.Getenv("BUILD_TIME"); buildTime != "" {
			version.BuildTime = buildTime
		}
		return version
	}

	// Fallback to development version with timestamp
	version.Version = fmt.Sprintf("dev-%d", time.Now().Unix())
	version.Source = "fallback"
	return version
}

// getEnvironment determines the current environment
func getEnvironment() string {
	if env := os.Getenv("ENVIRONMENT"); env != "" {
		return env
	}
	if env := os.Getenv("NODE_ENV"); env != "" {
		return env
	}
	// Check if we're running in Docker
	if _, err := os.Stat("/.dockerenv"); err == nil {
		return "docker"
	}
	return "development"
}

// Database initialization
func (pm *ProjectManager) initDatabase() {
	// Create projects table
	projectsTable := `
	CREATE TABLE IF NOT EXISTS projects (
		id SERIAL PRIMARY KEY,
		name VARCHAR(255) NOT NULL,
		description TEXT,
		status VARCHAR(50) NOT NULL DEFAULT 'active',
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP NULL,
		deletion_reason TEXT NULL
	)`

	// Create tasks table
	tasksTable := `
	CREATE TABLE IF NOT EXISTS tasks (
		id SERIAL PRIMARY KEY,
		project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
		title VARCHAR(255) NOT NULL,
		description TEXT,
		status VARCHAR(50) NOT NULL DEFAULT 'todo',
		priority VARCHAR(50) NOT NULL DEFAULT 'medium',
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
		deleted_at TIMESTAMP NULL,
		deletion_reason TEXT NULL
	)`

	// Create notes table
	notesTable := `
	CREATE TABLE IF NOT EXISTS notes (
		id SERIAL PRIMARY KEY,
		project_id INTEGER REFERENCES projects(id) ON DELETE CASCADE,
		task_id INTEGER REFERENCES tasks(id) ON DELETE CASCADE,
		content TEXT NOT NULL,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`

	// Create status_values table
	statusTable := `
	CREATE TABLE IF NOT EXISTS status_values (
		id SERIAL PRIMARY KEY,
		key VARCHAR(50) UNIQUE NOT NULL,
		label VARCHAR(100) NOT NULL,
		description TEXT,
		color VARCHAR(7) NOT NULL,
		sort_order INTEGER NOT NULL DEFAULT 0,
		is_active BOOLEAN NOT NULL DEFAULT true,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`

	// Create priority_values table
	priorityTable := `
	CREATE TABLE IF NOT EXISTS priority_values (
		id SERIAL PRIMARY KEY,
		key VARCHAR(50) UNIQUE NOT NULL,
		label VARCHAR(100) NOT NULL,
		description TEXT,
		color VARCHAR(7) NOT NULL,
		icon VARCHAR(10),
		level INTEGER NOT NULL DEFAULT 1,
		is_active BOOLEAN NOT NULL DEFAULT true,
		created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
	)`

	// Execute table creation
	if _, err := pm.db.Exec(projectsTable); err != nil {
		log.Fatal("Failed to create projects table:", err)
	}

	if _, err := pm.db.Exec(tasksTable); err != nil {
		log.Fatal("Failed to create tasks table:", err)
	}

	if _, err := pm.db.Exec(notesTable); err != nil {
		log.Fatal("Failed to create notes table:", err)
	}

	if _, err := pm.db.Exec(statusTable); err != nil {
		log.Fatal("Failed to create status_values table:", err)
	}

	if _, err := pm.db.Exec(priorityTable); err != nil {
		log.Fatal("Failed to create priority_values table:", err)
	}

	// Add blocked columns to tasks table if they don't exist
	alterTasksTable := `
	ALTER TABLE tasks 
	ADD COLUMN IF NOT EXISTS is_blocked BOOLEAN DEFAULT FALSE,
	ADD COLUMN IF NOT EXISTS blocked_reason TEXT NULL`

	if _, err := pm.db.Exec(alterTasksTable); err != nil {
		log.Fatal("Failed to add blocked columns to tasks table:", err)
	}

	// Seed default status values
	pm.seedStatusValues()
	pm.seedPriorityValues()

	log.Println("Database initialized successfully")
}

func (pm *ProjectManager) seedStatusValues() {
	statusValues := []StatusValue{
		{Key: "todo", Label: "To Do", Description: "Tasks that need to be started", Color: "#6B7280", SortOrder: 1, IsActive: true},
		{Key: "in_progress", Label: "In Progress", Description: "Tasks currently being worked on", Color: "#3B82F6", SortOrder: 2, IsActive: true},
		{Key: "review", Label: "Review", Description: "Tasks waiting for review or approval", Color: "#F59E0B", SortOrder: 3, IsActive: true},
		{Key: "done", Label: "Done", Description: "Completed tasks", Color: "#10B981", SortOrder: 4, IsActive: true},
		{Key: "deleted", Label: "Deleted", Description: "Tasks that have been deleted", Color: "#EF4444", SortOrder: 5, IsActive: false}, // Hidden from main board
	}

	for _, status := range statusValues {
		_, err := pm.db.Exec(`
			INSERT INTO status_values (key, label, description, color, sort_order, is_active)
			VALUES ($1, $2, $3, $4, $5, $6)
			ON CONFLICT (key) DO NOTHING`,
			status.Key, status.Label, status.Description, status.Color, status.SortOrder, status.IsActive)
		if err != nil {
			log.Printf("Warning: Failed to seed status value %s: %v", status.Key, err)
		}
	}
}

func (pm *ProjectManager) seedPriorityValues() {
	priorityValues := []PriorityValue{
		{Key: "low", Label: "Low", Description: "Low priority items", Color: "#10B981", Icon: "🟢", Level: 1, IsActive: true},
		{Key: "medium", Label: "Medium", Description: "Medium priority items", Color: "#F59E0B", Icon: "🟡", Level: 2, IsActive: true},
		{Key: "high", Label: "High", Description: "High priority items", Color: "#F97316", Icon: "🟠", Level: 3, IsActive: true},
		{Key: "urgent", Label: "Urgent", Description: "Urgent items requiring immediate attention", Color: "#EF4444", Icon: "🔴", Level: 4, IsActive: true},
	}

	for _, priority := range priorityValues {
		_, err := pm.db.Exec(`
			INSERT INTO priority_values (key, label, description, color, icon, level, is_active)
			VALUES ($1, $2, $3, $4, $5, $6, $7)
			ON CONFLICT (key) DO NOTHING`,
			priority.Key, priority.Label, priority.Description, priority.Color, priority.Icon, priority.Level, priority.IsActive)
		if err != nil {
			log.Printf("Warning: Failed to seed priority value %s: %v", priority.Key, err)
		}
	}
}

// API endpoints for status and priority values
func (pm *ProjectManager) GetStatusValues(w http.ResponseWriter, r *http.Request) {
	rows, err := pm.db.Query(`
		SELECT id, key, label, description, color, sort_order, is_active, created_at
		FROM status_values 
		WHERE is_active = true AND key != 'deleted'
		ORDER BY sort_order`)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var statusValues []StatusValue
	for rows.Next() {
		var s StatusValue
		err := rows.Scan(&s.ID, &s.Key, &s.Label, &s.Description, &s.Color, &s.SortOrder, &s.IsActive, &s.CreatedAt)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		statusValues = append(statusValues, s)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(statusValues)
}

func (pm *ProjectManager) GetPriorityValues(w http.ResponseWriter, r *http.Request) {
	rows, err := pm.db.Query(`
		SELECT id, key, label, description, color, icon, level, is_active, created_at
		FROM priority_values 
		WHERE is_active = true 
		ORDER BY level`)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var priorityValues []PriorityValue
	for rows.Next() {
		var p PriorityValue
		err := rows.Scan(&p.ID, &p.Key, &p.Label, &p.Description, &p.Color, &p.Icon, &p.Level, &p.IsActive, &p.CreatedAt)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		priorityValues = append(priorityValues, p)
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(priorityValues)
}

func main() {
	pm := NewProjectManager()
	defer pm.db.Close()

	// Initialize database tables and seed data
	pm.initDatabase()

	r := mux.NewRouter()

	// API routes
	api := r.PathPrefix("/api").Subrouter()
	api.HandleFunc("/health", pm.HealthCheck).Methods("GET")
	api.HandleFunc("/dashboard", pm.GetDashboard).Methods("GET")
	api.HandleFunc("/projects", pm.GetProjects).Methods("GET")
	api.HandleFunc("/projects", pm.CreateProject).Methods("POST")
	api.HandleFunc("/projects/{id:[0-9]+}", pm.GetProject).Methods("GET")
	api.HandleFunc("/projects/{id:[0-9]+}", pm.UpdateProject).Methods("PUT")
	api.HandleFunc("/projects/{id:[0-9]+}", pm.DeleteProject).Methods("DELETE")
	api.HandleFunc("/tasks", pm.GetTasks).Methods("GET")
	api.HandleFunc("/tasks", pm.CreateTask).Methods("POST")
	api.HandleFunc("/tasks/deleted", pm.GetDeletedTasks).Methods("GET")
	api.HandleFunc("/tasks/{id:[0-9]+}", pm.GetTask).Methods("GET")
	api.HandleFunc("/tasks/{id:[0-9]+}", pm.UpdateTask).Methods("PUT")
	api.HandleFunc("/tasks/{id:[0-9]+}", pm.DeleteTask).Methods("DELETE")
	api.HandleFunc("/tasks/{id:[0-9]+}/recover", pm.RecoverTask).Methods("POST")
	api.HandleFunc("/tasks/{id:[0-9]+}/block", pm.BlockTask).Methods("POST")
	api.HandleFunc("/tasks/{id:[0-9]+}/unblock", pm.UnblockTask).Methods("POST")
	api.HandleFunc("/status-values", pm.GetStatusValues).Methods("GET")
	api.HandleFunc("/priority-values", pm.GetPriorityValues).Methods("GET")
	api.HandleFunc("/notes", pm.GetNotes).Methods("GET")
	api.HandleFunc("/notes", pm.CreateNote).Methods("POST")
	api.HandleFunc("/notes/{id:[0-9]+}", pm.DeleteNote).Methods("DELETE")
	api.HandleFunc("/tasks-deleted", pm.GetDeletedTasks).Methods("GET")
	api.HandleFunc("/tasks/{id:[0-9]+}/recover", pm.RecoverTask).Methods("POST")

	// CORS
	c := cors.New(cors.Options{
		AllowedOrigins: []string{"*"},
		AllowedMethods: []string{"GET", "POST", "PUT", "DELETE"},
		AllowedHeaders: []string{"*"},
	})

	handler := c.Handler(r)

	port := getEnv("PORT", "8000")
	log.Printf("🚀 AI Project Manager API starting on port %s", port)
	log.Printf("📊 Health check: http://localhost:%s/api/health", port)
	log.Printf("📋 Dashboard: http://localhost:%s/api/dashboard", port)

	log.Fatal(http.ListenAndServe(":"+port, handler))
}

// getNotesForTask fetches all notes for a specific task
func (pm *ProjectManager) getNotesForTask(taskID int) ([]Note, error) {
	query := `
		SELECT id, project_id, task_id, content, created_at 
		FROM notes 
		WHERE task_id = $1 
		ORDER BY created_at DESC
	`

	rows, err := pm.db.Query(query, taskID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var notes []Note
	for rows.Next() {
		var note Note
		err := rows.Scan(&note.ID, &note.ProjectID, &note.TaskID, &note.Content, &note.CreatedAt)
		if err != nil {
			return nil, err
		}
		notes = append(notes, note)
	}

	// Return empty slice instead of nil if no notes found
	if notes == nil {
		notes = []Note{}
	}

	return notes, nil
}

// GetDeletedTasks retrieves all soft-deleted tasks
func (pm *ProjectManager) GetDeletedTasks(w http.ResponseWriter, r *http.Request) {
	projectID := r.URL.Query().Get("project_id")

	query := `
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.is_blocked, t.blocked_reason, t.created_at, t.updated_at, t.deleted_at, t.deletion_reason, p.name
		FROM tasks t 
		JOIN projects p ON t.project_id = p.id 
		WHERE t.deleted_at IS NOT NULL AND p.deleted_at IS NULL
	`
	args := []interface{}{}

	if projectID != "" {
		query += " AND t.project_id = $1"
		args = append(args, projectID)
	}

	query += " ORDER BY t.deleted_at DESC"

	rows, err := pm.db.Query(query, args...)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	defer rows.Close()

	var tasks []Task
	for rows.Next() {
		var t Task
		var isBlocked sql.NullBool
		err := rows.Scan(&t.ID, &t.ProjectID, &t.Title, &t.Description, &t.Status, &t.Priority, &isBlocked, &t.BlockedReason, &t.CreatedAt, &t.UpdatedAt, &t.DeletedAt, &t.DeletionReason, &t.ProjectName)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}

		// Handle nullable boolean - default to false if null
		if isBlocked.Valid {
			t.IsBlocked = isBlocked.Bool
		} else {
			t.IsBlocked = false
		}

		// Fetch notes for this task
		notes, err := pm.getNotesForTask(t.ID)
		if err != nil {
			http.Error(w, err.Error(), http.StatusInternalServerError)
			return
		}
		t.Notes = notes

		tasks = append(tasks, t)
	}

	// Return empty array instead of null if no tasks found
	if tasks == nil {
		tasks = []Task{}
	}

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(tasks)
}

// RecoverTask restores a soft-deleted task
func (pm *ProjectManager) RecoverTask(w http.ResponseWriter, r *http.Request) {
	vars := mux.Vars(r)
	taskID, err := strconv.Atoi(vars["id"])
	if err != nil {
		http.Error(w, "Invalid task ID", http.StatusBadRequest)
		return
	}

	var recoverRequest struct {
		Status string `json:"status"`
	}
	if err := json.NewDecoder(r.Body).Decode(&recoverRequest); err != nil {
		http.Error(w, err.Error(), http.StatusBadRequest)
		return
	}

	// Default to "todo" if no status provided
	if recoverRequest.Status == "" {
		recoverRequest.Status = "todo"
	}

	// Recover the task by clearing deletion fields and setting new status
	result, err := pm.db.Exec(`
		UPDATE tasks 
		SET deleted_at = NULL, deletion_reason = NULL, status = $1, updated_at = CURRENT_TIMESTAMP 
		WHERE id = $2 AND deleted_at IS NOT NULL`,
		recoverRequest.Status, taskID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	rowsAffected, err := result.RowsAffected()
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	if rowsAffected == 0 {
		http.Error(w, "Deleted task not found", http.StatusNotFound)
		return
	}

	// Return the recovered task
	var task Task
	var isBlocked sql.NullBool
	err = pm.db.QueryRow(`
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.is_blocked, t.blocked_reason, t.created_at, t.updated_at, p.name
		FROM tasks t 
		JOIN projects p ON t.project_id = p.id 
		WHERE t.id = $1 AND t.deleted_at IS NULL AND p.deleted_at IS NULL`, taskID).
		Scan(&task.ID, &task.ProjectID, &task.Title, &task.Description, &task.Status, &task.Priority, &isBlocked, &task.BlockedReason, &task.CreatedAt, &task.UpdatedAt, &task.ProjectName)

	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}

	// Handle nullable boolean - default to false if null
	if isBlocked.Valid {
		task.IsBlocked = isBlocked.Bool
	} else {
		task.IsBlocked = false
	}

	// Fetch notes for this task
	notes, err := pm.getNotesForTask(task.ID)
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	task.Notes = notes

	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(task)
}
