package user

import (
	"database/sql"
	"encoding/json"
	"fmt"

	"github.com/jmoiron/sqlx"
	"github.com/lib/pq"
	_ "github.com/lib/pq"
)

// Repository defines the interface for user data access
type Repository interface {
	GetByID(id string) (*User, error)
	GetByEmail(email string) (*User, error)
	Create(user *User) error
	Update(id string, updates map[string]interface{}) (*User, error)
	Delete(id string) error
	List(limit, offset int) ([]*User, error)
}

// ProjectRepository defines the interface for project data access
type ProjectRepository interface {
	GetByID(id string) (*Project, error)
	Create(project *Project) error
	Update(id string, updates map[string]interface{}) (*Project, error)
	Delete(id string) error
	List(limit, offset int) ([]*Project, error)
	ListByUserID(userID string, limit, offset int) ([]*Project, error)
}

// PostgresRepository implements Repository using PostgreSQL
type PostgresRepository struct {
	db *sqlx.DB
}

// PostgresProjectRepository implements ProjectRepository using PostgreSQL
type PostgresProjectRepository struct {
	db *sqlx.DB
}

// NewPostgresRepository creates a new PostgreSQL user repository
func NewPostgresRepository(db *sqlx.DB) *PostgresRepository {
	return &PostgresRepository{
		db: db,
	}
}

// NewPostgresProjectRepository creates a new PostgreSQL project repository
func NewPostgresProjectRepository(db *sqlx.DB) *PostgresProjectRepository {
	return &PostgresProjectRepository{
		db: db,
	}
}

// User Repository Implementation

// GetByID retrieves a user by ID
func (r *PostgresRepository) GetByID(id string) (*User, error) {
	var user User
	query := `
		SELECT id, email, name, avatar_url, roles, is_active, email_verified, 
			   last_login_at, created_at, updated_at 
		FROM users 
		WHERE id = $1`
	
	err := r.db.Get(&user, query, id)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // User not found
		}
		return nil, fmt.Errorf("failed to get user by ID: %w", err)
	}
	
	return &user, nil
}

// GetByEmail retrieves a user by email
func (r *PostgresRepository) GetByEmail(email string) (*User, error) {
	var user User
	query := `
		SELECT id, email, name, avatar_url, roles, is_active, email_verified, 
			   last_login_at, created_at, updated_at 
		FROM users 
		WHERE email = $1`
	
	err := r.db.Get(&user, query, email)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // User not found
		}
		return nil, fmt.Errorf("failed to get user by email: %w", err)
	}
	
	return &user, nil
}

// Create creates a new user
func (r *PostgresRepository) Create(user *User) error {
	query := `
		INSERT INTO users (email, name, avatar_url, roles, is_active, email_verified)
		VALUES ($1, $2, $3, $4, $5, $6)
		RETURNING id, created_at, updated_at`
	
	err := r.db.QueryRow(query, 
		user.Email, 
		user.Name, 
		user.AvatarURL, 
		pq.Array(user.Roles),
		user.IsActive,
		user.EmailVerified,
	).Scan(&user.ID, &user.CreatedAt, &user.UpdatedAt)
	
	if err != nil {
		return fmt.Errorf("failed to create user: %w", err)
	}
	
	return nil
}

// Update updates a user
func (r *PostgresRepository) Update(id string, updates map[string]interface{}) (*User, error) {
	// Build dynamic update query
	setParts := []string{}
	args := []interface{}{}
	argPos := 1
	
	for key, value := range updates {
		setParts = append(setParts, fmt.Sprintf("%s = $%d", key, argPos))
		args = append(args, value)
		argPos++
	}
	
	if len(setParts) == 0 {
		return r.GetByID(id) // No updates to perform
	}
	
	args = append(args, id)
	query := fmt.Sprintf(`
		UPDATE users 
		SET %s, updated_at = NOW()
		WHERE id = $%d
		RETURNING id, email, name, avatar_url, roles, is_active, email_verified, 
				  last_login_at, created_at, updated_at`,
		fmt.Sprintf("%s", setParts), argPos)
	
	var user User
	err := r.db.Get(&user, query, args...)
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, fmt.Errorf("user not found")
		}
		return nil, fmt.Errorf("failed to update user: %w", err)
	}
	
	return &user, nil
}

// Delete deletes a user
func (r *PostgresRepository) Delete(id string) error {
	query := `DELETE FROM users WHERE id = $1`
	
	result, err := r.db.Exec(query, id)
	if err != nil {
		return fmt.Errorf("failed to delete user: %w", err)
	}
	
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to check affected rows: %w", err)
	}
	
	if rowsAffected == 0 {
		return fmt.Errorf("user not found")
	}
	
	return nil
}

// List lists users with pagination
func (r *PostgresRepository) List(limit, offset int) ([]*User, error) {
	var users []*User
	query := `
		SELECT id, email, name, avatar_url, roles, is_active, email_verified, 
			   last_login_at, created_at, updated_at 
		FROM users 
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2`
	
	err := r.db.Select(&users, query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list users: %w", err)
	}
	
	return users, nil
}

// Project Repository Implementation

// GetByID retrieves a project by ID
func (r *PostgresProjectRepository) GetByID(id string) (*Project, error) {
	var project Project
	query := `
		SELECT id, name, description, user_id, status, tags, config, metadata, 
			   is_public, template_id, created_at, updated_at 
		FROM projects 
		WHERE id = $1`
	
	var configJSON, metadataJSON []byte
	err := r.db.QueryRow(query, id).Scan(
		&project.ID, &project.Name, &project.Description, &project.UserID,
		&project.Status, pq.Array(&project.Tags), &configJSON, &metadataJSON,
		&project.IsPublic, &project.TemplateID, &project.CreatedAt, &project.UpdatedAt,
	)
	
	if err != nil {
		if err == sql.ErrNoRows {
			return nil, nil // Project not found
		}
		return nil, fmt.Errorf("failed to get project by ID: %w", err)
	}
	
	// Parse JSON fields
	if len(configJSON) > 0 {
		if err := json.Unmarshal(configJSON, &project.Config); err != nil {
			return nil, fmt.Errorf("failed to parse config JSON: %w", err)
		}
	}
	if len(metadataJSON) > 0 {
		if err := json.Unmarshal(metadataJSON, &project.Metadata); err != nil {
			return nil, fmt.Errorf("failed to parse metadata JSON: %w", err)
		}
	}
	
	return &project, nil
}

// Create creates a new project
func (r *PostgresProjectRepository) Create(project *Project) error {
	configJSON, err := json.Marshal(project.Config)
	if err != nil {
		return fmt.Errorf("failed to marshal config: %w", err)
	}
	
	metadataJSON, err := json.Marshal(project.Metadata)
	if err != nil {
		return fmt.Errorf("failed to marshal metadata: %w", err)
	}
	
	query := `
		INSERT INTO projects (name, description, user_id, status, tags, config, metadata, is_public, template_id)
		VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9)
		RETURNING id, created_at, updated_at`
	
	err = r.db.QueryRow(query,
		project.Name, project.Description, project.UserID, project.Status,
		pq.Array(project.Tags), configJSON, metadataJSON, project.IsPublic, project.TemplateID,
	).Scan(&project.ID, &project.CreatedAt, &project.UpdatedAt)
	
	if err != nil {
		return fmt.Errorf("failed to create project: %w", err)
	}
	
	return nil
}

// Update updates a project
func (r *PostgresProjectRepository) Update(id string, updates map[string]interface{}) (*Project, error) {
	// Build dynamic update query (simplified for stub)
	setParts := []string{}
	args := []interface{}{}
	argPos := 1
	
	for key, value := range updates {
		if key == "config" || key == "metadata" {
			// Handle JSON fields
			jsonData, err := json.Marshal(value)
			if err != nil {
				return nil, fmt.Errorf("failed to marshal %s: %w", key, err)
			}
			setParts = append(setParts, fmt.Sprintf("%s = $%d", key, argPos))
			args = append(args, jsonData)
		} else if key == "tags" {
			setParts = append(setParts, fmt.Sprintf("%s = $%d", key, argPos))
			args = append(args, pq.Array(value))
		} else {
			setParts = append(setParts, fmt.Sprintf("%s = $%d", key, argPos))
			args = append(args, value)
		}
		argPos++
	}
	
	if len(setParts) == 0 {
		return r.GetByID(id) // No updates to perform
	}
	
	args = append(args, id)
	query := fmt.Sprintf(`
		UPDATE projects 
		SET %s, updated_at = NOW()
		WHERE id = $%d`,
		fmt.Sprintf("%s", setParts), argPos)
	
	_, err := r.db.Exec(query, args...)
	if err != nil {
		return nil, fmt.Errorf("failed to update project: %w", err)
	}
	
	return r.GetByID(id)
}

// Delete deletes a project
func (r *PostgresProjectRepository) Delete(id string) error {
	query := `DELETE FROM projects WHERE id = $1`
	
	result, err := r.db.Exec(query, id)
	if err != nil {
		return fmt.Errorf("failed to delete project: %w", err)
	}
	
	rowsAffected, err := result.RowsAffected()
	if err != nil {
		return fmt.Errorf("failed to check affected rows: %w", err)
	}
	
	if rowsAffected == 0 {
		return fmt.Errorf("project not found")
	}
	
	return nil
}

// List lists projects with pagination
func (r *PostgresProjectRepository) List(limit, offset int) ([]*Project, error) {
	var projects []*Project
	query := `
		SELECT id, name, description, user_id, status, tags, config, metadata, 
			   is_public, template_id, created_at, updated_at 
		FROM projects 
		ORDER BY created_at DESC
		LIMIT $1 OFFSET $2`
	
	rows, err := r.db.Query(query, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list projects: %w", err)
	}
	defer rows.Close()
	
	for rows.Next() {
		var project Project
		var configJSON, metadataJSON []byte
		
		err := rows.Scan(
			&project.ID, &project.Name, &project.Description, &project.UserID,
			&project.Status, pq.Array(&project.Tags), &configJSON, &metadataJSON,
			&project.IsPublic, &project.TemplateID, &project.CreatedAt, &project.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan project: %w", err)
		}
		
		// Parse JSON fields
		if len(configJSON) > 0 {
			if err := json.Unmarshal(configJSON, &project.Config); err != nil {
				return nil, fmt.Errorf("failed to parse config JSON: %w", err)
			}
		}
		if len(metadataJSON) > 0 {
			if err := json.Unmarshal(metadataJSON, &project.Metadata); err != nil {
				return nil, fmt.Errorf("failed to parse metadata JSON: %w", err)
			}
		}
		
		projects = append(projects, &project)
	}
	
	return projects, nil
}

// ListByUserID lists projects for a specific user
func (r *PostgresProjectRepository) ListByUserID(userID string, limit, offset int) ([]*Project, error) {
	var projects []*Project
	query := `
		SELECT id, name, description, user_id, status, tags, config, metadata, 
			   is_public, template_id, created_at, updated_at 
		FROM projects 
		WHERE user_id = $1
		ORDER BY created_at DESC
		LIMIT $2 OFFSET $3`
	
	rows, err := r.db.Query(query, userID, limit, offset)
	if err != nil {
		return nil, fmt.Errorf("failed to list user projects: %w", err)
	}
	defer rows.Close()
	
	for rows.Next() {
		var project Project
		var configJSON, metadataJSON []byte
		
		err := rows.Scan(
			&project.ID, &project.Name, &project.Description, &project.UserID,
			&project.Status, pq.Array(&project.Tags), &configJSON, &metadataJSON,
			&project.IsPublic, &project.TemplateID, &project.CreatedAt, &project.UpdatedAt,
		)
		if err != nil {
			return nil, fmt.Errorf("failed to scan project: %w", err)
		}
		
		// Parse JSON fields
		if len(configJSON) > 0 {
			if err := json.Unmarshal(configJSON, &project.Config); err != nil {
				return nil, fmt.Errorf("failed to parse config JSON: %w", err)
			}
		}
		if len(metadataJSON) > 0 {
			if err := json.Unmarshal(metadataJSON, &project.Metadata); err != nil {
				return nil, fmt.Errorf("failed to parse metadata JSON: %w", err)
			}
		}
		
		projects = append(projects, &project)
	}
	
	return projects, nil
}

// MockRepository implements Repository for testing/stub purposes
type MockRepository struct {
	users map[string]*User
}

// NewMockRepository creates a new mock repository
func NewMockRepository() *MockRepository {
	return &MockRepository{
		users: make(map[string]*User),
	}
}

// GetByID retrieves a user by ID
func (r *MockRepository) GetByID(id string) (*User, error) {
	if user, exists := r.users[id]; exists {
		return user, nil
	}
	return nil, nil // User not found
}

// GetByEmail retrieves a user by email
func (r *MockRepository) GetByEmail(email string) (*User, error) {
	for _, user := range r.users {
		if user.Email == email {
			return user, nil
		}
	}
	return nil, nil // User not found
}

// Create creates a new user
func (r *MockRepository) Create(user *User) error {
	r.users[user.ID] = user
	return nil
}

// Update updates a user
func (r *MockRepository) Update(id string, updates map[string]interface{}) (*User, error) {
	if user, exists := r.users[id]; exists {
		// Apply updates (simplified for mock)
		if name, ok := updates["name"].(string); ok {
			user.Name = name
		}
		if email, ok := updates["email"].(string); ok {
			user.Email = email
		}
		if avatarURL, ok := updates["avatar_url"].(string); ok {
			user.AvatarURL = avatarURL
		}
		r.users[id] = user
		return user, nil
	}
	return nil, nil // User not found
}

// Delete deletes a user
func (r *MockRepository) Delete(id string) error {
	delete(r.users, id)
	return nil
}

// List lists users with pagination
func (r *MockRepository) List(limit, offset int) ([]*User, error) {
	var users []*User
	count := 0
	for _, user := range r.users {
		if count >= offset && len(users) < limit {
			users = append(users, user)
		}
		count++
	}
	return users, nil
}
