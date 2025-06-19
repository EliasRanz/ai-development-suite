package user

import (
	"fmt"
	"time"
)

// User represents a user in the system
type User struct {
	ID            string    `json:"id" db:"id"`
	Email         string    `json:"email" db:"email"`
	Name          string    `json:"name" db:"name"`
	AvatarURL     string    `json:"avatar_url" db:"avatar_url"`
	Roles         []string  `json:"roles" db:"roles"`
	IsActive      bool      `json:"is_active" db:"is_active"`
	EmailVerified bool      `json:"email_verified" db:"email_verified"`
	LastLoginAt   *time.Time `json:"last_login_at,omitempty" db:"last_login_at"`
	CreatedAt     time.Time `json:"created_at" db:"created_at"`
	UpdatedAt     time.Time `json:"updated_at" db:"updated_at"`
}

// Project represents a project in the system
type Project struct {
	ID          string            `json:"id" db:"id"`
	Name        string            `json:"name" db:"name"`
	Description string            `json:"description" db:"description"`
	UserID      string            `json:"user_id" db:"user_id"`
	Status      string            `json:"status" db:"status"`
	Tags        []string          `json:"tags" db:"tags"`
	Config      map[string]interface{} `json:"config" db:"config"`
	Metadata    map[string]interface{} `json:"metadata" db:"metadata"`
	IsPublic    bool              `json:"is_public" db:"is_public"`
	TemplateID  *string           `json:"template_id,omitempty" db:"template_id"`
	CreatedAt   time.Time         `json:"created_at" db:"created_at"`
	UpdatedAt   time.Time         `json:"updated_at" db:"updated_at"`
}

// Service provides user and project business logic
type Service struct {
	repo        Repository
	projectRepo ProjectRepository
}

// NewService creates a new user service
func NewService(repo Repository) *Service {
	return &Service{
		repo: repo,
	}
}

// NewServiceWithProjects creates a new user service with project repository
func NewServiceWithProjects(repo Repository, projectRepo ProjectRepository) *Service {
	return &Service{
		repo:        repo,
		projectRepo: projectRepo,
	}
}

// GetUser retrieves a user by ID
func (s *Service) GetUser(id string) (*User, error) {
	// TODO: Implement get user logic
	return s.repo.GetByID(id)
}

// UpdateUser updates user information
func (s *Service) UpdateUser(id string, updates map[string]interface{}) (*User, error) {
	// TODO: Implement update user logic
	return s.repo.Update(id, updates)
}

// DeleteUser deletes a user
func (s *Service) DeleteUser(id string) error {
	// TODO: Implement delete user logic
	return s.repo.Delete(id)
}

// ListUsers lists users with pagination
func (s *Service) ListUsers(limit, offset int) ([]*User, error) {
	// TODO: Implement list users logic
	return s.repo.List(limit, offset)
}

// Project Service Methods

// GetProject retrieves a project by ID
func (s *Service) GetProject(id string) (*Project, error) {
	if s.projectRepo == nil {
		return nil, fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.GetByID(id)
}

// CreateProject creates a new project
func (s *Service) CreateProject(project *Project) error {
	if s.projectRepo == nil {
		return fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.Create(project)
}

// UpdateProject updates project information
func (s *Service) UpdateProject(id string, updates map[string]interface{}) (*Project, error) {
	if s.projectRepo == nil {
		return nil, fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.Update(id, updates)
}

// DeleteProject deletes a project
func (s *Service) DeleteProject(id string) error {
	if s.projectRepo == nil {
		return fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.Delete(id)
}

// ListProjects lists projects with pagination
func (s *Service) ListProjects(limit, offset int) ([]*Project, error) {
	if s.projectRepo == nil {
		return nil, fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.List(limit, offset)
}

// ListUserProjects lists projects for a specific user
func (s *Service) ListUserProjects(userID string, limit, offset int) ([]*Project, error) {
	if s.projectRepo == nil {
		return nil, fmt.Errorf("project repository not initialized")
	}
	return s.projectRepo.ListByUserID(userID, limit, offset)
}
