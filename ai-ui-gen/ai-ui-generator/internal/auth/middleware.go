package auth

import (
	"net/http"
	"strings"

	"github.com/gin-gonic/gin"
	"github.com/rs/zerolog/log"
)

// JWTMiddleware validates JWT tokens for protected routes
func JWTMiddleware() gin.HandlerFunc {
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

		// TODO: Validate JWT token
		// 1. Parse JWT token
		// 2. Verify signature with secret key
		// 3. Check expiration
		// 4. Extract claims (user_id, email, roles, etc.)
		
		log.Debug().
			Str("token_prefix", token[:min(10, len(token))]).
			Msg("JWT token validation in auth service")

		// TODO: Set user context from validated token claims
		// userID, email, roles := validateJWT(token)
		// c.Set("user_id", userID)
		// c.Set("user_email", email)
		// c.Set("user_roles", roles)

		// For now, set placeholder values
		c.Set("user_id", "placeholder_user_id")
		c.Set("user_email", "user@example.com")
		c.Set("user_roles", []string{"user"})

		c.Next()
	}
}

// AuthMiddleware provides JWT authentication middleware (legacy function for compatibility)
func AuthMiddleware(tokenManager *TokenManager) gin.HandlerFunc {
	return JWTMiddleware()
}

// RequireAuth ensures user is authenticated
func RequireAuth() gin.HandlerFunc {
	return JWTMiddleware()
}

// RequireAdmin ensures user has admin privileges
func RequireAdmin() gin.HandlerFunc {
	return func(c *gin.Context) {
		// Get user roles from context (set by JWT middleware)
		roles, exists := c.Get("user_roles")
		if !exists {
			c.JSON(http.StatusForbidden, gin.H{"error": "User roles not found"})
			c.Abort()
			return
		}

		userRoles, ok := roles.([]string)
		if !ok {
			c.JSON(http.StatusForbidden, gin.H{"error": "Invalid user roles"})
			c.Abort()
			return
		}

		// Check if user has admin role
		hasAdmin := false
		for _, role := range userRoles {
			if role == "admin" {
				hasAdmin = true
				break
			}
		}

		if !hasAdmin {
			c.JSON(http.StatusForbidden, gin.H{"error": "Admin access required"})
			c.Abort()
			return
		}

		log.Debug().
			Str("user_id", c.GetString("user_id")).
			Msg("Admin access granted")

		c.Next()
	}
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}
