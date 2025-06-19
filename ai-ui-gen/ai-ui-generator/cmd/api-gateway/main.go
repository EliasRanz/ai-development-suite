package main

import (
	"log"
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/ai-tools/ai-ui-generator/internal/config"
	"github.com/ai-tools/ai-ui-generator/internal/service"
)

const (
	serviceName = "api-gateway"
	version     = "1.0.0"
)

func main() {
	// Load configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatal("Failed to load configuration:", err)
	}

	// Override port for this service
	cfg.Server.Port = getServicePort(cfg, 8080)

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		log.Fatal("Configuration validation failed:", err)
	}

	// Create service instance
	svc := service.New(serviceName, version, cfg)

	// Initialize observability
	if err := svc.Initialize(); err != nil {
		log.Fatal("Failed to initialize service:", err)
	}

	// Setup router
	router := setupRouter(cfg)

	// Setup HTTP server
	svc.SetupHTTPServer(router)

	// Start service
	if err := svc.Start(); err != nil {
		log.Fatal("Service failed to start:", err)
	}
}

func setupRouter(cfg *config.Config) http.Handler {
	// Set Gin mode based on log level
	if cfg.Logging.Level == "debug" {
		gin.SetMode(gin.DebugMode)
	} else {
		gin.SetMode(gin.ReleaseMode)
	}

	r := gin.New()

	// Add middleware
	r.Use(gin.Recovery())
	r.Use(gin.Logger())

	// Health check endpoint
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"status":  "ok",
			"service": serviceName,
			"version": version,
		})
	})

	// API routes - placeholder for future implementation
	api := r.Group("/api/v1")
	{
		// TODO: Add service proxying to microservices
		api.GET("/status", func(c *gin.Context) {
			c.JSON(200, gin.H{"message": "API Gateway is running"})
		})
	}

	return r
}

func getServicePort(cfg *config.Config, defaultPort int) int {
	// This allows each service to override the default port
	// In a real deployment, you'd use service discovery or environment variables
	return defaultPort
}
