# ADR-002: Project Structure and Architecture Pattern

**Status**: Accepted  
**Date**: 2025-06-12  
**Deciders**: Development Team  

## Context

We need to establish a clear, maintainable project structure for the Wails-based ComfyUI Launcher that:

### Requirements:
- **AI Maintainability**: Clear separation of concerns for AI agents to understand
- **Extensibility**: Easy to add new features without breaking existing code
- **Testability**: Structure that supports comprehensive testing
- **SOLID Principles**: Proper dependency inversion, single responsibility
- **Industry Standards**: Follow Go and React best practices
- **Production Ready**: Support for logging, monitoring, configuration management

### Current Challenges:
- Python codebase has mixed concerns (GUI + business logic)
- Testing is difficult due to tight coupling
- Adding features requires touching multiple files
- No clear domain boundaries

## Decision

**Adopt Clean Architecture with Domain-Driven Design (DDD) principles**

### Architecture Layers:

```
┌─────────────────────────────────────────┐
│           Presentation Layer            │ ← React Frontend + Wails Handlers
├─────────────────────────────────────────┤
│           Application Layer             │ ← Use Cases, App Services
├─────────────────────────────────────────┤
│             Domain Layer                │ ← Business Logic, Entities
├─────────────────────────────────────────┤
│          Infrastructure Layer           │ ← External Dependencies
└─────────────────────────────────────────┘
```

### Directory Structure:
```
comfy-launcher-wails/
├── cmd/app/                    # Application entry point
├── internal/                   # Private application code
│   ├── app/                   # Application layer
│   ├── domain/                # Domain layer (business logic)
│   ├── infrastructure/        # Infrastructure layer
│   ├── interfaces/            # Interface adapters
│   └── shared/                # Shared utilities
├── frontend/                   # React frontend
├── test/                      # Test utilities and fixtures
├── docs/                      # Documentation
├── scripts/                   # Build and development scripts
└── configs/                   # Configuration files
```

## Rationale

### Why Clean Architecture:
1. **Independence**: Business logic independent of frameworks
2. **Testability**: Easy to test each layer in isolation
3. **Flexibility**: Can change UI or infrastructure without affecting business logic
4. **Maintainability**: Clear boundaries and responsibilities

### Why Domain-Driven Design:
1. **Clear Domains**: Server Management, UI Management, Logging
2. **Ubiquitous Language**: Consistent terminology across codebase
3. **Encapsulation**: Domain logic encapsulated within domain boundaries
4. **Evolution**: Domains can evolve independently

### Layer Responsibilities:

#### 1. Domain Layer (`internal/domain/`)
**Purpose**: Contains business logic and rules
```go
// Example: Server domain
package server

type Service interface {
    Start(ctx context.Context, config Config) error
    Stop(ctx context.Context) error
    GetStatus() Status
    IsHealthy() bool
}

type Manager struct {
    // Pure business logic, no external dependencies
}
```

#### 2. Application Layer (`internal/app/`)
**Purpose**: Orchestrates domain services, handles use cases
```go
// Example: Application service
package app

type ServerUseCase struct {
    serverService server.Service
    logger       logging.Service
    events       events.Emitter
}

func (uc *ServerUseCase) StartServer(ctx context.Context) error {
    // Orchestrate multiple domain services
}
```

#### 3. Infrastructure Layer (`internal/infrastructure/`)
**Purpose**: External dependencies, file system, processes
```go
// Example: Process infrastructure
package process

type Manager struct {
    // Implements domain interfaces using external tools
}

func (m *Manager) StartProcess(cmd string, args []string) (*Process, error) {
    // Actual process management using os/exec
}
```

#### 4. Interface Layer (`internal/interfaces/`)
**Purpose**: Wails handlers, event management
```go
// Example: Wails handlers
package handlers

type ServerHandler struct {
    serverUseCase app.ServerUseCase
}

// Wails-bound method
func (h *ServerHandler) StartServer(ctx context.Context) error {
    return h.serverUseCase.StartServer(ctx)
}
```

### Domain Organization:

#### Server Management Domain
```
internal/domain/server/
├── service.go      # Service interface
├── manager.go      # Business logic implementation
├── health.go       # Health checking logic
├── config.go       # Server configuration
└── types.go        # Domain types and enums
```

#### UI Management Domain
```
internal/domain/ui/
├── overlay.go      # Overlay management
├── tray.go         # System tray logic
├── window.go       # Window management
├── theme.go        # Theme detection
└── notifications.go # Notification logic
```

#### Logging Domain
```
internal/domain/logging/
├── service.go      # Logging service interface
├── manager.go      # Log management logic
├── rotation.go     # Log rotation logic
└── types.go        # Log levels, formats
```

## Alternatives Considered

### 1. Simple Layered Architecture
**Rejected**: Not flexible enough, tight coupling between layers

### 2. Microservices Architecture
**Rejected**: Overkill for desktop application, unnecessary complexity

### 3. Model-View-Controller (MVC)
**Rejected**: UI-centric pattern, doesn't fit Go backend well

### 4. Hexagonal Architecture
**Considered**: Similar benefits, but Clean Architecture more widely understood

## Implementation Guidelines

### Dependency Rules:
1. **Dependencies point inward**: Outer layers depend on inner layers, never vice versa
2. **Domain independence**: Domain layer has no external dependencies
3. **Interface segregation**: Small, focused interfaces
4. **Dependency injection**: Use interfaces for testability

### File Organization Rules:
1. **One domain per directory**: Clear boundaries
2. **Interfaces in domain**: Define contracts where they're used
3. **Implementation in infrastructure**: Concrete implementations in outer layers
4. **Shared utilities**: Common code in `shared/` package

### Testing Strategy:
```go
// Domain tests - pure unit tests
func TestServerManager_Start(t *testing.T) {
    manager := server.NewManager()
    // Test business logic only
}

// Application tests - integration tests with mocks
func TestServerUseCase_StartServer(t *testing.T) {
    mockServer := &mocks.ServerService{}
    useCase := app.NewServerUseCase(mockServer, ...)
    // Test orchestration logic
}

// Infrastructure tests - test external integrations
func TestProcessManager_StartProcess(t *testing.T) {
    manager := process.NewManager()
    // Test actual process management
}
```

## Benefits

### For Development:
- ✅ **Clear Responsibilities**: Each file has a single, clear purpose
- ✅ **Easy Testing**: Can test each layer independently
- ✅ **Safe Refactoring**: Changes in one layer don't break others
- ✅ **Parallel Development**: Teams can work on different layers

### For AI Maintenance:
- ✅ **Predictable Structure**: AI agents can easily locate relevant code
- ✅ **Clear Interfaces**: Well-defined contracts between components
- ✅ **Isolated Changes**: Modifications are localized to specific domains
- ✅ **Self-Documenting**: Structure explains the system's organization

### For Feature Addition:
- ✅ **Domain Extension**: Add new features within existing domains
- ✅ **New Domains**: Add completely new domains without affecting existing code
- ✅ **Interface Evolution**: Extend interfaces without breaking implementations
- ✅ **Independent Testing**: Test new features in isolation

## Consequences

### Positive:
- ✅ **Maintainability**: Clear structure makes code easy to understand and modify
- ✅ **Testability**: Each layer can be tested independently with appropriate mocks
- ✅ **Scalability**: Can easily add new features and domains
- ✅ **Quality**: Enforced separation prevents mixing of concerns

### Negative:
- ❌ **Initial Complexity**: More files and directories to manage
- ❌ **Learning Curve**: Team needs to understand Clean Architecture principles
- ❌ **Boilerplate**: More interfaces and abstraction layers

### Mitigation Strategies:
- 📚 **Documentation**: Comprehensive guides and examples
- 🎯 **Code Generation**: Templates for new domains and services
- 🔍 **Linting**: Automated checks for architecture compliance
- 📖 **Training**: Team education on Clean Architecture principles

## Validation Criteria

### Architecture Compliance:
- [ ] No circular dependencies between layers
- [ ] Domain layer has no external imports
- [ ] All external dependencies injected via interfaces
- [ ] Clear separation between business logic and infrastructure

### Code Quality:
- [ ] Each package has single responsibility
- [ ] Interfaces are small and focused
- [ ] High test coverage in each layer
- [ ] No code duplication across domains

### Maintainability:
- [ ] AI agents can easily locate functionality
- [ ] New features can be added without modifying existing code
- [ ] Changes are localized to appropriate layers
- [ ] Clear documentation for each domain

## References

- [Clean Architecture by Robert Martin](https://blog.cleancoder.com/uncle-bob/2012/08/13/the-clean-architecture.html)
- [Domain-Driven Design by Eric Evans](https://domainlanguage.com/ddd/)
- [Go Project Layout](https://github.com/golang-standards/project-layout)
- [SOLID Principles in Go](https://dave.cheney.net/2016/08/20/solid-go-design)

---

**This ADR supersedes**: None  
**Related ADRs**: ADR-001 (Technology Stack), ADR-003 (Testing Strategy)
