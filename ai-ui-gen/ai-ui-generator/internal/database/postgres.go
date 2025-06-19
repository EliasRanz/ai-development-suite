package database

import (
	"database/sql"
	
	_ "github.com/lib/pq" // PostgreSQL driver
)

// Config holds database configuration
type Config struct {
	Host     string
	Port     int
	User     string
	Password string
	DBName   string
	SSLMode  string
}

// Connection holds database connection and metadata
type Connection struct {
	DB     *sql.DB
	Config *Config
}

// Close closes the database connection
func (c *Connection) Close() error {
	if c.DB != nil {
		return c.DB.Close()
	}
	return nil
}

// Health checks database health
func (c *Connection) Health() error {
	// TODO: Implement health check
	return c.DB.Ping()
}

// Migrate runs database migrations
func (c *Connection) Migrate() error {
	// TODO: Implement database migrations
	// This would typically use a migration library
	return nil
}
