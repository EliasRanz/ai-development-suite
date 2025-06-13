package container

import (
	"github.com/ai-studio/backend/application/usecases"
	"github.com/ai-studio/backend/domain/repositories"
	"github.com/ai-studio/backend/domain/services"
	"github.com/ai-studio/backend/infrastructure/repositories/memory"
	"github.com/ai-studio/backend/infrastructure/services/impl"
	"github.com/ai-studio/backend/interfaces/wails"
)

// Container holds all dependencies
type Container struct {
	// Repositories
	ConfigRepo   repositories.ConfigurationRepository
	InstanceRepo repositories.InstanceRepository

	// Services
	ToolManager   services.ToolManager
	SystemService services.SystemService
	LogService    services.LogService

	// Use Cases
	LaunchTool    *usecases.LaunchToolUseCase
	StopTool      *usecases.StopToolUseCase
	CreateConfig  *usecases.CreateConfigurationUseCase
	ListInstances *usecases.ListInstancesUseCase
	GetSystemInfo *usecases.GetSystemInfoUseCase

	// Wails App
	WailsApp *wails.App
}

// NewContainer creates and wires up all dependencies
func NewContainer() *Container {
	c := &Container{}

	// Initialize repositories
	c.ConfigRepo = memory.NewConfigurationRepository()
	c.InstanceRepo = memory.NewInstanceRepository()

	// Initialize services
	c.LogService = impl.NewLogService()
	c.SystemService = impl.NewSystemService()
	c.ToolManager = impl.NewToolManager(c.LogService)

	// Initialize use cases
	c.LaunchTool = usecases.NewLaunchToolUseCase(
		c.ConfigRepo,
		c.InstanceRepo,
		c.ToolManager,
		c.LogService,
	)

	c.StopTool = usecases.NewStopToolUseCase(
		c.InstanceRepo,
		c.ToolManager,
		c.LogService,
	)

	c.CreateConfig = usecases.NewCreateConfigurationUseCase(
		c.ConfigRepo,
		c.SystemService,
		c.LogService,
	)

	c.ListInstances = usecases.NewListInstancesUseCase(c.InstanceRepo)

	c.GetSystemInfo = usecases.NewGetSystemInfoUseCase(c.SystemService)

	// Initialize Wails app
	c.WailsApp = wails.NewApp(
		c.LaunchTool,
		c.StopTool,
		c.CreateConfig,
		c.ListInstances,
		c.GetSystemInfo,
	)

	return c
}
