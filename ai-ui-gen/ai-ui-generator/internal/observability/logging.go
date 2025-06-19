package observability

import (
	"github.com/rs/zerolog"
	"os"
)

// Logger provides structured logging
var Logger zerolog.Logger

// InitLogging initializes the logging system
func InitLogging(level string, format string) {
	// TODO: Implement logging initialization
	
	// Set log level
	switch level {
	case "debug":
		zerolog.SetGlobalLevel(zerolog.DebugLevel)
	case "info":
		zerolog.SetGlobalLevel(zerolog.InfoLevel)
	case "warn":
		zerolog.SetGlobalLevel(zerolog.WarnLevel)
	case "error":
		zerolog.SetGlobalLevel(zerolog.ErrorLevel)
	default:
		zerolog.SetGlobalLevel(zerolog.InfoLevel)
	}
	
	// Configure output format
	if format == "console" {
		Logger = zerolog.New(zerolog.ConsoleWriter{Out: os.Stdout}).With().Timestamp().Logger()
	} else {
		Logger = zerolog.New(os.Stdout).With().Timestamp().Logger()
	}
}

// GetLogger returns a logger with context
func GetLogger(service string) zerolog.Logger {
	return Logger.With().Str("service", service).Logger()
}

// LogRequest logs HTTP request information
func LogRequest(method, path, userAgent string, statusCode int, duration int64) {
	Logger.Info().
		Str("method", method).
		Str("path", path).
		Str("user_agent", userAgent).
		Int("status_code", statusCode).
		Int64("duration_ms", duration).
		Msg("HTTP request")
}

// LogError logs error information
func LogError(err error, context string) {
	Logger.Error().
		Err(err).
		Str("context", context).
		Msg("Error occurred")
}
