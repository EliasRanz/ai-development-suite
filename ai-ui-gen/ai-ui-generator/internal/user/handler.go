package user

import (
	"net/http"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	pb "github.com/ai-tools/ai-ui-generator/api/proto/user"
)

// Global gRPC client - will be set by the main function
var grpcClient *GRPCClient

// SetGRPCClient sets the global gRPC client for handlers
func SetGRPCClient(client *GRPCClient) {
	grpcClient = client
}

// User HTTP handlers that call gRPC service

// CreateUserHandler handles user creation
func CreateUserHandler(c *gin.Context) {
	log.Info().Msg("Create user request")
	
	var req struct {
		Email     string   `json:"email" binding:"required"`
		Name      string   `json:"name" binding:"required"`
		AvatarURL string   `json:"avatar_url"`
		Roles     []string `json:"roles"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	if grpcClient == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "gRPC client not initialized"})
		return
	}
	
	grpcReq := &pb.CreateUserRequest{
		Email:     req.Email,
		Name:      req.Name,
		AvatarUrl: req.AvatarURL,
		Roles:     req.Roles,
	}
	
	resp, err := grpcClient.CreateUser(grpcReq)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create user via gRPC")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create user"})
		return
	}
	
	if resp.Error != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": resp.Error})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"user": gin.H{
			"id":         resp.User.Id,
			"email":      resp.User.Email,
			"name":       resp.User.Name,
			"avatar_url": resp.User.AvatarUrl,
			"roles":      resp.User.Roles,
			"created_at": resp.User.CreatedAt,
			"updated_at": resp.User.UpdatedAt,
		},
	})
}

// GetUserHandler retrieves a user by ID
func GetUserHandler(c *gin.Context) {
	userID := c.Param("id")
	log.Info().Str("user_id", userID).Msg("Get user request")
	
	if grpcClient == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "gRPC client not initialized"})
		return
	}
	
	resp, err := grpcClient.GetUser(userID)
	if err != nil {
		log.Error().Err(err).Msg("Failed to get user via gRPC")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get user"})
		return
	}
	
	if resp.Error != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": resp.Error})
		return
	}
	
	if resp.User == nil {
		c.JSON(http.StatusNotFound, gin.H{"error": "User not found"})
		return
	}
	
	c.JSON(http.StatusOK, gin.H{
		"user": gin.H{
			"id":         resp.User.Id,
			"email":      resp.User.Email,
			"name":       resp.User.Name,
			"avatar_url": resp.User.AvatarUrl,
			"roles":      resp.User.Roles,
			"created_at": resp.User.CreatedAt,
			"updated_at": resp.User.UpdatedAt,
		},
	})
}

// UpdateUserHandler updates a user
func UpdateUserHandler(c *gin.Context) {
	userID := c.Param("id")
	log.Info().Str("user_id", userID).Msg("Update user request")
	
	// TODO: Parse request body
	// TODO: Call gRPC UpdateUser method
	// TODO: Return updated user
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Update user endpoint - not implemented yet",
		"user_id": userID,
	})
}

// DeleteUserHandler deletes a user
func DeleteUserHandler(c *gin.Context) {
	userID := c.Param("id")
	log.Info().Str("user_id", userID).Msg("Delete user request")
	
	// TODO: Call gRPC DeleteUser method
	// TODO: Return success/error
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Delete user endpoint - not implemented yet",
		"user_id": userID,
	})
}

// ListUsersHandler lists users with pagination
func ListUsersHandler(c *gin.Context) {
	log.Info().Msg("List users request")
	
	// Parse query parameters
	page := ParseInt32(c.Query("page"), 1)
	limit := ParseInt32(c.Query("limit"), 10)
	search := c.Query("search")
	
	if grpcClient == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "gRPC client not initialized"})
		return
	}
	
	resp, err := grpcClient.ListUsers(page, limit, search)
	if err != nil {
		log.Error().Err(err).Msg("Failed to list users via gRPC")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to list users"})
		return
	}
	
	if resp.Error != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": resp.Error})
		return
	}
	
	users := make([]gin.H, len(resp.Users))
	for i, user := range resp.Users {
		users[i] = gin.H{
			"id":         user.Id,
			"email":      user.Email,
			"name":       user.Name,
			"avatar_url": user.AvatarUrl,
			"roles":      user.Roles,
			"created_at": user.CreatedAt,
			"updated_at": user.UpdatedAt,
		}
	}
	
	c.JSON(http.StatusOK, gin.H{
		"users": users,
		"total": resp.Total,
		"page":  page,
		"limit": limit,
	})
}

// GetUserProfileHandler gets user profile
func GetUserProfileHandler(c *gin.Context) {
	userID := c.Param("id")
	log.Info().Str("user_id", userID).Msg("Get user profile request")
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Get user profile endpoint - not implemented yet",
		"user_id": userID,
		"profile": gin.H{},
	})
}

// UpdateUserProfileHandler updates user profile
func UpdateUserProfileHandler(c *gin.Context) {
	userID := c.Param("id")
	log.Info().Str("user_id", userID).Msg("Update user profile request")
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Update user profile endpoint - not implemented yet",
		"user_id": userID,
	})
}

// Project handlers

// CreateProjectHandler creates a new project
func CreateProjectHandler(c *gin.Context) {
	log.Info().Msg("Create project request")
	
	var req struct {
		Name        string   `json:"name" binding:"required"`
		Description string   `json:"description"`
		UserID      string   `json:"user_id" binding:"required"`
		Tags        []string `json:"tags"`
		Config      string   `json:"config"`
	}
	
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}
	
	if grpcClient == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "gRPC client not initialized"})
		return
	}
	
	grpcReq := &pb.CreateProjectRequest{
		Name:        req.Name,
		Description: req.Description,
		UserId:      req.UserID,
		Tags:        req.Tags,
		Config:      req.Config,
	}
	
	resp, err := grpcClient.CreateProject(grpcReq)
	if err != nil {
		log.Error().Err(err).Msg("Failed to create project via gRPC")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create project"})
		return
	}
	
	if resp.Error != "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": resp.Error})
		return
	}
	
	c.JSON(http.StatusCreated, gin.H{
		"project": gin.H{
			"id":          resp.Project.Id,
			"name":        resp.Project.Name,
			"description": resp.Project.Description,
			"user_id":     resp.Project.UserId,
			"status":      resp.Project.Status.String(),
			"tags":        resp.Project.Tags,
			"config":      resp.Project.Config,
			"created_at":  resp.Project.CreatedAt,
			"updated_at":  resp.Project.UpdatedAt,
		},
	})
}

// GetProjectHandler retrieves a project by ID
func GetProjectHandler(c *gin.Context) {
	projectID := c.Param("id")
	log.Info().Str("project_id", projectID).Msg("Get project request")
	
	// TODO: Call gRPC GetProject method
	// TODO: Return project data
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Get project endpoint - not implemented yet",
		"project_id": projectID,
		"name": "Sample Project",
		"description": "A sample project",
	})
}

// UpdateProjectHandler updates a project
func UpdateProjectHandler(c *gin.Context) {
	projectID := c.Param("id")
	log.Info().Str("project_id", projectID).Msg("Update project request")
	
	// TODO: Parse request body
	// TODO: Call gRPC UpdateProject method
	// TODO: Return updated project
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Update project endpoint - not implemented yet",
		"project_id": projectID,
	})
}

// DeleteProjectHandler deletes a project
func DeleteProjectHandler(c *gin.Context) {
	projectID := c.Param("id")
	log.Info().Str("project_id", projectID).Msg("Delete project request")
	
	// TODO: Call gRPC DeleteProject method
	// TODO: Return success/error
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Delete project endpoint - not implemented yet",
		"project_id": projectID,
	})
}

// ListProjectsHandler lists projects with pagination
func ListProjectsHandler(c *gin.Context) {
	log.Info().Msg("List projects request")
	
	// TODO: Parse query parameters (page, limit, search, status)
	// TODO: Call gRPC ListProjects method
	// TODO: Return paginated project list
	
	c.JSON(http.StatusOK, gin.H{
		"message": "List projects endpoint - not implemented yet",
		"projects": []gin.H{},
		"total": 0,
		"page": 1,
	})
}

// ListUserProjectsHandler lists projects for a specific user
func ListUserProjectsHandler(c *gin.Context) {
	userID := c.Param("user_id")
	log.Info().Str("user_id", userID).Msg("List user projects request")
	
	// TODO: Parse query parameters (page, limit, status)
	// TODO: Call gRPC ListUserProjects method
	// TODO: Return user's projects
	
	c.JSON(http.StatusOK, gin.H{
		"message": "List user projects endpoint - not implemented yet",
		"user_id": userID,
		"projects": []gin.H{},
		"total": 0,
	})
}

// Admin handlers

// AdminListUsersHandler lists all users (admin only)
func AdminListUsersHandler(c *gin.Context) {
	log.Info().Msg("Admin list users request")
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Admin list users endpoint - not implemented yet",
		"users": []gin.H{},
		"total": 0,
	})
}

// AdminListProjectsHandler lists all projects (admin only)
func AdminListProjectsHandler(c *gin.Context) {
	log.Info().Msg("Admin list projects request")
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Admin list projects endpoint - not implemented yet",
		"projects": []gin.H{},
		"total": 0,
	})
}

// GetStatsHandler returns system statistics
func GetStatsHandler(c *gin.Context) {
	log.Info().Msg("Get stats request")
	
	c.JSON(http.StatusOK, gin.H{
		"message": "Get stats endpoint - not implemented yet",
		"stats": gin.H{
			"total_users": 0,
			"total_projects": 0,
			"active_projects": 0,
		},
	})
}

// Legacy handler struct for compatibility
type Handler struct {
	service *Service
}

// NewHandler creates a new user handler
func NewHandler(service *Service) *Handler {
	return &Handler{
		service: service,
	}
}

// Legacy methods that delegate to the new handlers
func (h *Handler) GetUser(c *gin.Context) {
	GetUserHandler(c)
}

func (h *Handler) UpdateUser(c *gin.Context) {
	UpdateUserHandler(c)
}

func (h *Handler) DeleteUser(c *gin.Context) {
	DeleteUserHandler(c)
}

func (h *Handler) ListUsers(c *gin.Context) {
	ListUsersHandler(c)
}
