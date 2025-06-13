package services

import (
	"context"
	"github.com/ai-studio/internal/domain/entities"
)

// ToolManager defines the interface for managing AI tool instances
type ToolManager interface {
	// Launch starts a new instance of an AI tool
	Launch(ctx context.Context, config entities.Configuration) (*entities.AIToolInstance, error)
	
	// Stop terminates a running instance
	Stop(ctx context.Context, instanceID string) error
	
	// Restart stops and starts an instance
	Restart(ctx context.Context, instanceID string) error
	
	// GetStatus returns the current status of an instance
	GetStatus(ctx context.Context, instanceID string) (entities.InstanceStatus, error)
	
	// GetDefaultConfig returns the default configuration for a tool type
	GetDefaultConfig(toolType entities.ToolType) entities.Configuration
	
	// ValidateConfig validates a configuration before launching
	ValidateConfig(config entities.Configuration) error
	
	// GetLogs retrieves logs for an instance
	GetLogs(ctx context.Context, instanceID string, lines int) ([]string, error)
	
	// IsPortAvailable checks if a port is available for use
	IsPortAvailable(port int) bool
	
	// FindAvailablePort finds an available port in a given range
	FindAvailablePort(startPort, endPort int) (int, error)
}

// SystemService provides system-level operations
type SystemService interface {
	// GetSystemInfo returns system information
	GetSystemInfo() SystemInfo
	
	// CheckDependencies verifies required dependencies are installed
	CheckDependencies(toolType entities.ToolType) DependencyStatus
	
	// GetAvailableTools returns tools that can be launched on this system
	GetAvailableTools() []entities.ToolType
	
	// ValidatePath checks if a path exists and is accessible
	ValidatePath(path string) error
	
	// GetRecommendedPorts returns recommended port ranges for different tools
	GetRecommendedPorts(toolType entities.ToolType) (int, int)
}

// LogService handles logging operations
type LogService interface {
	// WriteLog writes a log entry for an instance
	WriteLog(instanceID string, level LogLevel, message string) error
	
	// ReadLogs reads recent log entries for an instance
	ReadLogs(instanceID string, lines int) ([]LogEntry, error)
	
	// RotateLogs rotates log files for an instance
	RotateLogs(instanceID string) error
	
	// CleanupLogs removes old log files
	CleanupLogs(olderThan int) error
}

// SystemInfo contains system information
type SystemInfo struct {
	OS           string `json:"os"`
	Architecture string `json:"architecture"`
	CPUCores     int    `json:"cpu_cores"`
	Memory       int64  `json:"memory"`
	DiskSpace    int64  `json:"disk_space"`
}

// DependencyStatus represents the status of dependencies for a tool
type DependencyStatus struct {
	Available     bool              `json:"available"`
	MissingDeps   []string          `json:"missing_dependencies"`
	Satisfied     []string          `json:"satisfied_dependencies"`
	Recommendations []string        `json:"recommendations"`
}

// LogLevel represents the severity of a log entry
type LogLevel string

const (
	LogLevelDebug LogLevel = "debug"
	LogLevelInfo  LogLevel = "info"
	LogLevelWarn  LogLevel = "warn"
	LogLevelError LogLevel = "error"
)

// LogEntry represents a single log entry
type LogEntry struct {
	Timestamp   string   `json:"timestamp"`
	Level       LogLevel `json:"level"`
	InstanceID  string   `json:"instance_id"`
	Message     string   `json:"message"`
}
