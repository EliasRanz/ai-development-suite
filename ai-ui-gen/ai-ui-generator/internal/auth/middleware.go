package auth

import (
	"github.com/gin-gonic/gin"
)

// AuthMiddleware provides JWT authentication middleware
func AuthMiddleware(tokenManager *TokenManager) gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Implement JWT middleware
		// 1. Extract token from Authorization header
		// 2. Validate token
		// 3. Set user context
		// 4. Call next handler or return unauthorized
		
		c.Next()
	}
}

// RequireAuth ensures user is authenticated
func RequireAuth() gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Check if user is authenticated from context
		c.Next()
	}
}

// RequireAdmin ensures user has admin privileges
func RequireAdmin() gin.HandlerFunc {
	return func(c *gin.Context) {
		// TODO: Check if user has admin role
		c.Next()
	}
}
