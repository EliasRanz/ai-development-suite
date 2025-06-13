package repositories

import (
	"context"
	"github.com/ai-launcher/internal/domain/entities"
)

// ConfigurationRepository handles persistence of tool configurations
type ConfigurationRepository interface {
	// Save stores a configuration
	Save(ctx context.Context, config entities.Configuration) error
	
	// FindByID retrieves a configuration by ID
	FindByID(ctx context.Context, id string) (*entities.Configuration, error)
	
	// FindByType retrieves all configurations of a specific type
	FindByType(ctx context.Context, toolType entities.ToolType) ([]entities.Configuration, error)
	
	// FindAll retrieves all configurations
	FindAll(ctx context.Context) ([]entities.Configuration, error)
	
	// Delete removes a configuration
	Delete(ctx context.Context, id string) error
	
	// Update modifies an existing configuration
	Update(ctx context.Context, config entities.Configuration) error
}

// InstanceRepository handles runtime instance management
type InstanceRepository interface {
	// Save stores an instance state
	Save(ctx context.Context, instance entities.AIToolInstance) error
	
	// FindByID retrieves an instance by ID
	FindByID(ctx context.Context, id string) (*entities.AIToolInstance, error)
	
	// FindRunning retrieves all running instances
	FindRunning(ctx context.Context) ([]entities.AIToolInstance, error)
	
	// FindByType retrieves instances of a specific type
	FindByType(ctx context.Context, toolType entities.ToolType) ([]entities.AIToolInstance, error)
	
	// FindAll retrieves all instances
	FindAll(ctx context.Context) ([]entities.AIToolInstance, error)
	
	// Delete removes an instance
	Delete(ctx context.Context, id string) error
	
	// Update modifies an existing instance
	Update(ctx context.Context, instance entities.AIToolInstance) error
}
