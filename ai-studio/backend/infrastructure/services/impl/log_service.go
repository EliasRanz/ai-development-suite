package impl

import (
	"fmt"
	"os"
	"path/filepath"
	"sync"
	"time"

	"github.com/ai-studio/internal/domain/services"
)

// LogService implements the LogService interface
type LogService struct {
	mu      sync.RWMutex
	logDir  string
	entries map[string][]services.LogEntry
}

// NewLogService creates a new log service
func NewLogService() *LogService {
	homeDir, _ := os.UserHomeDir()
	logDir := filepath.Join(homeDir, ".ai-launcher", "logs")
	os.MkdirAll(logDir, 0755)
	
	return &LogService{
		logDir:  logDir,
		entries: make(map[string][]services.LogEntry),
	}
}

// WriteLog writes a log entry for an instance
func (ls *LogService) WriteLog(instanceID string, level services.LogLevel, message string) error {
	ls.mu.Lock()
	defer ls.mu.Unlock()
	
	entry := services.LogEntry{
		Timestamp:  time.Now().Format(time.RFC3339),
		Level:      level,
		InstanceID: instanceID,
		Message:    message,
	}
	
	if ls.entries[instanceID] == nil {
		ls.entries[instanceID] = make([]services.LogEntry, 0)
	}
	
	ls.entries[instanceID] = append(ls.entries[instanceID], entry)
	
	// Also write to file
	logFile := filepath.Join(ls.logDir, fmt.Sprintf("%s.log", instanceID))
	file, err := os.OpenFile(logFile, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		return err
	}
	defer file.Close()
	
	logLine := fmt.Sprintf("[%s] %s: %s\n", entry.Timestamp, string(level), message)
	_, err = file.WriteString(logLine)
	return err
}

// ReadLogs reads recent log entries for an instance
func (ls *LogService) ReadLogs(instanceID string, lines int) ([]services.LogEntry, error) {
	ls.mu.RLock()
	defer ls.mu.RUnlock()
	
	entries, exists := ls.entries[instanceID]
	if !exists {
		return []services.LogEntry{}, nil
	}
	
	if len(entries) <= lines {
		return entries, nil
	}
	
	return entries[len(entries)-lines:], nil
}

// RotateLogs rotates log files for an instance
func (ls *LogService) RotateLogs(instanceID string) error {
	logFile := filepath.Join(ls.logDir, fmt.Sprintf("%s.log", instanceID))
	backupFile := filepath.Join(ls.logDir, fmt.Sprintf("%s.log.%s", instanceID, time.Now().Format("20060102-150405")))
	
	if _, err := os.Stat(logFile); os.IsNotExist(err) {
		return nil // No log file to rotate
	}
	
	return os.Rename(logFile, backupFile)
}

// CleanupLogs removes old log files
func (ls *LogService) CleanupLogs(olderThanDays int) error {
	cutoff := time.Now().AddDate(0, 0, -olderThanDays)
	
	return filepath.Walk(ls.logDir, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			return err
		}
		
		if !info.IsDir() && info.ModTime().Before(cutoff) {
			return os.Remove(path)
		}
		
		return nil
	})
}
