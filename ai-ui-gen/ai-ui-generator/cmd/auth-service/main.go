package main

import (
	"log"
	"github.com/gin-gonic/gin"
)

func main() {
	// TODO: Initialize configuration
	// TODO: Setup database connection
	// TODO: Setup gRPC server
	// TODO: Initialize observability
	
	r := gin.Default()
	
	// Placeholder routes
	r.GET("/health", func(c *gin.Context) {
		c.JSON(200, gin.H{"status": "ok", "service": "auth-service"})
	})
	
	// TODO: Implement OAuth 2.0 endpoints
	// TODO: Implement JWT token management
	// TODO: Implement user authentication
	
	log.Println("Starting Auth Service on :8081")
	r.Run(":8081")
}
