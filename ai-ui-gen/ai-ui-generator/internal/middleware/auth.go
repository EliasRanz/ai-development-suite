package middleware

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

// AuthMiddleware validates JWT tokens
func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get the Authorization header
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Authorization header required"})
			c.Abort()
			return
		}

		// Check for Bearer token
		if !strings.HasPrefix(authHeader, "Bearer ") {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid authorization header format"})
			c.Abort()
			return
		}

		// Extract token
		token := strings.TrimPrefix(authHeader, "Bearer ")
		if token == "" {
			c.JSON(http.StatusUnauthorized, gin.H{"error": "Token required"})
			c.Abort()
			return
		}

		// TODO: Validate JWT token with auth service
		// For now, just log the token validation attempt
		log.Debug().
			Str("token_prefix", token[:min(10, len(token))]).
			Msg("JWT token validation attempt")

		// TODO: Set user context from validated token
		// c.Set("user_id", userID)
		// c.Set("user_email", userEmail)

		c.Next()
	}
}

// OptionalAuth middleware that doesn't fail if no auth is provided
func OptionalAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		authHeader := c.GetHeader("Authorization")
		if authHeader == "" {
			c.Next()
			return
		}

		// Try to validate token but don't fail if invalid
		if strings.HasPrefix(authHeader, "Bearer ") {
			token := strings.TrimPrefix(authHeader, "Bearer ")
			if token != "" {
				// TODO: Validate token and set user context if valid
				log.Debug().
					Str("token_prefix", token[:min(10, len(token))]).
					Msg("Optional JWT token validation")
			}
		}

		c.Next()
	}
}

// AdminRequired middleware ensures user has admin privileges
func AdminRequired() gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Check user role from context
		// userRole := c.GetString("user_role")
		// if userRole != "admin" {
		//     c.JSON(http.StatusForbidden, gin.H{"error": "Admin access required"})
		//     c.Abort()
		//     return
		// }

		log.Debug().Msg("Admin access check")
		c.Next()
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
