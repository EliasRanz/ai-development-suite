package generation

import (
	"context"
	"encoding/json"
	"fmt"
	"net/http"
	"strings"
	"time"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"

	"github.com/ai-tools/ai-ui-generator/internal/llm"
)

// RedisClient interface for Redis operations (stubbed for now)
type RedisClient interface {
	Ping(ctx context.Context) error
	Close() error
}

// stubRedisClient is a stub implementation of RedisClient
type stubRedisClient struct{}

func (s *stubRedisClient) Ping(ctx context.Context) error {
	// TODO: Implement actual Redis ping
	log.Debug().Msg("Redis ping (stubbed)")
	return nil
}

func (s *stubRedisClient) Close() error {
	// TODO: Implement actual Redis close
	log.Debug().Msg("Redis close (stubbed)")
	return nil
}

// Service provides AI generation functionality
type Service struct {
	llmClient llm.LLMClient
	redis     RedisClient
}

// Config holds configuration for the generation service
type Config struct {
	LLMConfig   *llm.VLLMConfig `json:"llm"`
	RedisConfig *RedisConfig    `json:"redis"`
}

// RedisConfig holds Redis configuration for pub/sub
type RedisConfig struct {
	Host     string `json:"host"`
	Port     int    `json:"port"`
	Password string `json:"password"`
	DB       int    `json:"db"`
}

// GenerationRequest represents the incoming generation request
type GenerationRequest struct {
	Model       string                 `json:"model" binding:"required"`
	Prompt      string                 `json:"prompt" binding:"required"`
	MaxTokens   int                    `json:"max_tokens,omitempty"`
	Temperature float64                `json:"temperature,omitempty"`
	Stream      bool                   `json:"stream,omitempty"`
	ProjectID   string                 `json:"project_id,omitempty"`
	Metadata    map[string]interface{} `json:"metadata,omitempty"`
}

// StreamResponse represents a server-sent event response
type StreamResponse struct {
	Event string      `json:"event"`
	Data  interface{} `json:"data"`
	ID    string      `json:"id,omitempty"`
}

// NewService creates a new generation service
func NewService(config *Config) (*Service, error) {
	// Initialize LLM client
	llmClient := llm.NewVLLMClient(config.LLMConfig)

	// Initialize Redis client (stubbed for now)
	var redisClient RedisClient
	if config.RedisConfig != nil {
		// TODO: Implement actual Redis client
		redisClient = &stubRedisClient{}
		
		// Test Redis connection
		ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
		defer cancel()

		if err := redisClient.Ping(ctx); err != nil {
			log.Warn().Err(err).Msg("Redis connection failed, continuing without Redis")
			redisClient = nil
		} else {
			log.Info().Msg("Redis connection established for generation service")
		}
	}

	return &Service{
		llmClient: llmClient,
		redis:     redisClient,
	}, nil
}

// StreamGenerationHandler handles the /generate/stream SSE endpoint
func (s *Service) StreamGenerationHandler(c *gin.Context) {
	// TODO: Add authentication middleware
	// For now, we'll extract user_id from headers if present
	userID := c.GetHeader("X-User-ID")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Authentication required"})
		return
	}

	var req GenerationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Set up SSE headers
	c.Header("Content-Type", "text/event-stream")
	c.Header("Cache-Control", "no-cache")
	c.Header("Connection", "keep-alive")
	c.Header("Access-Control-Allow-Origin", "*")
	c.Header("Access-Control-Allow-Headers", "Cache-Control")

	// Convert to LLM request
	llmReq := &llm.GenerationRequest{
		Model:       req.Model,
		Prompt:      req.Prompt,
		MaxTokens:   req.MaxTokens,
		Temperature: req.Temperature,
		Stream:      true,
		UserID:      userID,
		ProjectID:   req.ProjectID,
		Metadata:    req.Metadata,
	}

	// Start streaming generation
	ctx := c.Request.Context()
	respChan, err := s.llmClient.GenerateStream(ctx, llmReq)
	if err != nil {
		log.Error().Err(err).Msg("Failed to start generation stream")
		s.writeSSEError(c, "generation_failed", "Failed to start generation")
		return
	}

	// Stream the response
	s.streamResponse(c, respChan, userID, req.ProjectID)
}

// NonStreamGenerationHandler handles non-streaming generation requests
func (s *Service) NonStreamGenerationHandler(c *gin.Context) {
	// TODO: Add authentication middleware
	userID := c.GetHeader("X-User-ID")
	if userID == "" {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Authentication required"})
		return
	}

	var req GenerationRequest
	if err := c.ShouldBindJSON(&req); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	// Convert to LLM request
	llmReq := &llm.GenerationRequest{
		Model:       req.Model,
		Prompt:      req.Prompt,
		MaxTokens:   req.MaxTokens,
		Temperature: req.Temperature,
		Stream:      false,
		UserID:      userID,
		ProjectID:   req.ProjectID,
		Metadata:    req.Metadata,
	}

	// Generate response
	ctx := c.Request.Context()
	resp, err := s.llmClient.Generate(ctx, llmReq)
	if err != nil {
		log.Error().Err(err).Msg("Failed to generate response")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Generation failed"})
		return
	}

	c.JSON(http.StatusOK, resp)
}

// GetModelsHandler returns available models
func (s *Service) GetModelsHandler(c *gin.Context) {
	ctx := c.Request.Context()
	models, err := s.llmClient.GetModels(ctx)
	if err != nil {
		log.Error().Err(err).Msg("Failed to get models")
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to get models"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"models": models})
}

// HealthHandler checks the health of the generation service
func (s *Service) HealthHandler(c *gin.Context) {
	ctx := c.Request.Context()
	
	health := gin.H{
		"status": "healthy",
		"timestamp": time.Now().UTC(),
		"services": gin.H{
			"llm": "unknown",
			"redis": "unknown",
		},
	}

	// Check LLM health
	if err := s.llmClient.Health(ctx); err != nil {
		health["services"].(gin.H)["llm"] = "unhealthy"
		health["status"] = "degraded"
		log.Warn().Err(err).Msg("LLM service health check failed")
	} else {
		health["services"].(gin.H)["llm"] = "healthy"
	}

	// Check Redis health (if available)
	if s.redis != nil {
		if err := s.redis.Ping(ctx); err != nil {
			health["services"].(gin.H)["redis"] = "unhealthy"
			health["status"] = "degraded"
			log.Warn().Err(err).Msg("Redis health check failed")
		} else {
			health["services"].(gin.H)["redis"] = "healthy"
		}
	} else {
		health["services"].(gin.H)["redis"] = "disabled"
	}

	status := http.StatusOK
	if health["status"] == "degraded" {
		status = http.StatusServiceUnavailable
	}

	c.JSON(status, health)
}

// streamResponse handles the actual streaming of responses
func (s *Service) streamResponse(c *gin.Context, respChan <-chan *llm.GenerationResponse, userID, projectID string) {
	flusher, ok := c.Writer.(http.Flusher)
	if !ok {
		log.Error().Msg("Streaming unsupported")
		s.writeSSEError(c, "streaming_unsupported", "Streaming not supported")
		return
	}

	// Send initial event
	s.writeSSEEvent(c, "generation_started", gin.H{
		"message": "Generation started",
		"user_id": userID,
		"project_id": projectID,
	}, "")
	flusher.Flush()

	// Stream responses
	for resp := range respChan {
		// Publish to Redis for horizontal scaling (stubbed)
		if s.redis != nil {
			s.publishToRedis(resp, userID, projectID)
		}

		// Send the response chunk
		s.writeSSEEvent(c, "generation_chunk", resp, resp.ID)
		flusher.Flush()

		// Check if generation is complete
		if len(resp.Choices) > 0 && resp.Choices[0].FinishReason != nil {
			s.writeSSEEvent(c, "generation_complete", gin.H{
				"message": "Generation completed",
				"finish_reason": *resp.Choices[0].FinishReason,
				"usage": resp.Usage,
			}, "")
			flusher.Flush()
			break
		}
	}

	// Send final event
	s.writeSSEEvent(c, "stream_end", gin.H{"message": "Stream ended"}, "")
	flusher.Flush()
}

// writeSSEEvent writes a server-sent event
func (s *Service) writeSSEEvent(c *gin.Context, event string, data interface{}, id string) {
	if id != "" {
		fmt.Fprintf(c.Writer, "id: %s\n", id)
	}
	fmt.Fprintf(c.Writer, "event: %s\n", event)
	
	dataBytes, err := json.Marshal(data)
	if err != nil {
		log.Error().Err(err).Msg("Failed to marshal SSE data")
		dataBytes = []byte(`{"error": "Failed to marshal data"}`)
	}
	
	// Handle multi-line data
	dataStr := string(dataBytes)
	for _, line := range strings.Split(dataStr, "\n") {
		fmt.Fprintf(c.Writer, "data: %s\n", line)
	}
	fmt.Fprintf(c.Writer, "\n")
}

// writeSSEError writes an error event
func (s *Service) writeSSEError(c *gin.Context, errorCode, message string) {
	s.writeSSEEvent(c, "error", gin.H{
		"error": errorCode,
		"message": message,
	}, "")
}

// publishToRedis publishes generation events to Redis for horizontal scaling (stubbed)
func (s *Service) publishToRedis(resp *llm.GenerationResponse, userID, projectID string) {
	// TODO: Implement actual Redis pub/sub for horizontal scaling
	log.Debug().
		Str("user_id", userID).
		Str("project_id", projectID).
		Str("response_id", resp.ID).
		Msg("Publishing to Redis (stubbed)")

	// This would publish to a channel like:
	// PUBLISH generation:user:${userID} ${json_response}
	// PUBLISH generation:project:${projectID} ${json_response}
}

// Close closes the service and its dependencies
func (s *Service) Close() error {
	var err error

	if s.llmClient != nil {
		if closeErr := s.llmClient.Close(); closeErr != nil {
			err = closeErr
		}
	}

	if s.redis != nil {
		if closeErr := s.redis.Close(); closeErr != nil {
			err = closeErr
		}
	}

	return err
}
