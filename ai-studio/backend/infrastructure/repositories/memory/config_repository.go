package memory

import (
	"context"
	"fmt"
	"sync"

	"github.com/ai-studio/internal/domain/entities"
)

// ConfigurationRepository is an in-memory implementation of the configuration repository
type ConfigurationRepository struct {
	mu      sync.RWMutex
	configs map[string]entities.Configuration
}

// NewConfigurationRepository creates a new in-memory configuration repository
func NewConfigurationRepository() *ConfigurationRepository {
	return &ConfigurationRepository{
		configs: make(map[string]entities.Configuration),
	}
}

// Save stores a configuration
func (r *ConfigurationRepository) Save(ctx context.Context, config entities.Configuration) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	r.configs[config.ID] = config
	return nil
}

// FindByID retrieves a configuration by ID
func (r *ConfigurationRepository) FindByID(ctx context.Context, id string) (*entities.Configuration, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	config, exists := r.configs[id]
	if !exists {
		return nil, fmt.Errorf("configuration with ID %s not found", id)
	}
	
	return &config, nil
}

// FindByType retrieves all configurations of a specific type
func (r *ConfigurationRepository) FindByType(ctx context.Context, toolType entities.ToolType) ([]entities.Configuration, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var configs []entities.Configuration
	for _, config := range r.configs {
		if config.Type == toolType {
			configs = append(configs, config)
		}
	}
	
	return configs, nil
}

// FindAll retrieves all configurations
func (r *ConfigurationRepository) FindAll(ctx context.Context) ([]entities.Configuration, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	configs := make([]entities.Configuration, 0, len(r.configs))
	for _, config := range r.configs {
		configs = append(configs, config)
	}
	
	return configs, nil
}

// Delete removes a configuration
func (r *ConfigurationRepository) Delete(ctx context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.configs[id]; !exists {
		return fmt.Errorf("configuration with ID %s not found", id)
	}
	
	delete(r.configs, id)
	return nil
}

// Update modifies an existing configuration
func (r *ConfigurationRepository) Update(ctx context.Context, config entities.Configuration) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.configs[config.ID]; !exists {
		return fmt.Errorf("configuration with ID %s not found", config.ID)
	}
	
	r.configs[config.ID] = config
	return nil
}
