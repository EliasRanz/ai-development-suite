# Development Guidelines

## Environment Setup
WSL development - `777` permissions normal due to DRVFS, work in ~/Development/ for performance.

Commands: `make dev`, `make test`, `make build`, `make plane-setup`.

Requirements: Go 1.21+, Node.js 18+, Wails v2.

## Project Structure
- `cmd/app/` - application entry points
- `internal/` - Go backend (Clean Architecture layers)
- `frontend/` - React TypeScript
- `tests/` - test suites
- `.github/instructions/` - AI context
- `ADRs/` - Architecture Decision Records
- `scripts/plane-api.sh` - AI agent interface to project management
- `pm-service/` - Development-only project management API

## Code Organization Standards

### File Size Limits
- **Single files should not exceed 500 lines**
- **When a file approaches 300+ lines, consider refactoring**
- **Break up monolithic files into logical modules**

### Go Service Structure
For services like `pm-service/`, organize code into:
```
pm-service/
├── main.go              # Entry point (< 50 lines)
├── config/
│   └── config.go        # Configuration and environment
├── models/
│   ├── project.go       # Project struct and methods
│   ├── task.go          # Task struct and methods
│   └── types.go         # Common types and interfaces
├── handlers/
│   ├── projects.go      # Project HTTP handlers
│   ├── tasks.go         # Task HTTP handlers
│   └── dashboard.go     # Dashboard handlers
├── database/
│   ├── connection.go    # Database connection setup
│   ├── migrations.go    # Schema initialization
│   └── queries.go       # Common queries
└── utils/
    └── response.go      # HTTP response helpers
```

### Refactoring Triggers
- **File > 300 lines**: Plan refactoring
- **File > 500 lines**: Immediate refactoring required
- **Function > 50 lines**: Consider breaking down
- **Duplicate code**: Extract to shared functions

### Best Practices
- **Single Responsibility**: Each file/package has one clear purpose
- **Consistent Naming**: Use Go conventions (PascalCase for exports)
- **Error Handling**: Always handle errors explicitly
- **Documentation**: Add comments for exported functions and types

## Migration Notes
Python→Go migration targeting 4x performance improvement.

## Database Management Guidelines

### Current State
- **Issue**: Raw SQL queries scattered throughout `main.go`
- **Problems**: No type safety, manual query building, difficult migrations
- **Goal**: Migrate to proper database abstraction layer

### Recommended Go Database Libraries

#### GORM (Recommended for this project)
```go
// Example: Clean, type-safe queries
db.Where("deleted_at IS NULL").Find(&projects)
db.Model(&task).Where("id = ?", taskID).Updates(updates)
```
**Pros**: Auto-migrations, built-in soft deletes, associations, good docs
**Use when**: Rapid development, complex relationships needed

#### Squirrel (Alternative)
```go
// Example: SQL builder approach
query := squirrel.Select("*").From("tasks").Where("deleted_at IS NULL")
```
**Pros**: Lightweight, SQL-like, no magic
**Use when**: Want more control over SQL generation

#### Selection Criteria
- **GORM**: Complex models, rapid development, built-in features
- **Squirrel**: Simple models, performance critical, minimal dependencies
- **Raw SQL**: Only for very specific optimization cases

### Migration Strategy
1. **Keep existing endpoints working** during migration
2. **Migrate one model at a time** (Project → Task → Notes)
3. **Add database tests** before and after migration
4. **Use database transactions** for data consistency
