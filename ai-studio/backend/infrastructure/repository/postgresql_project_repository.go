package infrastructure

import (
	"database/sql"
	"fmt"
	"time"

	"github.com/ai-studio/backend/domain"
	_ "github.com/lib/pq"
)

type PostgreSQLProjectRepository struct {
	db *sql.DB
}

func NewPostgreSQLProjectRepository(db *sql.DB) *PostgreSQLProjectRepository {
	return &PostgreSQLProjectRepository{db: db}
}

// Initialize creates the required tables if they don't exist
func (r *PostgreSQLProjectRepository) Initialize() error {
	queries := []string{
		`CREATE TABLE IF NOT EXISTS projects (
			id SERIAL PRIMARY KEY,
			name VARCHAR(255) NOT NULL,
			description TEXT,
			status VARCHAR(50) DEFAULT 'active',
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS tasks (
			id SERIAL PRIMARY KEY,
			project_id INTEGER REFERENCES projects(id),
			title VARCHAR(255) NOT NULL,
			description TEXT,
			status VARCHAR(50) DEFAULT 'todo',
			priority VARCHAR(20) DEFAULT 'medium',
			assigned_to VARCHAR(100),
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
			updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
		`CREATE TABLE IF NOT EXISTS notes (
			id SERIAL PRIMARY KEY,
			project_id INTEGER REFERENCES projects(id),
			task_id INTEGER REFERENCES tasks(id),
			content TEXT NOT NULL,
			created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
		)`,
	}

	for _, query := range queries {
		if _, err := r.db.Exec(query); err != nil {
			return fmt.Errorf("failed to create table: %w", err)
		}
	}

	return nil
}

// Project operations
func (r *PostgreSQLProjectRepository) CreateProject(project *domain.Project) error {
	query := `
		INSERT INTO projects (name, description, status)
		VALUES ($1, $2, $3)
		RETURNING id, created_at, updated_at`

	err := r.db.QueryRow(query, project.Name, project.Description, project.Status).
		Scan(&project.ID, &project.CreatedAt, &project.UpdatedAt)

	return err
}

func (r *PostgreSQLProjectRepository) GetProject(id int) (*domain.Project, error) {
	project := &domain.Project{}
	query := `SELECT id, name, description, status, created_at, updated_at FROM projects WHERE id = $1`

	err := r.db.QueryRow(query, id).
		Scan(&project.ID, &project.Name, &project.Description, &project.Status, &project.CreatedAt, &project.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return project, nil
}

func (r *PostgreSQLProjectRepository) GetAllProjects() ([]*domain.Project, error) {
	query := `SELECT id, name, description, status, created_at, updated_at FROM projects ORDER BY created_at DESC`

	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var projects []*domain.Project
	for rows.Next() {
		project := &domain.Project{}
		err := rows.Scan(&project.ID, &project.Name, &project.Description, &project.Status, &project.CreatedAt, &project.UpdatedAt)
		if err != nil {
			return nil, err
		}
		projects = append(projects, project)
	}

	return projects, nil
}

func (r *PostgreSQLProjectRepository) UpdateProject(project *domain.Project) error {
	query := `
		UPDATE projects 
		SET name = $1, description = $2, status = $3, updated_at = CURRENT_TIMESTAMP
		WHERE id = $4`

	_, err := r.db.Exec(query, project.Name, project.Description, project.Status, project.ID)
	return err
}

func (r *PostgreSQLProjectRepository) DeleteProject(id int) error {
	query := `DELETE FROM projects WHERE id = $1`
	_, err := r.db.Exec(query, id)
	return err
}

// Task operations
func (r *PostgreSQLProjectRepository) CreateTask(task *domain.Task) error {
	query := `
		INSERT INTO tasks (project_id, title, description, status, priority, assigned_to)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id, created_at, updated_at`

	err := r.db.QueryRow(query, task.ProjectID, task.Title, task.Description, task.Status, task.Priority, task.AssignedTo).
		Scan(&task.ID, &task.CreatedAt, &task.UpdatedAt)

	return err
}

func (r *PostgreSQLProjectRepository) GetTask(id int) (*domain.Task, error) {
	task := &domain.Task{}
	query := `SELECT id, project_id, title, description, status, priority, assigned_to, created_at, updated_at FROM tasks WHERE id = $1`

	err := r.db.QueryRow(query, id).
		Scan(&task.ID, &task.ProjectID, &task.Title, &task.Description, &task.Status, &task.Priority, &task.AssignedTo, &task.CreatedAt, &task.UpdatedAt)

	if err != nil {
		return nil, err
	}

	return task, nil
}

func (r *PostgreSQLProjectRepository) GetTasksByProject(projectID int) ([]*domain.Task, error) {
	query := `SELECT id, project_id, title, description, status, priority, assigned_to, created_at, updated_at FROM tasks WHERE project_id = $1 ORDER BY created_at DESC`

	rows, err := r.db.Query(query, projectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []*domain.Task
	for rows.Next() {
		task := &domain.Task{}
		err := rows.Scan(&task.ID, &task.ProjectID, &task.Title, &task.Description, &task.Status, &task.Priority, &task.AssignedTo, &task.CreatedAt, &task.UpdatedAt)
		if err != nil {
			return nil, err
		}
		tasks = append(tasks, task)
	}

	return tasks, nil
}

func (r *PostgreSQLProjectRepository) GetAllTasks() ([]*domain.Task, error) {
	query := `
		SELECT t.id, t.project_id, t.title, t.description, t.status, t.priority, t.assigned_to, t.created_at, t.updated_at
		FROM tasks t 
		ORDER BY t.created_at DESC`

	rows, err := r.db.Query(query)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var tasks []*domain.Task
	for rows.Next() {
		task := &domain.Task{}
		err := rows.Scan(&task.ID, &task.ProjectID, &task.Title, &task.Description, &task.Status, &task.Priority, &task.AssignedTo, &task.CreatedAt, &task.UpdatedAt)
		if err != nil {
			return nil, err
		}
		tasks = append(tasks, task)
	}

	return tasks, nil
}

func (r *PostgreSQLProjectRepository) UpdateTask(task *domain.Task) error {
	query := `
		UPDATE tasks 
		SET title = $1, description = $2, status = $3, priority = $4, assigned_to = $5, updated_at = CURRENT_TIMESTAMP
		WHERE id = $6`

	_, err := r.db.Exec(query, task.Title, task.Description, task.Status, task.Priority, task.AssignedTo, task.ID)
	return err
}

func (r *PostgreSQLProjectRepository) DeleteTask(id int) error {
	query := `DELETE FROM tasks WHERE id = $1`
	_, err := r.db.Exec(query, id)
	return err
}

// Note operations
func (r *PostgreSQLProjectRepository) CreateNote(note *domain.Note) error {
	query := `
		INSERT INTO notes (project_id, task_id, content)
		VALUES ($1, $2, $3)
		RETURNING id, created_at`

	err := r.db.QueryRow(query, note.ProjectID, note.TaskID, note.Content).
		Scan(&note.ID, &note.CreatedAt)

	return err
}

func (r *PostgreSQLProjectRepository) GetNotesByProject(projectID int) ([]*domain.Note, error) {
	query := `SELECT id, project_id, task_id, content, created_at FROM notes WHERE project_id = $1 ORDER BY created_at DESC`

	rows, err := r.db.Query(query, projectID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var notes []*domain.Note
	for rows.Next() {
		note := &domain.Note{}
		err := rows.Scan(&note.ID, &note.ProjectID, &note.TaskID, &note.Content, &note.CreatedAt)
		if err != nil {
			return nil, err
		}
		notes = append(notes, note)
	}

	return notes, nil
}

func (r *PostgreSQLProjectRepository) GetNotesByTask(taskID int) ([]*domain.Note, error) {
	query := `SELECT id, project_id, task_id, content, created_at FROM notes WHERE task_id = $1 ORDER BY created_at DESC`

	rows, err := r.db.Query(query, taskID)
	if err != nil {
		return nil, err
	}
	defer rows.Close()

	var notes []*domain.Note
	for rows.Next() {
		note := &domain.Note{}
		err := rows.Scan(&note.ID, &note.ProjectID, &note.TaskID, &note.Content, &note.CreatedAt)
		if err != nil {
			return nil, err
		}
		notes = append(notes, note)
	}

	return notes, nil
}

func (r *PostgreSQLProjectRepository) DeleteNote(id int) error {
	query := `DELETE FROM notes WHERE id = $1`
	_, err := r.db.Exec(query, id)
	return err
}
