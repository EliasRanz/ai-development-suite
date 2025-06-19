package main

import (
	"log"
	"github.com/gin-gonic/gin"
)

func main() {
	// TODO: Initialize configuration
	// TODO: Setup middleware (CORS, logging, etc.)
	// TODO: Setup routes and proxy to microservices
	// TODO: Initialize observability (metrics, tracing)
	
	r := gin.Default()
	
	// Placeholder routes
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": "api-gateway"})
	})
	
	// TODO: Setup auth middleware
	// TODO: Setup service proxying
	// TODO: Setup WebSocket/SSE endpoints
	
	log.Println("Starting API Gateway on :8080")
	r.Run(":8080")
}
