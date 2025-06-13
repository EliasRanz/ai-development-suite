package impl

import (
	"context"
	"fmt"
	"net"
	"os"
	"os/exec"
	"runtime"
	"strconv"
	"strings"
	"time"

	"github.com/ai-launcher/internal/domain/entities"
	"github.com/ai-launcher/internal/domain/services"
	"github.com/google/uuid"
)

// ToolManager implements the ToolManager interface
type ToolManager struct {
	logService services.LogService
}

// NewToolManager creates a new tool manager
func NewToolManager(logService services.LogService) *ToolManager {
	return &ToolManager{
		logService: logService,
	}
}

// Launch starts a new instance of an AI tool
func (tm *ToolManager) Launch(ctx context.Context, config entities.Configuration) (*entities.AIToolInstance, error) {
	// Validate the executable exists
	if _, err := os.Stat(config.ExecutablePath); os.IsNotExist(err) {
		return nil, fmt.Errorf("executable not found: %s", config.ExecutablePath)
	}

	// Prepare command arguments
	args := config.Arguments
	if len(args) == 0 {
		args = tm.getDefaultArgs(config.Type, config.Port, config.Host)
	}

	// Create command
	cmd := exec.CommandContext(ctx, config.ExecutablePath, args...)
	cmd.Dir = config.WorkingDir
	
	// Set environment variables
	cmd.Env = os.Environ()
	for key, value := range config.Environment {
		cmd.Env = append(cmd.Env, fmt.Sprintf("%s=%s", key, value))
	}

	// Start the process
	if err := cmd.Start(); err != nil {
		return nil, fmt.Errorf("failed to start process: %w", err)
	}

	// Create instance
	now := time.Now()
	instance := &entities.AIToolInstance{
		ID:        uuid.New().String(),
		Config:    config,
		Process:   cmd.Process,
		Status:    entities.StatusStarting,
		PID:       cmd.Process.Pid,
		StartedAt: &now,
	}

	// Monitor the process in a goroutine
	go tm.monitorProcess(instance, cmd)

	return instance, nil
}

// Stop terminates a running instance
func (tm *ToolManager) Stop(ctx context.Context, instanceID string) error {
	// For now, we'll implement a simple stop mechanism
	// In a real implementation, this would track running processes
	tm.logService.WriteLog(instanceID, services.LogLevelInfo, "Stop requested")
	return nil
}

// Restart stops and starts an instance
func (tm *ToolManager) Restart(ctx context.Context, instanceID string) error {
	if err := tm.Stop(ctx, instanceID); err != nil {
		return err
	}
	
	// Wait a moment for the process to stop
	time.Sleep(2 * time.Second)
	
	// For now, return success - in a real implementation we'd relaunch
	tm.logService.WriteLog(instanceID, services.LogLevelInfo, "Restart completed")
	return nil
}

// GetStatus returns the current status of an instance
func (tm *ToolManager) GetStatus(ctx context.Context, instanceID string) (entities.InstanceStatus, error) {
	// For now, return running - in a real implementation we'd check the actual process
	return entities.StatusRunning, nil
}

// GetDefaultConfig returns the default configuration for a tool type
func (tm *ToolManager) GetDefaultConfig(toolType entities.ToolType) entities.Configuration {
	config := entities.Configuration{
		ID:          uuid.New().String(),
		Type:        toolType,
		Host:        "127.0.0.1",
		AutoStart:   false,
		Environment: make(map[string]string),
		CreatedAt:   time.Now(),
		UpdatedAt:   time.Now(),
	}

	switch toolType {
	case entities.ComfyUI:
		config.Name = "ComfyUI Instance"
		config.Port = 8188
		config.Arguments = []string{"--listen", "127.0.0.1", "--port", "8188"}
	case entities.Automatic1111:
		config.Name = "Automatic1111 Instance"
		config.Port = 7860
		config.Arguments = []string{"--listen", "--port", "7860"}
	case entities.Ollama:
		config.Name = "Ollama Instance"
		config.Port = 11434
		config.Arguments = []string{"serve"}
	case entities.LMStudio:
		config.Name = "LM Studio Instance"
		config.Port = 1234
		config.Arguments = []string{}
	case entities.TextGenWebUI:
		config.Name = "Text Generation WebUI Instance"
		config.Port = 7860
		config.Arguments = []string{"--listen", "--listen-port", "7860"}
	default:
		config.Name = "AI Tool Instance"
		config.Port = 8080
		config.Arguments = []string{}
	}

	return config
}

// ValidateConfig validates a configuration before launching
func (tm *ToolManager) ValidateConfig(config entities.Configuration) error {
	if config.ExecutablePath == "" {
		return fmt.Errorf("executable path is required")
	}
	
	if config.Port <= 0 || config.Port > 65535 {
		return fmt.Errorf("port must be between 1 and 65535")
	}
	
	if config.Host == "" {
		return fmt.Errorf("host is required")
	}
	
	return nil
}

// GetLogs retrieves logs for an instance
func (tm *ToolManager) GetLogs(ctx context.Context, instanceID string, lines int) ([]string, error) {
	// For now, return mock logs
	logs := []string{
		fmt.Sprintf("[%s] Instance %s started", time.Now().Format(time.RFC3339), instanceID),
		fmt.Sprintf("[%s] Listening on port", time.Now().Format(time.RFC3339)),
	}
	return logs, nil
}

// IsPortAvailable checks if a port is available for use
func (tm *ToolManager) IsPortAvailable(port int) bool {
	conn, err := net.Listen("tcp", fmt.Sprintf(":%d", port))
	if err != nil {
		return false
	}
	conn.Close()
	return true
}

// FindAvailablePort finds an available port in a given range
func (tm *ToolManager) FindAvailablePort(startPort, endPort int) (int, error) {
	for port := startPort; port <= endPort; port++ {
		if tm.IsPortAvailable(port) {
			return port, nil
		}
	}
	return 0, fmt.Errorf("no available port found in range %d-%d", startPort, endPort)
}

// getDefaultArgs returns default arguments for a tool type
func (tm *ToolManager) getDefaultArgs(toolType entities.ToolType, port int, host string) []string {
	portStr := strconv.Itoa(port)
	
	switch toolType {
	case entities.ComfyUI:
		return []string{"--listen", host, "--port", portStr}
	case entities.Automatic1111:
		return []string{"--listen", "--port", portStr}
	case entities.Ollama:
		return []string{"serve"}
	case entities.TextGenWebUI:
		return []string{"--listen", "--listen-port", portStr}
	default:
		return []string{}
	}
}

// monitorProcess monitors a running process and updates its status
func (tm *ToolManager) monitorProcess(instance *entities.AIToolInstance, cmd *exec.Cmd) {
	// Wait for the process to finish
	err := cmd.Wait()
	
	if err != nil {
		instance.Status = entities.StatusError
		instance.LastError = err.Error()
		tm.logService.WriteLog(instance.ID, services.LogLevelError, fmt.Sprintf("Process exited with error: %s", err.Error()))
	} else {
		instance.Status = entities.StatusStopped
		tm.logService.WriteLog(instance.ID, services.LogLevelInfo, "Process exited normally")
	}
	
	now := time.Now()
	instance.StoppedAt = &now
}

// SystemService implements the SystemService interface
type SystemService struct{}

// NewSystemService creates a new system service
func NewSystemService() *SystemService {
	return &SystemService{}
}

// GetSystemInfo returns system information
func (ss *SystemService) GetSystemInfo() services.SystemInfo {
	return services.SystemInfo{
		OS:           runtime.GOOS,
		Architecture: runtime.GOARCH,
		CPUCores:     runtime.NumCPU(),
		Memory:       0, // Would implement actual memory detection
		DiskSpace:    0, // Would implement actual disk space detection
	}
}

// CheckDependencies verifies required dependencies are installed
func (ss *SystemService) CheckDependencies(toolType entities.ToolType) services.DependencyStatus {
	// For now, return that everything is available
	return services.DependencyStatus{
		Available:       true,
		MissingDeps:     []string{},
		Satisfied:       []string{"system"},
		Recommendations: []string{},
	}
}

// GetAvailableTools returns tools that can be launched on this system
func (ss *SystemService) GetAvailableTools() []entities.ToolType {
	return []entities.ToolType{
		entities.ComfyUI,
		entities.Automatic1111,
		entities.Ollama,
		entities.LMStudio,
		entities.TextGenWebUI,
		entities.StableDiffusion,
		entities.LocalAI,
	}
}

// ValidatePath checks if a path exists and is accessible
func (ss *SystemService) ValidatePath(path string) error {
	// Check for path traversal
	if strings.Contains(path, "..") {
		return fmt.Errorf("path traversal detected in: %s", path)
	}
	
	// Check if path exists
	if _, err := os.Stat(path); os.IsNotExist(err) {
		return fmt.Errorf("path does not exist: %s", path)
	}
	
	return nil
}

// GetRecommendedPorts returns recommended port ranges for different tools
func (ss *SystemService) GetRecommendedPorts(toolType entities.ToolType) (int, int) {
	switch toolType {
	case entities.ComfyUI:
		return 8188, 8198
	case entities.Automatic1111:
		return 7860, 7870
	case entities.Ollama:
		return 11434, 11444
	case entities.LMStudio:
		return 1234, 1244
	case entities.TextGenWebUI:
		return 7860, 7870
	default:
		return 8080, 8090
	}
}
