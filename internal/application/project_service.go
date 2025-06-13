package application

import (
	"fmt"
	"time"

	"github.com/ai-launcher/internal/domain"
)

type ProjectServiceImpl struct {
	repo domain.ProjectRepository
}

func NewProjectService(repo domain.ProjectRepository) domain.ProjectService {
	return &ProjectServiceImpl{repo: repo}
}

// Project management
func (s *ProjectServiceImpl) CreateProject(name, description string) (*domain.Project, error) {
	if name == "" {
		return nil, fmt.Errorf("project name is required")
	}

	project := &domain.Project{
		Name:        name,
		Description: description,
		Status:      domain.ProjectStatusActive,
	}

	err := s.repo.CreateProject(project)
	if err != nil {
		return nil, fmt.Errorf("failed to create project: %w", err)
	}

	return project, nil
}

func (s *ProjectServiceImpl) GetProject(id int) (*domain.Project, error) {
	if id <= 0 {
		return nil, fmt.Errorf("invalid project ID")
	}

	return s.repo.GetProject(id)
}

func (s *ProjectServiceImpl) GetAllProjects() ([]*domain.Project, error) {
	return s.repo.GetAllProjects()
}

func (s *ProjectServiceImpl) UpdateProjectStatus(id int, status string) error {
	project, err := s.repo.GetProject(id)
	if err != nil {
		return fmt.Errorf("project not found: %w", err)
	}

	// Validate status
	validStatuses := map[string]bool{
		domain.ProjectStatusActive:   true,
		domain.ProjectStatusComplete: true,
		domain.ProjectStatusArchived: true,
	}

	if !validStatuses[status] {
		return fmt.Errorf("invalid project status: %s", status)
	}

	project.Status = status
	project.UpdatedAt = time.Now()

	return s.repo.UpdateProject(project)
}

// Task management
func (s *ProjectServiceImpl) CreateTask(projectID int, title, description, priority string) (*domain.Task, error) {
	if title == "" {
		return nil, fmt.Errorf("task title is required")
	}

	// Verify project exists
	_, err := s.repo.GetProject(projectID)
	if err != nil {
		return nil, fmt.Errorf("project not found: %w", err)
	}

	// Validate priority
	if priority == "" {
		priority = domain.TaskPriorityMedium
	}

	validPriorities := map[string]bool{
		domain.TaskPriorityLow:    true,
		domain.TaskPriorityMedium: true,
		domain.TaskPriorityHigh:   true,
		domain.TaskPriorityUrgent: true,
	}

	if !validPriorities[priority] {
		return nil, fmt.Errorf("invalid task priority: %s", priority)
	}

	task := &domain.Task{
		ProjectID:   projectID,
		Title:       title,
		Description: description,
		Status:      domain.TaskStatusTodo,
		Priority:    priority,
	}

	err = s.repo.CreateTask(task)
	if err != nil {
		return nil, fmt.Errorf("failed to create task: %w", err)
	}

	return task, nil
}

func (s *ProjectServiceImpl) GetTask(id int) (*domain.Task, error) {
	if id <= 0 {
		return nil, fmt.Errorf("invalid task ID")
	}

	return s.repo.GetTask(id)
}

func (s *ProjectServiceImpl) GetTasksByProject(projectID int) ([]*domain.Task, error) {
	if projectID <= 0 {
		return nil, fmt.Errorf("invalid project ID")
	}

	return s.repo.GetTasksByProject(projectID)
}

func (s *ProjectServiceImpl) GetAllTasks() ([]*domain.Task, error) {
	return s.repo.GetAllTasks()
}

func (s *ProjectServiceImpl) UpdateTaskStatus(id int, status string) error {
	task, err := s.repo.GetTask(id)
	if err != nil {
		return fmt.Errorf("task not found: %w", err)
	}

	// Validate status
	validStatuses := map[string]bool{
		domain.TaskStatusTodo:       true,
		domain.TaskStatusInProgress: true,
		domain.TaskStatusReview:     true,
		domain.TaskStatusDone:       true,
	}

	if !validStatuses[status] {
		return fmt.Errorf("invalid task status: %s", status)
	}

	task.Status = status
	task.UpdatedAt = time.Now()

	return s.repo.UpdateTask(task)
}

func (s *ProjectServiceImpl) UpdateTaskPriority(id int, priority string) error {
	task, err := s.repo.GetTask(id)
	if err != nil {
		return fmt.Errorf("task not found: %w", err)
	}

	// Validate priority
	validPriorities := map[string]bool{
		domain.TaskPriorityLow:    true,
		domain.TaskPriorityMedium: true,
		domain.TaskPriorityHigh:   true,
		domain.TaskPriorityUrgent: true,
	}

	if !validPriorities[priority] {
		return fmt.Errorf("invalid task priority: %s", priority)
	}

	task.Priority = priority
	task.UpdatedAt = time.Now()

	return s.repo.UpdateTask(task)
}

// Note management
func (s *ProjectServiceImpl) AddNote(projectID int, taskID *int, content string) (*domain.Note, error) {
	if content == "" {
		return nil, fmt.Errorf("note content is required")
	}

	// Verify project exists
	_, err := s.repo.GetProject(projectID)
	if err != nil {
		return nil, fmt.Errorf("project not found: %w", err)
	}

	// Verify task exists if taskID is provided
	if taskID != nil && *taskID > 0 {
		_, err := s.repo.GetTask(*taskID)
		if err != nil {
			return nil, fmt.Errorf("task not found: %w", err)
		}
	}

	note := &domain.Note{
		ProjectID: projectID,
		TaskID:    taskID,
		Content:   content,
	}

	err = s.repo.CreateNote(note)
	if err != nil {
		return nil, fmt.Errorf("failed to create note: %w", err)
	}

	return note, nil
}

func (s *ProjectServiceImpl) GetProjectNotes(projectID int) ([]*domain.Note, error) {
	if projectID <= 0 {
		return nil, fmt.Errorf("invalid project ID")
	}

	return s.repo.GetNotesByProject(projectID)
}

func (s *ProjectServiceImpl) GetTaskNotes(taskID int) ([]*domain.Note, error) {
	if taskID <= 0 {
		return nil, fmt.Errorf("invalid task ID")
	}

	return s.repo.GetNotesByTask(taskID)
}

// Statistics and reporting
func (s *ProjectServiceImpl) GetProjectStats(projectID int) (*domain.ProjectStats, error) {
	tasks, err := s.repo.GetTasksByProject(projectID)
	if err != nil {
		return nil, fmt.Errorf("failed to get project tasks: %w", err)
	}

	stats := &domain.ProjectStats{
		ProjectID: projectID,
	}

	for _, task := range tasks {
		stats.TotalTasks++

		switch task.Status {
		case domain.TaskStatusDone:
			stats.CompletedTasks++
		case domain.TaskStatusInProgress:
			stats.InProgressTasks++
		case domain.TaskStatusTodo:
			stats.TodoTasks++
		case domain.TaskStatusReview:
			stats.ReviewTasks++
		}

		switch task.Priority {
		case domain.TaskPriorityHigh:
			stats.HighPriorityTasks++
		case domain.TaskPriorityUrgent:
			stats.UrgentTasks++
		}
	}

	return stats, nil
}

func (s *ProjectServiceImpl) GetOverallStats() (*domain.OverallStats, error) {
	projects, err := s.repo.GetAllProjects()
	if err != nil {
		return nil, fmt.Errorf("failed to get projects: %w", err)
	}

	tasks, err := s.repo.GetAllTasks()
	if err != nil {
		return nil, fmt.Errorf("failed to get tasks: %w", err)
	}

	stats := &domain.OverallStats{}

	// Project stats
	for _, project := range projects {
		stats.TotalProjects++
		if project.Status == domain.ProjectStatusActive {
			stats.ActiveProjects++
		}
	}

	// Task stats
	for _, task := range tasks {
		stats.TotalTasks++

		switch task.Status {
		case domain.TaskStatusDone:
			stats.CompletedTasks++
		case domain.TaskStatusInProgress:
			stats.InProgressTasks++
		}
	}

	return stats, nil
}
