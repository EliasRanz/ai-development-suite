package wails

import (
	"context"
	"fmt"

	"github.com/ai-studio/internal/application/usecases"
	"github.com/ai-studio/internal/domain/entities"
	"github.com/ai-studio/internal/domain/services"
)

// App represents the Wails application with all use cases
type App struct {
	ctx context.Context

	// Use cases
	launchTool       *usecases.LaunchToolUseCase
	stopTool         *usecases.StopToolUseCase
	createConfig     *usecases.CreateConfigurationUseCase
	listInstances    *usecases.ListInstancesUseCase
	getSystemInfo    *usecases.GetSystemInfoUseCase
}

// NewApp creates a new Wails application with dependency injection
func NewApp(
	launchTool *usecases.LaunchToolUseCase,
	stopTool *usecases.StopToolUseCase,
	createConfig *usecases.CreateConfigurationUseCase,
	listInstances *usecases.ListInstancesUseCase,
	getSystemInfo *usecases.GetSystemInfoUseCase,
) *App {
	return &App{
		launchTool:    launchTool,
		stopTool:      stopTool,
		createConfig:  createConfig,
		listInstances: listInstances,
		getSystemInfo: getSystemInfo,
	}
}

// Startup is called when the app starts. The context is saved
// so we can call the runtime methods
func (a *App) Startup(ctx context.Context) {
	a.ctx = ctx
}

// GetSystemInfo returns system information
func (a *App) GetSystemInfo() services.SystemInfo {
	return a.getSystemInfo.Execute()
}

// LaunchTool launches an AI tool with the given configuration ID
func (a *App) LaunchTool(configID string) (*entities.AIToolInstance, error) {
	return a.launchTool.Execute(a.ctx, configID)
}

// StopTool stops a running AI tool instance
func (a *App) StopTool(instanceID string) error {
	return a.stopTool.Execute(a.ctx, instanceID)
}

// CreateConfiguration creates a new tool configuration
func (a *App) CreateConfiguration(req usecases.CreateConfigRequest) (*entities.Configuration, error) {
	return a.createConfig.Execute(a.ctx, req)
}

// ListInstances returns all tool instances
func (a *App) ListInstances() ([]entities.AIToolInstance, error) {
	return a.listInstances.Execute(a.ctx)
}

// GetAvailableTools returns available tool types
func (a *App) GetAvailableTools() []string {
	return []string{
		string(entities.ComfyUI),
		string(entities.Automatic1111),
		string(entities.Ollama),
		string(entities.LMStudio),
		string(entities.TextGenWebUI),
		string(entities.StableDiffusion),
		string(entities.LocalAI),
	}
}

// GetToolDefaultConfig returns default configuration for a tool type
func (a *App) GetToolDefaultConfig(toolType string) map[string]interface{} {
	switch entities.ToolType(toolType) {
	case entities.ComfyUI:
		return map[string]interface{}{
			"port":    8188,
			"host":    "127.0.0.1",
			"arguments": []string{"--listen", "127.0.0.1", "--port", "8188"},
		}
	case entities.Automatic1111:
		return map[string]interface{}{
			"port":    7860,
			"host":    "127.0.0.1",
			"arguments": []string{"--listen", "--port", "7860"},
		}
	case entities.Ollama:
		return map[string]interface{}{
			"port":    11434,
			"host":    "127.0.0.1",
			"arguments": []string{"serve"},
		}
	case entities.LMStudio:
		return map[string]interface{}{
			"port":    1234,
			"host":    "127.0.0.1",
			"arguments": []string{},
		}
	case entities.TextGenWebUI:
		return map[string]interface{}{
			"port":    7860,
			"host":    "127.0.0.1",
			"arguments": []string{"--listen", "--listen-port", "7860"},
		}
	default:
		return map[string]interface{}{
			"port":    8080,
			"host":    "127.0.0.1",
			"arguments": []string{},
		}
	}
}

// ValidateConfiguration validates a configuration before saving
func (a *App) ValidateConfiguration(config usecases.CreateConfigRequest) error {
	if config.Name == "" {
		return fmt.Errorf("configuration name is required")
	}
	if config.ExecutablePath == "" {
		return fmt.Errorf("executable path is required")
	}
	if config.Port <= 0 || config.Port > 65535 {
		return fmt.Errorf("port must be between 1 and 65535")
	}
	if config.Host == "" {
		config.Host = "127.0.0.1"
	}
	return nil
}

// IsPortAvailable checks if a port is available
func (a *App) IsPortAvailable(port int) bool {
	// This would typically use the tool manager, but for now return true
	// TODO: Implement actual port checking
	return true
}

// GetRecommendedPorts returns recommended port ranges for tools
func (a *App) GetRecommendedPorts(toolType string) map[string]int {
	switch entities.ToolType(toolType) {
	case entities.ComfyUI:
		return map[string]int{"start": 8188, "end": 8198}
	case entities.Automatic1111:
		return map[string]int{"start": 7860, "end": 7870}
	case entities.Ollama:
		return map[string]int{"start": 11434, "end": 11444}
	case entities.LMStudio:
		return map[string]int{"start": 1234, "end": 1244}
	case entities.TextGenWebUI:
		return map[string]int{"start": 7860, "end": 7870}
	default:
		return map[string]int{"start": 8080, "end": 8090}
	}
}
