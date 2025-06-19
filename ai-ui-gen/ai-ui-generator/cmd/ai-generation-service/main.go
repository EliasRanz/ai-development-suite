package main

import (
	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	"github.com/ai-tools/ai-ui-generator/internal/config"
	"github.com/ai-tools/ai-ui-generator/internal/generation"
	"github.com/ai-tools/ai-ui-generator/internal/llm"
	"github.com/ai-tools/ai-ui-generator/internal/service"
)

func main() {
	// Initialize configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to load configuration")
	}

	// Override port for this service
	cfg.Server.Port = cfg.AIGenService.Port

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		log.Fatal().Err(err).Msg("Configuration validation failed")
	}

	// Create service
	svc := service.New("ai-generation-service", "1.0.0", cfg)

	// Initialize observability
	if err := svc.Initialize(); err != nil {
		log.Fatal().Err(err).Msg("Failed to initialize service")
	}

	// Initialize generation service
	genConfig := &generation.Config{
		LLMConfig: &llm.VLLMConfig{
			BaseURL:    cfg.AI.LLM.BaseURL,
			APIKey:     cfg.AI.LLM.APIKey,
			Timeout:    cfg.AI.LLM.Timeout,
			MaxRetries: cfg.AI.LLM.MaxRetries,
		},
		RedisConfig: &generation.RedisConfig{
			Host:     cfg.Redis.Host,
			Port:     cfg.Redis.Port,
			Password: cfg.Redis.Password,
			DB:       cfg.Redis.DB,
		},
	}

	genService, err := generation.NewService(genConfig)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to create generation service")
	}
	defer genService.Close()

	// Setup HTTP router
	router := setupGenerationRouter(cfg, genService)

	// Setup HTTP server
	svc.SetupHTTPServer(router)

	// Start service
	if err := svc.Start(); err != nil {
		log.Fatal().Err(err).Msg("Failed to start AI generation service")
	}
}

// setupGenerationRouter configures all generation routes
func setupGenerationRouter(cfg *config.Config, genService *generation.Service) *gin.Engine {
	router := gin.New()
	router.Use(gin.Logger())
	router.Use(gin.Recovery())

	// Health check endpoint
	router.GET("/health", genService.HealthHandler)

	// Generation endpoints
	router.POST("/generate", genService.NonStreamGenerationHandler)
	router.POST("/generate/stream", genService.StreamGenerationHandler)

	// Models endpoint
	router.GET("/models", genService.GetModelsHandler)

	// Version endpoint
	router.GET("/version", func(c *gin.Context) {
		c.JSON(200, gin.H{
			"service": "ai-generation-service",
			"version": "1.0.0",
			"status":  "ready",
		})
	})

	return router
}
