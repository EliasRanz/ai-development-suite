package user

import (
	"time"
)

// User represents a user in the system
type User struct {
	ID        string    `json:"id" db:"id"`
	Email     string    `json:"email" db:"email"`
	Name      string    `json:"name" db:"name"`
	AvatarURL string    `json:"avatar_url" db:"avatar_url"`
	CreatedAt time.Time `json:"created_at" db:"created_at"`
	UpdatedAt time.Time `json:"updated_at" db:"updated_at"`
}

// Service provides user business logic
type Service struct {
	repo Repository
}

// NewService creates a new user service
func NewService(repo Repository) *Service {
	return &Service{
		repo: repo,
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
