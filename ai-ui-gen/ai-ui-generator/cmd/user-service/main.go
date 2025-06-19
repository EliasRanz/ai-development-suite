package main

import (
	"fmt"
	"net"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
	"google.golang.org/grpc"

	"github.com/ai-tools/ai-ui-generator/internal/config"
	"github.com/ai-tools/ai-ui-generator/internal/database"
	"github.com/ai-tools/ai-ui-generator/internal/service"
	"github.com/ai-tools/ai-ui-generator/internal/user"
	pb "github.com/ai-tools/ai-ui-generator/api/proto/user"
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

	// Initialize database connection
	db, err := database.NewConnection(&cfg.Database)
	if err != nil {
		log.Fatal().Err(err).Msg("Failed to connect to database")
	}
	defer database.Close(db)

	// Initialize repositories
	userRepo := user.NewPostgresRepository(db)
	projectRepo := user.NewPostgresProjectRepository(db)
	
	// Initialize user service with project repository
	userService := user.NewServiceWithProjects(userRepo, projectRepo)
	
	// Initialize gRPC server
	userGRPCServer := user.NewGRPCServer(userService)
	
	// Initialize gRPC client for HTTP handlers
	grpcClient := user.NewGRPCClient(userGRPCServer)
	user.SetGRPCClient(grpcClient)
	
	// Setup HTTP router with user and project endpoints
	router := setupUserRouter(cfg, userService)

	// Setup HTTP server
	svc.SetupHTTPServer(router)

	// Start gRPC server in a goroutine
	go func() {
		if err := startGRPCServer(cfg, userGRPCServer); err != nil {
			log.Fatal().Err(err).Msg("Failed to start gRPC server")
		}
	}()

	// Start service
	if err := svc.Start(); err != nil {
		log.Fatal().Err(err).Msg("Failed to start user service")
	}
}

// setupUserRouter configures all user and project routes
func setupUserRouter(cfg *config.Config, userService *user.Service) *gin.Engine {
	router := gin.New()
	router.Use(gin.Recovery())
	router.Use(gin.Logger())

	// Health check endpoint
	router.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": "user-service"})
	})

	// User management endpoints
	userGroup := router.Group("/users")
	{
		userGroup.GET("/:id", user.GetUserHandler)
		userGroup.PUT("/:id", user.UpdateUserHandler)
		userGroup.DELETE("/:id", user.DeleteUserHandler)
		userGroup.GET("/", user.ListUsersHandler)
		userGroup.POST("/", user.CreateUserHandler)
		
		// User profile endpoints
		userGroup.GET("/:id/profile", user.GetUserProfileHandler)
		userGroup.PUT("/:id/profile", user.UpdateUserProfileHandler)
	}

	// Project management endpoints
	projectGroup := router.Group("/projects")
	{
		projectGroup.POST("/", user.CreateProjectHandler)
		projectGroup.GET("/:id", user.GetProjectHandler)
		projectGroup.PUT("/:id", user.UpdateProjectHandler)
		projectGroup.DELETE("/:id", user.DeleteProjectHandler)
		projectGroup.GET("/", user.ListProjectsHandler)
		
		// User-specific project endpoints
		projectGroup.GET("/user/:user_id", user.ListUserProjectsHandler)
	}

	// Admin endpoints
	adminGroup := router.Group("/admin")
	{
		adminGroup.GET("/users", user.AdminListUsersHandler)
		adminGroup.GET("/projects", user.AdminListProjectsHandler)
		adminGroup.GET("/stats", user.GetStatsHandler)
	}

	return router
}

// startGRPCServer starts the gRPC server
func startGRPCServer(cfg *config.Config, userGRPCServer *user.GRPCServer) error {
	// Calculate gRPC port (HTTP port + 1000)
	grpcPort := cfg.UserService.Port + 1000
	
	lis, err := net.Listen("tcp", fmt.Sprintf(":%d", grpcPort))
	if err != nil {
		return err
	}

	grpcServer := grpc.NewServer()
	pb.RegisterUserServiceServer(grpcServer, userGRPCServer)

	log.Info().
		Int("port", grpcPort).
		Msg("Starting gRPC server")

	return grpcServer.Serve(lis)
}
