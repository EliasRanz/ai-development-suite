# ADR 008: Hybrid Project Management Architecture

**Status:** Accepted  
**Date:** 2025-06-13  
**Deciders:** AI Development Team  
**Supersedes:** ADR 007 (partial)

## Context

After successfully migrating from Plane to a custom AI Project Manager system, we identified a critical development workflow issue: during active development, the main Wails application needs frequent restarts, but project management should remain stable and always available for tracking development progress.

We need a solution that provides:
1. **Development Stability**: Project management always available during main app development
2. **Production Integration**: Unified experience in production builds
3. **Minimal Tech Stack**: Avoid unnecessary complexity

## Decision

**Implement a hybrid architecture with deployment flexibility:**

### Development Mode
- **Standalone PM Service**: Independent Go service for project management
- **Always Available**: Runs separately from main Wails app
- **Stable During Development**: Unaffected by main app restarts
- **API Interface**: RESTful API for development tools and AI agents

### Production Mode  
- **Integrated Option**: Project management can be embedded in main Wails app
- **OR Standalone Option**: Keep as separate service if preferred
- **Shared Infrastructure**: Both modes use same PostgreSQL/Redis/MinIO

### Architecture

**Backend (Go):**
- Domain models: `internal/domain/project.go`
- Interfaces: `internal/domain/project_interfaces.go`
- Repository: `internal/infrastructure/repository/postgresql_project_repository.go`
- Service layer: `internal/application/project_service.go`
- Wails interface: `internal/interfaces/project_manager_app.go`

**Frontend (React/TypeScript):**
- Project management components integrated into existing frontend
- Consistent UI/UX with main application
- Direct function calls to Go backend (no API overhead)

**Infrastructure:**
- PostgreSQL database (existing, working)
- Redis cache (existing, working)
- MinIO storage (existing, working)

## Rationale

### Advantages of Wails Integration

1. **Single Tech Stack**
   - Go + React/TypeScript (already established)
   - No additional Node.js dependency
   - Consistent development experience

2. **Unified Application**
   - Project management as core feature, not separate tool
   - Better user experience with integrated workflows
   - Shared state and context between features

3. **Better Performance**
   - Direct function calls instead of HTTP APIs
   - No network overhead for project management operations
   - Faster data access and updates

4. **Simplified Deployment**
   - Single binary for entire application
   - No container orchestration for application layer
   - Easier distribution and installation

5. **Platform Compatibility**
   - Avoids Docker platform issues we encountered
   - Wails handles cross-platform compilation
   - Better WSL2/Windows integration

6. **Development Efficiency**
   - Single codebase to maintain
   - Shared types and interfaces
   - Unified build and test processes

### Infrastructure Benefits

- **Keep What Works**: Retain solid PostgreSQL, Redis, MinIO infrastructure
- **Remove Problems**: Eliminate problematic API/Web containers
- **Maintain CLI**: Keep existing CLI tools for AI agent interaction

## Implementation Plan

### Phase 1: Backend Integration ✅
- [x] Create domain models and interfaces
- [x] Implement PostgreSQL repository
- [x] Create service layer
- [x] Build Wails application interface
- [x] Simplify Docker Compose to infrastructure only

### Phase 2: Frontend Integration (In Progress)
- [ ] Wire up Wails app in main.go
- [ ] Create React components for project management
- [ ] Integrate with existing UI framework
- [ ] Test functionality end-to-end

### Phase 3: Enhancement
- [ ] Add advanced features (filters, search, reporting)
- [ ] Implement real-time updates
- [ ] Add file attachments using MinIO
- [ ] Create dashboard and analytics

## Consequences

### ✅ **Strong Advantages for Our Use Case**
- **Unified Architecture**: Single, cohesive desktop application (exactly what we want!)
- **Better Performance**: No API overhead, direct function calls
- **Platform Reliability**: Avoids Docker/container compatibility issues in WSL2
- **Simplified Deployment**: One binary to distribute (perfect for desktop app)
- **Development Efficiency**: Single codebase and tech stack (Go + React)
- **Integrated User Experience**: Project management within main application context
- **AI Agent Friendly**: Single process for agents to interact with

### 🔧 **Implementation Considerations (Not Negatives)**
- **Component Wiring**: Need to connect services in main.go (standard Go practice)
- **Monolithic Design**: All features in one application (ideal for desktop apps)

### 🔄 **Maintained Benefits**
- **CLI Tools**: Keep existing scripts for AI agent automation
- **Infrastructure**: PostgreSQL, Redis, MinIO remain separate and reusable
- **Future Flexibility**: Can extract services later if needed (but unlikely)
- **API Option**: Can still expose HTTP endpoints if required

### 🎯 **Why This is Perfect for AI Tools Launcher**

This approach aligns ideally with our project goals:
1. **Desktop Application**: Monolithic structure is the standard for desktop apps
2. **Cross-Platform**: Wails provides excellent cross-platform support
3. **AI Integration**: Single binary is easier for AI agents to manage
4. **User Experience**: Integrated project management feels natural in a tool launcher
5. **Development Velocity**: No service boundaries means faster iteration

## Migration from ADR 007

This decision builds upon ADR 007 (AI Project Manager Migration) by:
- **Keeping**: Infrastructure components (PostgreSQL, Redis, MinIO)
- **Keeping**: Domain models and business logic
- **Changing**: Application layer from separate services to Wails integration
- **Improving**: Platform compatibility and performance

## Related ADRs

- ADR 001: Technology Stack Selection (Go/Wails chosen)
- ADR 002: Project Structure Architecture (clean architecture)
- ADR 007: AI Project Manager Migration (infrastructure foundation)

## Status

**Current Implementation:**
- ✅ Backend Go code complete
- ✅ Infrastructure running reliably
- 🔄 Frontend integration in progress
- 📋 Testing and refinement planned
