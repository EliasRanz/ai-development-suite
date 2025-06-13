package usecases

import (
	"context"
	"fmt"
	"time"

	"github.com/ai-launcher/internal/domain/entities"
	"github.com/ai-launcher/internal/domain/repositories"
	"github.com/ai-launcher/internal/domain/services"
	"github.com/google/uuid"
)

// LaunchToolUseCase handles launching AI tool instances
type LaunchToolUseCase struct {
	configRepo   repositories.ConfigurationRepository
	instanceRepo repositories.InstanceRepository
	toolManager  services.ToolManager
	logService   services.LogService
}

// NewLaunchToolUseCase creates a new use case for launching tools
func NewLaunchToolUseCase(
	configRepo repositories.ConfigurationRepository,
	instanceRepo repositories.InstanceRepository,
	toolManager services.ToolManager,
	logService services.LogService,
) *LaunchToolUseCase {
	return &LaunchToolUseCase{
		configRepo:   configRepo,
		instanceRepo: instanceRepo,
		toolManager:  toolManager,
		logService:   logService,
	}
}

// Execute launches a tool with the given configuration
func (uc *LaunchToolUseCase) Execute(ctx context.Context, configID string) (*entities.AIToolInstance, error) {
	// Retrieve configuration
	config, err := uc.configRepo.FindByID(ctx, configID)
	if err != nil {
		return nil, fmt.Errorf("failed to find configuration: %w", err)
	}

	// Validate configuration
	if err := uc.toolManager.ValidateConfig(*config); err != nil {
		return nil, fmt.Errorf("invalid configuration: %w", err)
	}

	// Check if port is available
	if !uc.toolManager.IsPortAvailable(config.Port) {
		return nil, fmt.Errorf("port %d is not available", config.Port)
	}

	// Launch the tool
	instance, err := uc.toolManager.Launch(ctx, *config)
	if err != nil {
		uc.logService.WriteLog(config.ID, services.LogLevelError, fmt.Sprintf("Failed to launch: %s", err.Error()))
		return nil, fmt.Errorf("failed to launch tool: %w", err)
	}

	// Save instance state
	if err := uc.instanceRepo.Save(ctx, *instance); err != nil {
		uc.logService.WriteLog(instance.ID, services.LogLevelError, fmt.Sprintf("Failed to save instance state: %s", err.Error()))
		return instance, fmt.Errorf("failed to save instance state: %w", err)
	}

	uc.logService.WriteLog(instance.ID, services.LogLevelInfo, "Tool launched successfully")
	return instance, nil
}

// StopToolUseCase handles stopping AI tool instances
type StopToolUseCase struct {
	instanceRepo repositories.InstanceRepository
	toolManager  services.ToolManager
	logService   services.LogService
}

// NewStopToolUseCase creates a new use case for stopping tools
func NewStopToolUseCase(
	instanceRepo repositories.InstanceRepository,
	toolManager services.ToolManager,
	logService services.LogService,
) *StopToolUseCase {
	return &StopToolUseCase{
		instanceRepo: instanceRepo,
		toolManager:  toolManager,
		logService:   logService,
	}
}

// Execute stops a running tool instance
func (uc *StopToolUseCase) Execute(ctx context.Context, instanceID string) error {
	// Check if instance exists
	instance, err := uc.instanceRepo.FindByID(ctx, instanceID)
	if err != nil {
		return fmt.Errorf("failed to find instance: %w", err)
	}

	if !instance.IsRunning() {
		return fmt.Errorf("instance %s is not running", instanceID)
	}

	// Stop the tool
	if err := uc.toolManager.Stop(ctx, instanceID); err != nil {
		uc.logService.WriteLog(instanceID, services.LogLevelError, fmt.Sprintf("Failed to stop: %s", err.Error()))
		return fmt.Errorf("failed to stop tool: %w", err)
	}

	// Update instance state
	instance.Status = entities.StatusStopped
	now := time.Now()
	instance.StoppedAt = &now
	
	if err := uc.instanceRepo.Update(ctx, *instance); err != nil {
		uc.logService.WriteLog(instanceID, services.LogLevelError, fmt.Sprintf("Failed to update instance state: %s", err.Error()))
		return fmt.Errorf("failed to update instance state: %w", err)
	}

	uc.logService.WriteLog(instanceID, services.LogLevelInfo, "Tool stopped successfully")
	return nil
}

// CreateConfigurationUseCase handles creating new tool configurations
type CreateConfigurationUseCase struct {
	configRepo    repositories.ConfigurationRepository
	systemService services.SystemService
	logService    services.LogService
}

// NewCreateConfigurationUseCase creates a new use case for creating configurations
func NewCreateConfigurationUseCase(
	configRepo repositories.ConfigurationRepository,
	systemService services.SystemService,
	logService services.LogService,
) *CreateConfigurationUseCase {
	return &CreateConfigurationUseCase{
		configRepo:    configRepo,
		systemService: systemService,
		logService:    logService,
	}
}

// Execute creates a new tool configuration
func (uc *CreateConfigurationUseCase) Execute(ctx context.Context, req CreateConfigRequest) (*entities.Configuration, error) {
	// Validate the executable path
	if err := uc.systemService.ValidatePath(req.ExecutablePath); err != nil {
		return nil, fmt.Errorf("invalid executable path: %w", err)
	}

	// Create configuration
	config := entities.Configuration{
		ID:             uuid.New().String(),
		Name:           req.Name,
		Type:           req.Type,
		ExecutablePath: req.ExecutablePath,
		WorkingDir:     req.WorkingDir,
		Port:           req.Port,
		Host:           req.Host,
		Arguments:      req.Arguments,
		Environment:    req.Environment,
		AutoStart:      req.AutoStart,
		CreatedAt:      time.Now(),
		UpdatedAt:      time.Now(),
	}

	// Save configuration
	if err := uc.configRepo.Save(ctx, config); err != nil {
		return nil, fmt.Errorf("failed to save configuration: %w", err)
	}

	uc.logService.WriteLog(config.ID, services.LogLevelInfo, "Configuration created successfully")
	return &config, nil
}

// CreateConfigRequest represents a request to create a new configuration
type CreateConfigRequest struct {
	Name           string            `json:"name"`
	Type           entities.ToolType `json:"type"`
	ExecutablePath string            `json:"executable_path"`
	WorkingDir     string            `json:"working_dir"`
	Port           int               `json:"port"`
	Host           string            `json:"host"`
	Arguments      []string          `json:"arguments"`
	Environment    map[string]string `json:"environment"`
	AutoStart      bool              `json:"auto_start"`
}

// ListInstancesUseCase handles listing tool instances
type ListInstancesUseCase struct {
	instanceRepo repositories.InstanceRepository
}

// NewListInstancesUseCase creates a new use case for listing instances
func NewListInstancesUseCase(instanceRepo repositories.InstanceRepository) *ListInstancesUseCase {
	return &ListInstancesUseCase{
		instanceRepo: instanceRepo,
	}
}

// Execute lists all tool instances
func (uc *ListInstancesUseCase) Execute(ctx context.Context) ([]entities.AIToolInstance, error) {
	instances, err := uc.instanceRepo.FindAll(ctx)
	if err != nil {
		return nil, fmt.Errorf("failed to list instances: %w", err)
	}
	return instances, nil
}

// GetSystemInfoUseCase handles retrieving system information
type GetSystemInfoUseCase struct {
	systemService services.SystemService
}

// NewGetSystemInfoUseCase creates a new use case for getting system info
func NewGetSystemInfoUseCase(systemService services.SystemService) *GetSystemInfoUseCase {
	return &GetSystemInfoUseCase{
		systemService: systemService,
	}
}

// Execute retrieves system information
func (uc *GetSystemInfoUseCase) Execute() services.SystemInfo {
	return uc.systemService.GetSystemInfo()
}
