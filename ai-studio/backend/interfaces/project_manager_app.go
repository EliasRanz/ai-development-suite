package interfaces

import (
	"context"
	"fmt"

	"github.com/ai-studio/backend/domain"
)

// ProjectManagerApp handles project management functionality for Wails
type ProjectManagerApp struct {
	ctx            context.Context
	projectService domain.ProjectService
}

// NewProjectManagerApp creates a new project manager app instance
func NewProjectManagerApp(projectService domain.ProjectService) *ProjectManagerApp {
	return &ProjectManagerApp{
		projectService: projectService,
	}
}

// Startup is called when the app context is ready
func (p *ProjectManagerApp) Startup(ctx context.Context) {
	p.ctx = ctx
}

// Project Management Methods exposed to frontend

// GetAllProjects returns all projects
func (p *ProjectManagerApp) GetAllProjects() ([]*domain.Project, error) {
	return p.projectService.GetAllProjects()
}

// GetProject returns a specific project by ID
func (p *ProjectManagerApp) GetProject(id int) (*domain.Project, error) {
	return p.projectService.GetProject(id)
}

// CreateProject creates a new project
func (p *ProjectManagerApp) CreateProject(name, description string) (*domain.Project, error) {
	return p.projectService.CreateProject(name, description)
}

// UpdateProjectStatus updates a project's status
func (p *ProjectManagerApp) UpdateProjectStatus(id int, status string) error {
	return p.projectService.UpdateProjectStatus(id, status)
}

// Task Management Methods

// GetAllTasks returns all tasks across all projects
func (p *ProjectManagerApp) GetAllTasks() ([]*domain.Task, error) {
	return p.projectService.GetAllTasks()
}

// GetTasksByProject returns all tasks for a specific project
func (p *ProjectManagerApp) GetTasksByProject(projectID int) ([]*domain.Task, error) {
	return p.projectService.GetTasksByProject(projectID)
}

// GetTask returns a specific task by ID
func (p *ProjectManagerApp) GetTask(id int) (*domain.Task, error) {
	return p.projectService.GetTask(id)
}

// CreateTask creates a new task
func (p *ProjectManagerApp) CreateTask(projectID int, title, description, priority string) (*domain.Task, error) {
	return p.projectService.CreateTask(projectID, title, description, priority)
}

// UpdateTaskStatus updates a task's status
func (p *ProjectManagerApp) UpdateTaskStatus(id int, status string) error {
	return p.projectService.UpdateTaskStatus(id, status)
}

// UpdateTaskPriority updates a task's priority
func (p *ProjectManagerApp) UpdateTaskPriority(id int, priority string) error {
	return p.projectService.UpdateTaskPriority(id, priority)
}

// Note Management Methods

// AddNote adds a note to a project or task
func (p *ProjectManagerApp) AddNote(projectID int, taskID *int, content string) (*domain.Note, error) {
	return p.projectService.AddNote(projectID, taskID, content)
}

// GetProjectNotes returns all notes for a project
func (p *ProjectManagerApp) GetProjectNotes(projectID int) ([]*domain.Note, error) {
	return p.projectService.GetProjectNotes(projectID)
}

// GetTaskNotes returns all notes for a task
func (p *ProjectManagerApp) GetTaskNotes(taskID int) ([]*domain.Note, error) {
	return p.projectService.GetTaskNotes(taskID)
}

// Statistics Methods

// GetProjectStats returns statistics for a specific project
func (p *ProjectManagerApp) GetProjectStats(projectID int) (*domain.ProjectStats, error) {
	return p.projectService.GetProjectStats(projectID)
}

// GetOverallStats returns overall system statistics
func (p *ProjectManagerApp) GetOverallStats() (*domain.OverallStats, error) {
	return p.projectService.GetOverallStats()
}

// Utility Methods

// GetTaskStatuses returns available task statuses
func (p *ProjectManagerApp) GetTaskStatuses() []string {
	return []string{
		domain.TaskStatusTodo,
		domain.TaskStatusInProgress,
		domain.TaskStatusReview,
		domain.TaskStatusDone,
	}
}

// GetTaskPriorities returns available task priorities
func (p *ProjectManagerApp) GetTaskPriorities() []string {
	return []string{
		domain.TaskPriorityLow,
		domain.TaskPriorityMedium,
		domain.TaskPriorityHigh,
		domain.TaskPriorityUrgent,
	}
}

// GetProjectStatuses returns available project statuses
func (p *ProjectManagerApp) GetProjectStatuses() []string {
	return []string{
		domain.ProjectStatusActive,
		domain.ProjectStatusComplete,
		domain.ProjectStatusArchived,
	}
}

// InitializeDatabase initializes the database tables
func (p *ProjectManagerApp) InitializeDatabase() error {
	// This would be called during app startup to ensure tables exist
	// Implementation depends on how you handle database initialization
	return nil
}

// Dashboard Data - useful for overview pages

// GetDashboardData returns combined data for dashboard view
func (p *ProjectManagerApp) GetDashboardData() (*DashboardData, error) {
	projects, err := p.projectService.GetAllProjects()
	if err != nil {
		return nil, fmt.Errorf("failed to get projects: %w", err)
	}

	tasks, err := p.projectService.GetAllTasks()
	if err != nil {
		return nil, fmt.Errorf("failed to get tasks: %w", err)
	}

	overallStats, err := p.projectService.GetOverallStats()
	if err != nil {
		return nil, fmt.Errorf("failed to get overall stats: %w", err)
	}

	return &DashboardData{
		Projects:     projects,
		RecentTasks:  getRecentTasks(tasks, 10),
		OverallStats: overallStats,
	}, nil
}

// DashboardData represents data for the main dashboard
type DashboardData struct {
	Projects     []*domain.Project      `json:"projects"`
	RecentTasks  []*domain.Task         `json:"recent_tasks"`
	OverallStats *domain.OverallStats   `json:"overall_stats"`
}

// Helper function to get recent tasks (could be moved to service layer)
func getRecentTasks(tasks []*domain.Task, limit int) []*domain.Task {
	if len(tasks) <= limit {
		return tasks
	}
	return tasks[:limit]
}
