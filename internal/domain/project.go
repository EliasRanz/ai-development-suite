package domain

import (
	"time"
)

// Project represents a project in the system
type Project struct {
	ID          int       `json:"id" db:"id"`
	Name        string    `json:"name" db:"name"`
	Description string    `json:"description" db:"description"`
	Status      string    `json:"status" db:"status"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// Task represents a task within a project
type Task struct {
	ID          int       `json:"id" db:"id"`
	ProjectID   int       `json:"project_id" db:"project_id"`
	Title       string    `json:"title" db:"title"`
	Description string    `json:"description" db:"description"`
	Status      string    `json:"status" db:"status"`
	Priority    string    `json:"priority" db:"priority"`
	AssignedTo  string    `json:"assigned_to" db:"assigned_to"`
	CreatedAt   time.Time `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time `json:"updated_at" db:"updated_at"`
}

// Note represents a note or comment on a project or task
type Note struct {
	ID        int       `json:"id" db:"id"`
	ProjectID int       `json:"project_id" db:"project_id"`
	TaskID    *int      `json:"task_id" db:"task_id"` // nullable
	Content   string    `json:"content" db:"content"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
}

// TaskStatus constants
const (
	TaskStatusTodo       = "todo"
	TaskStatusInProgress = "in_progress"
	TaskStatusReview     = "review"
	TaskStatusDone       = "done"
)

// TaskPriority constants
const (
	TaskPriorityLow    = "low"
	TaskPriorityMedium = "medium"
	TaskPriorityHigh   = "high"
	TaskPriorityUrgent = "urgent"
)

// ProjectStatus constants
const (
	ProjectStatusActive   = "active"
	ProjectStatusComplete = "complete"
	ProjectStatusArchived = "archived"
)
