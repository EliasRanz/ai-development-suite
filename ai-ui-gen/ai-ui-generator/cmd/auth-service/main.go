package main

import (
	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	"github.com/ai-tools/ai-ui-generator/internal/config"
	"github.com/ai-tools/ai-ui-generator/internal/service"
	"github.com/ai-tools/ai-ui-generator/internal/auth"
)

func main() {
	// Initialize configuration
	cfg, err := config.Load()
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to load configuration")
	}

	// Override port for this service
	cfg.Server.Port = cfg.AuthService.Port

	// Validate configuration
	if err := cfg.Validate(); err != nil {
		log.Fatal().Err(err).Msg("Configuration validation failed")
	}

	// Create service
	svc := service.New("auth-service", "1.0.0", cfg)

	// Initialize observability
	if err := svc.Initialize(); err != nil {
		log.Fatal().Err(err).Msg("Failed to initialize service")
	}

	// Setup router with auth endpoints
	router := setupAuthRouter(cfg)

	// Setup HTTP server
	svc.SetupHTTPServer(router)

	// Start service
	if err := svc.Start(); err != nil {
		log.Fatal().Err(err).Msg("Failed to start auth service")
	}
}

// setupAuthRouter configures all authentication routes
func setupAuthRouter(cfg *config.Config) *gin.Engine {
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(gin.Logger())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": "auth-service"})
	})

	// Authentication endpoints
	authGroup := router.Group("/auth")
	{
		// OAuth login endpoints
		authGroup.POST("/login", auth.LoginHandler)
		authGroup.GET("/login/google", auth.GoogleOAuthHandler)
		authGroup.GET("/callback/google", auth.GoogleCallbackHandler)
		
		// JWT token management
		authGroup.POST("/refresh", auth.RefreshTokenHandler)
		authGroup.POST("/logout", auth.LogoutHandler)
		authGroup.POST("/validate", auth.ValidateTokenHandler)
		
		// User registration (if not using OAuth)
		authGroup.POST("/register", auth.RegisterHandler)
	}

	// Protected routes for token introspection
	protected := router.Group("/")
	protected.Use(auth.JWTMiddleware())
	{
		protected.GET("/user", auth.GetUserHandler)
		protected.POST("/change-password", auth.ChangePasswordHandler)
	}

	return router
}
