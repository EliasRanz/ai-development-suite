package user

// Repository defines the interface for user data access
type Repository interface {
	GetByID(id string) (*User, error)
	GetByEmail(email string) (*User, error)
	Create(user *User) error
	Update(id string, updates map[string]interface{}) (*User, error)
	Delete(id string) error
	List(limit, offset int) ([]*User, error)
}

// PostgresRepository implements Repository using PostgreSQL
type PostgresRepository struct {
	// TODO: Add database connection
}

// NewPostgresRepository creates a new PostgreSQL user repository
func NewPostgresRepository() *PostgresRepository {
	return &PostgresRepository{
		// TODO: Initialize database connection
	}
}

// GetByID retrieves a user by ID
func (r *PostgresRepository) GetByID(id string) (*User, error) {
	// TODO: Implement database query
	return nil, nil
}

// GetByEmail retrieves a user by email
func (r *PostgresRepository) GetByEmail(email string) (*User, error) {
	// TODO: Implement database query
	return nil, nil
}

// Create creates a new user
func (r *PostgresRepository) Create(user *User) error {
	// TODO: Implement database insert
	return nil
}

// Update updates user information
func (r *PostgresRepository) Update(id string, updates map[string]interface{}) (*User, error) {
	// TODO: Implement database update
	return nil, nil
}

// Delete deletes a user
func (r *PostgresRepository) Delete(id string) error {
	// TODO: Implement database delete
	return nil
}

// List lists users with pagination
func (r *PostgresRepository) List(limit, offset int) ([]*User, error) {
	// TODO: Implement database query with pagination
	return nil, nil
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
