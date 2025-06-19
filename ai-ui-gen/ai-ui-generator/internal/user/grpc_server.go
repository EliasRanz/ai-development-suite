package user

import (
	"context"

	"github.com/rs/zerolog/log"

	pb "github.com/ai-tools/ai-ui-generator/api/proto/user"
)

// GRPCServer implements the UserService gRPC interface
type GRPCServer struct {
	pb.UnimplementedUserServiceServer
	service *Service
}

// NewGRPCServer creates a new gRPC server instance
func NewGRPCServer(service *Service) *GRPCServer {
	return &GRPCServer{
		service: service,
	}
}

// User management methods

// CreateUser creates a new user
func (s *GRPCServer) CreateUser(ctx context.Context, req *pb.CreateUserRequest) (*pb.CreateUserResponse, error) {
	log.Info().
		Str("email", req.Email).
		Str("name", req.Name).
		Msg("gRPC CreateUser called")

	// TODO: Implement user creation logic
	// For now, return a stub response
	user := &pb.User{
		Id:        "user_" + generateID(),
		Email:     req.Email,
		Name:      req.Name,
		AvatarUrl: req.AvatarUrl,
		Roles:     req.Roles,
		CreatedAt: getCurrentTimestamp(),
		UpdatedAt: getCurrentTimestamp(),
	}

	return &pb.CreateUserResponse{
		User:  user,
		Error: "",
	}, nil
}

// GetUser retrieves a user by ID
func (s *GRPCServer) GetUser(ctx context.Context, req *pb.GetUserRequest) (*pb.GetUserResponse, error) {
	log.Info().
		Str("user_id", req.Id).
		Msg("gRPC GetUser called")

	// TODO: Implement user retrieval logic
	// For now, return a stub response
	user := &pb.User{
		Id:        req.Id,
		Email:     "john@example.com",
		Name:      "John Doe",
		AvatarUrl: "https://example.com/avatar.jpg",
		Roles:     []string{"user"},
		CreatedAt: getCurrentTimestamp(),
		UpdatedAt: getCurrentTimestamp(),
	}

	return &pb.GetUserResponse{
		User:  user,
		Error: "",
	}, nil
}

// UpdateUser updates an existing user
func (s *GRPCServer) UpdateUser(ctx context.Context, req *pb.UpdateUserRequest) (*pb.UpdateUserResponse, error) {
	log.Info().
		Str("user_id", req.Id).
		Str("name", req.Name).
		Msg("gRPC UpdateUser called")

	// TODO: Implement user update logic
	// For now, return a stub response
	user := &pb.User{
		Id:        req.Id,
		Email:     "john@example.com", // Keep existing email
		Name:      req.Name,
		AvatarUrl: req.AvatarUrl,
		Roles:     req.Roles,
		CreatedAt: getCurrentTimestamp() - 3600, // Fake older creation time
		UpdatedAt: getCurrentTimestamp(),
	}

	return &pb.UpdateUserResponse{
		User:  user,
		Error: "",
	}, nil
}

// DeleteUser deletes a user
func (s *GRPCServer) DeleteUser(ctx context.Context, req *pb.DeleteUserRequest) (*pb.DeleteUserResponse, error) {
	log.Info().
		Str("user_id", req.Id).
		Msg("gRPC DeleteUser called")

	// TODO: Implement user deletion logic
	// For now, return success
	return &pb.DeleteUserResponse{
		Success: true,
		Error:   "",
	}, nil
}

// ListUsers lists users with pagination
func (s *GRPCServer) ListUsers(ctx context.Context, req *pb.ListUsersRequest) (*pb.ListUsersResponse, error) {
	log.Info().
		Int32("page", req.Page).
		Int32("limit", req.Limit).
		Str("search", req.Search).
		Msg("gRPC ListUsers called")

	// TODO: Implement user listing logic
	// For now, return stub data
	users := []*pb.User{
		{
			Id:        "user_1",
			Email:     "john@example.com",
			Name:      "John Doe",
			AvatarUrl: "https://example.com/john.jpg",
			Roles:     []string{"user"},
			CreatedAt: getCurrentTimestamp(),
			UpdatedAt: getCurrentTimestamp(),
		},
		{
			Id:        "user_2",
			Email:     "jane@example.com",
			Name:      "Jane Smith",
			AvatarUrl: "https://example.com/jane.jpg",
			Roles:     []string{"user", "admin"},
			CreatedAt: getCurrentTimestamp(),
			UpdatedAt: getCurrentTimestamp(),
		},
	}

	return &pb.ListUsersResponse{
		Users: users,
		Total: int32(len(users)),
		Error: "",
	}, nil
}

// Project management methods

// CreateProject creates a new project
func (s *GRPCServer) CreateProject(ctx context.Context, req *pb.CreateProjectRequest) (*pb.CreateProjectResponse, error) {
	log.Info().
		Str("name", req.Name).
		Str("user_id", req.UserId).
		Msg("gRPC CreateProject called")

	// TODO: Implement project creation logic
	project := &pb.Project{
		Id:          "project_" + generateID(),
		Name:        req.Name,
		Description: req.Description,
		UserId:      req.UserId,
		Status:      pb.ProjectStatus_PROJECT_STATUS_DRAFT,
		Tags:        req.Tags,
		Config:      req.Config,
		CreatedAt:   getCurrentTimestamp(),
		UpdatedAt:   getCurrentTimestamp(),
	}

	return &pb.CreateProjectResponse{
		Project: project,
		Error:   "",
	}, nil
}

// GetProject retrieves a project by ID
func (s *GRPCServer) GetProject(ctx context.Context, req *pb.GetProjectRequest) (*pb.GetProjectResponse, error) {
	log.Info().
		Str("project_id", req.Id).
		Msg("gRPC GetProject called")

	// TODO: Implement project retrieval logic
	project := &pb.Project{
		Id:          req.Id,
		Name:        "Sample Project",
		Description: "A sample project for demonstration",
		UserId:      "user_1",
		Status:      pb.ProjectStatus_PROJECT_STATUS_ACTIVE,
		Tags:        []string{"sample", "demo"},
		Config:      `{"theme": "dark", "features": ["ai", "ui"]}`,
		CreatedAt:   getCurrentTimestamp(),
		UpdatedAt:   getCurrentTimestamp(),
	}

	return &pb.GetProjectResponse{
		Project: project,
		Error:   "",
	}, nil
}

// UpdateProject updates an existing project
func (s *GRPCServer) UpdateProject(ctx context.Context, req *pb.UpdateProjectRequest) (*pb.UpdateProjectResponse, error) {
	log.Info().
		Str("project_id", req.Id).
		Str("name", req.Name).
		Msg("gRPC UpdateProject called")

	// TODO: Implement project update logic
	project := &pb.Project{
		Id:          req.Id,
		Name:        req.Name,
		Description: req.Description,
		UserId:      "user_1", // Keep existing user
		Status:      req.Status,
		Tags:        req.Tags,
		Config:      req.Config,
		CreatedAt:   getCurrentTimestamp() - 3600,
		UpdatedAt:   getCurrentTimestamp(),
	}

	return &pb.UpdateProjectResponse{
		Project: project,
		Error:   "",
	}, nil
}

// DeleteProject deletes a project
func (s *GRPCServer) DeleteProject(ctx context.Context, req *pb.DeleteProjectRequest) (*pb.DeleteProjectResponse, error) {
	log.Info().
		Str("project_id", req.Id).
		Msg("gRPC DeleteProject called")

	// TODO: Implement project deletion logic
	return &pb.DeleteProjectResponse{
		Success: true,
		Error:   "",
	}, nil
}

// ListProjects lists projects with pagination
func (s *GRPCServer) ListProjects(ctx context.Context, req *pb.ListProjectsRequest) (*pb.ListProjectsResponse, error) {
	log.Info().
		Int32("page", req.Page).
		Int32("limit", req.Limit).
		Str("search", req.Search).
		Msg("gRPC ListProjects called")

	// TODO: Implement project listing logic
	projects := []*pb.Project{
		{
			Id:          "project_1",
			Name:        "AI Dashboard",
			Description: "A modern AI dashboard",
			UserId:      "user_1",
			Status:      pb.ProjectStatus_PROJECT_STATUS_ACTIVE,
			Tags:        []string{"ai", "dashboard"},
			Config:      `{"theme": "dark"}`,
			CreatedAt:   getCurrentTimestamp(),
			UpdatedAt:   getCurrentTimestamp(),
		},
		{
			Id:          "project_2",
			Name:        "UI Components",
			Description: "Reusable UI components",
			UserId:      "user_2",
			Status:      pb.ProjectStatus_PROJECT_STATUS_DRAFT,
			Tags:        []string{"ui", "components"},
			Config:      `{"theme": "light"}`,
			CreatedAt:   getCurrentTimestamp(),
			UpdatedAt:   getCurrentTimestamp(),
		},
	}

	return &pb.ListProjectsResponse{
		Projects: projects,
		Total:    int32(len(projects)),
		Error:    "",
	}, nil
}

// ListUserProjects lists projects for a specific user
func (s *GRPCServer) ListUserProjects(ctx context.Context, req *pb.ListUserProjectsRequest) (*pb.ListUserProjectsResponse, error) {
	log.Info().
		Str("user_id", req.UserId).
		Int32("page", req.Page).
		Int32("limit", req.Limit).
		Msg("gRPC ListUserProjects called")

	// TODO: Implement user-specific project listing logic
	projects := []*pb.Project{
		{
			Id:          "project_1",
			Name:        "User's Project",
			Description: "A project owned by the user",
			UserId:      req.UserId,
			Status:      pb.ProjectStatus_PROJECT_STATUS_ACTIVE,
			Tags:        []string{"personal"},
			Config:      `{"theme": "auto"}`,
			CreatedAt:   getCurrentTimestamp(),
			UpdatedAt:   getCurrentTimestamp(),
		},
	}

	return &pb.ListUserProjectsResponse{
		Projects: projects,
		Total:    int32(len(projects)),
		Error:    "",
	}, nil
}

// Helper functions

// generateID generates a simple ID for demo purposes
func generateID() string {
	// TODO: Use a proper UUID library
	return "12345678"
}

// getCurrentTimestamp returns the current Unix timestamp
func getCurrentTimestamp() int64 {
	// TODO: Use time.Now().Unix()
	return 1704067200 // 2024-01-01 00:00:00 UTC for demo
}
