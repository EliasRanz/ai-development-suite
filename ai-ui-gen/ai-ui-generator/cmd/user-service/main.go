package main

import (
	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	"github.com/ai-tools/ai-ui-generator/internal/config"
	"github.com/ai-tools/ai-ui-generator/internal/service"
)

func main() {
	// Initialize configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to load configuration")
	}

	// Override port for this service
	cfg.Server.Port = cfg.UserService.Port

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		log.Fatal().Err(err).Msg("Configuration validation failed")
	}

	// Create service
	svc := service.New("user-service", "1.0.0", cfg)

	// Initialize observability
	if err := svc.Initialize(); err != nil {
		log.Fatal().Err(err).Msg("Failed to initialize service")
	}

	// Setup placeholder routes (no business logic implemented yet)
	router := gin.New()
	router.Use(gin.Logger(), gin.Recovery())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": "user-service"})
	})

	// TODO: Implement user CRUD operations
	// TODO: Implement user profile management
	// TODO: Implement user preferences

	// Setup HTTP server
	svc.SetupHTTPServer(router)

	// Start service
	if err := svc.Start(); err != nil {
		log.Fatal().Err(err).Msg("Failed to start user service")
	}
}
