package entities

import (
	"os"
	"time"
)

// ToolType represents the type of AI tool
type ToolType string

const (
	ComfyUI           ToolType = "comfyui"
	Automatic1111     ToolType = "automatic1111"
	Ollama            ToolType = "ollama"
	LMStudio          ToolType = "lmstudio"
	TextGenWebUI      ToolType = "text-gen-webui"
	StableDiffusion   ToolType = "stable-diffusion"
	LocalAI           ToolType = "localai"
)

// InstanceStatus represents the current status of a tool instance
type InstanceStatus string

const (
	StatusStopped  InstanceStatus = "stopped"
	StatusStarting InstanceStatus = "starting"
	StatusRunning  InstanceStatus = "running"
	StatusStopping InstanceStatus = "stopping"
	StatusError    InstanceStatus = "error"
)

// Configuration holds the configuration for an AI tool instance
type Configuration struct {
	ID           string            `json:"id"`
	Name         string            `json:"name"`
	Type         ToolType          `json:"type"`
	ExecutablePath string          `json:"executable_path"`
	WorkingDir   string            `json:"working_dir"`
	Port         int               `json:"port"`
	Host         string            `json:"host"`
	Arguments    []string          `json:"arguments"`
	Environment  map[string]string `json:"environment"`
	AutoStart    bool              `json:"auto_start"`
	CreatedAt    time.Time         `json:"created_at"`
	UpdatedAt    time.Time         `json:"updated_at"`
}

// AIToolInstance represents a running instance of an AI tool
type AIToolInstance struct {
	ID          string         `json:"id"`
	Config      Configuration  `json:"config"`
	Process     *os.Process    `json:"-"`
	Status      InstanceStatus `json:"status"`
	PID         int            `json:"pid"`
	StartedAt   *time.Time     `json:"started_at"`
	StoppedAt   *time.Time     `json:"stopped_at"`
	LastError   string         `json:"last_error"`
	LogFilePath string         `json:"log_file_path"`
}

// IsRunning returns true if the instance is currently running
func (i *AIToolInstance) IsRunning() bool {
	return i.Status == StatusRunning || i.Status == StatusStarting
}

// IsStopped returns true if the instance is stopped
func (i *AIToolInstance) IsStopped() bool {
	return i.Status == StatusStopped
}

// HasError returns true if the instance is in an error state
func (i *AIToolInstance) HasError() bool {
	return i.Status == StatusError
}

// GetURL returns the URL for accessing the tool's web interface
func (i *AIToolInstance) GetURL() string {
	if i.Config.Host == "" {
		return ""
	}
	protocol := "http"
	if i.Config.Port == 443 {
		protocol = "https"
	}
	return protocol + "://" + i.Config.Host + ":" + string(rune(i.Config.Port))
}
