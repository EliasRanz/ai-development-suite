# Coding Standards for AI Agents

## SOLID Principles (MANDATORY)
```go
// Single Responsibility - One reason to change
type UserService struct{}
func (s *UserService) CreateUser(user User) error

// Open/Closed - Open for extension, closed for modification  
type Handler interface {
    Handle(request Request) Response
}

// Liskov Substitution - Subtypes must be substitutable
type Database interface {
    Save(entity interface{}) error
}

// Interface Segregation - Small, focused interfaces
type Reader interface { Read([]byte) (int, error) }
type Writer interface { Write([]byte) (int, error) }

// Dependency Inversion - Depend on abstractions
type Service struct {
    repo Repository // interface, not concrete type
}
```

## DRY Principle
- EXTRACT common functionality into shared functions
- USE composition over inheritance
- CREATE shared interfaces for similar operations

## KISS Principle  
- CHOOSE simplest solution that works
- AVOID over-engineering
- WRITE code readable by any skill level

## API-First Design
```go
// Define interfaces before implementation
type TaskService interface {
    CreateTask(task Task) error
    GetTask(id string) (Task, error)
    UpdateTask(id string, updates TaskUpdate) error
    DeleteTask(id string) error
}
```

## File Size Limits (ENFORCED)
- **Maximum 500 lines per file**
- **Refactor at 300+ lines**
- **Break monolithic files into modules**

## Error Handling Pattern
```go
func doSomething() error {
    if err := validate(); err != nil {
        return fmt.Errorf("validation failed: %w", err)
    }
    return nil
}
```

## Security Standards (MANDATORY)

### Input Validation (ALWAYS REQUIRED)
```go
// Create centralized validation utilities
package validation

import (
    "errors"
    "strings"
    "unicode/utf8"
)

// ValidateText validates text input with security checks
func ValidateText(input string, minLen, maxLen int, fieldName string) error {
    // Length validation
    if len(input) < minLen || len(input) > maxLen {
        return fmt.Errorf("%s length must be between %d and %d characters", fieldName, minLen, maxLen)
    }
    
    // UTF-8 validation
    if !utf8.ValidString(input) {
        return errors.New("invalid UTF-8 encoding")
    }
    
    // XSS prevention
    dangerous := []string{"<script>", "</script>", "javascript:", "onclick=", "onerror="}
    for _, pattern := range dangerous {
        if strings.Contains(strings.ToLower(input), pattern) {
            return errors.New("potentially malicious content detected")
        }
    }
    
    // Path traversal prevention
    if strings.Contains(input, "..") || strings.Contains(input, "/etc/") {
        return errors.New("path traversal attempt detected")
    }
    
    return nil
}

// ValidateID validates identifier strings
func ValidateID(id string) error {
    if len(id) == 0 || len(id) > 50 {
        return errors.New("invalid ID length")
    }
    
    // Only allow alphanumeric and hyphens
    for _, char := range id {
        if !((char >= 'a' && char <= 'z') || (char >= 'A' && char <= 'Z') || 
             (char >= '0' && char <= '9') || char == '-') {
            return errors.New("ID contains invalid characters")
        }
    }
    
    return nil
}

// Usage in application code - ALWAYS use validation utilities
func CreateTask(title, description string) error {
    // Validate all inputs using centralized functions
    if err := validation.ValidateText(title, 1, 255, "title"); err != nil {
        return fmt.Errorf("invalid title: %w", err)
    }
    
    if err := validation.ValidateText(description, 0, 2000, "description"); err != nil {
        return fmt.Errorf("invalid description: %w", err)
    }
    
    // Proceed with business logic
    return saveTask(title, description)
}

func GetTaskByID(taskID string) (Task, error) {
    // Validate ID format
    if err := validation.ValidateID(taskID); err != nil {
        return Task{}, fmt.Errorf("invalid task ID: %w", err)
    }
    
    // Proceed with database query
    return fetchTask(taskID)
}
```

### SQL Injection Prevention (MANDATORY)
```go
// ALWAYS use parameterized queries
func GetUserByID(db *sql.DB, userID string) (User, error) {
    // ✅ CORRECT - Parameterized query
    query := "SELECT name, email FROM users WHERE id = ?"
    row := db.QueryRow(query, userID)
    
    // ❌ NEVER DO THIS - String concatenation
    // query := "SELECT * FROM users WHERE id = '" + userID + "'"
    
    var user User
    err := row.Scan(&user.Name, &user.Email)
    return user, err
}
```

### Authentication & Authorization
```go
// ALWAYS verify permissions before operations
func DeleteTask(userID, taskID string) error {
    // Verify user owns the task
    task, err := GetTask(taskID)
    if err != nil {
        return err
    }
    
    if task.OwnerID != userID {
        return errors.New("unauthorized: user does not own this task")
    }
    
    return performDelete(taskID)
}
```

### File Path Security
```go
// ALWAYS sanitize file paths
func SaveFile(filename string, content []byte) error {
    // Clean and validate path
    cleanPath := filepath.Clean(filename)
    
    // Prevent directory traversal
    if strings.Contains(cleanPath, "..") {
        return errors.New("invalid file path")
    }
    
    // Restrict to allowed directory
    allowedDir := "/app/uploads"
    fullPath := filepath.Join(allowedDir, cleanPath)
    
    if !strings.HasPrefix(fullPath, allowedDir) {
        return errors.New("path outside allowed directory")
    }
    
    return os.WriteFile(fullPath, content, 0644)
}
```

### Environment Variable Security
```go
// NEVER hardcode secrets in code
func GetDatabaseURL() string {
    // ✅ CORRECT - Read from environment
    dbURL := os.Getenv("DATABASE_URL")
    if dbURL == "" {
        log.Fatal("DATABASE_URL environment variable required")
    }
    return dbURL
    
    // ❌ NEVER DO THIS - Hardcoded secrets
    // return "postgres://user:password123@localhost/db"
}
```

### HTTP Security Headers
```go
// ALWAYS set security headers
func SetSecurityHeaders(w http.ResponseWriter) {
    w.Header().Set("X-Content-Type-Options", "nosniff")
    w.Header().Set("X-Frame-Options", "DENY")
    w.Header().Set("X-XSS-Protection", "1; mode=block")
    w.Header().Set("Content-Security-Policy", "default-src 'self'")
}
```

### Error Handling Security
```go
// NEVER expose internal details in errors
func LoginUser(email, password string) error {
    user, err := getUserByEmail(email)
    if err != nil {
        // ✅ CORRECT - Generic error message
        return errors.New("invalid credentials")
        
        // ❌ NEVER DO THIS - Exposes system details
        // return fmt.Errorf("user not found in database: %v", err)
    }
    
    if !validatePassword(password, user.HashedPassword) {
        // ✅ CORRECT - Same generic message
        return errors.New("invalid credentials")
    }
    
    return nil
}
```

## Security Checklist (ENFORCE BEFORE COMMIT)
- [ ] All user inputs validated and sanitized
- [ ] No SQL injection vulnerabilities (parameterized queries only)
- [ ] No path traversal vulnerabilities  
- [ ] No hardcoded secrets or credentials
- [ ] Proper error handling (no information leakage)
- [ ] Authentication/authorization checks in place
- [ ] Security headers set for HTTP responses
- [ ] Input length limits enforced
- [ ] File upload restrictions implemented
