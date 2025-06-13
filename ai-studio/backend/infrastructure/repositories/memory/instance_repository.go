package memory

import (
	"context"
	"fmt"
	"sync"

	"github.com/ai-studio/backend/domain/entities"
)

// InstanceRepository is an in-memory implementation of the instance repository
type InstanceRepository struct {
	mu        sync.RWMutex
	instances map[string]entities.AIToolInstance
}

// NewInstanceRepository creates a new in-memory instance repository
func NewInstanceRepository() *InstanceRepository {
	return &InstanceRepository{
		instances: make(map[string]entities.AIToolInstance),
	}
}

// Save stores an instance state
func (r *InstanceRepository) Save(ctx context.Context, instance entities.AIToolInstance) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	r.instances[instance.ID] = instance
	return nil
}

// FindByID retrieves an instance by ID
func (r *InstanceRepository) FindByID(ctx context.Context, id string) (*entities.AIToolInstance, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	instance, exists := r.instances[id]
	if !exists {
		return nil, fmt.Errorf("instance with ID %s not found", id)
	}
	
	return &instance, nil
}

// FindRunning retrieves all running instances
func (r *InstanceRepository) FindRunning(ctx context.Context) ([]entities.AIToolInstance, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var instances []entities.AIToolInstance
	for _, instance := range r.instances {
		if instance.IsRunning() {
			instances = append(instances, instance)
		}
	}
	
	return instances, nil
}

// FindByType retrieves instances of a specific type
func (r *InstanceRepository) FindByType(ctx context.Context, toolType entities.ToolType) ([]entities.AIToolInstance, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	var instances []entities.AIToolInstance
	for _, instance := range r.instances {
		if instance.Config.Type == toolType {
			instances = append(instances, instance)
		}
	}
	
	return instances, nil
}

// FindAll retrieves all instances
func (r *InstanceRepository) FindAll(ctx context.Context) ([]entities.AIToolInstance, error) {
	r.mu.RLock()
	defer r.mu.RUnlock()
	
	instances := make([]entities.AIToolInstance, 0, len(r.instances))
	for _, instance := range r.instances {
		instances = append(instances, instance)
	}
	
	return instances, nil
}

// Delete removes an instance
func (r *InstanceRepository) Delete(ctx context.Context, id string) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.instances[id]; !exists {
		return fmt.Errorf("instance with ID %s not found", id)
	}
	
	delete(r.instances, id)
	return nil
}

// Update modifies an existing instance
func (r *InstanceRepository) Update(ctx context.Context, instance entities.AIToolInstance) error {
	r.mu.Lock()
	defer r.mu.Unlock()
	
	if _, exists := r.instances[instance.ID]; !exists {
		return fmt.Errorf("instance with ID %s not found", instance.ID)
	}
	
	r.instances[instance.ID] = instance
	return nil
}
