# ADR 009: Development-Only Project Management Tool

**Status:** Accepted  
**Date:** 2025-06-13  
**Deciders:** AI Development Team  
**Supersedes:** ADR 008 (Architecture Simplification)

## Context

Through discussion, we realized a key distinction: **the project management system is a development tool, not a product feature**. The AI tools launcher we're building is for managing and launching AI tools, not for project management.

## Key Insight

**Separation of Concerns:**
- **Project Management**: Tool for developing the AI tools launcher
- **AI Tools Launcher**: Product for managing and launching AI tools
- **These are completely different domains**

## Decision

Create a **standalone, development-only project management service** that:

1. **Development Tool Only**: Not included in production AI tools launcher
2. **Always Available**: Runs independently during development
3. **Simple Deployment**: Docker services for development environment
4. **No Integration Needed**: Completely separate from main application

## Architecture

### Development Environment
```
Development Infrastructure (Always Running)
├── PostgreSQL (project data)
├── Redis (caching) 
├── MinIO (file storage)
└── AI-PM Service (Go web server)
    ├── REST API (:8000)
    ├── Web UI (:3000)
    └── CLI scripts

AI Tools Launcher (Development - Frequently Restarted)
└── Wails App (separate application entirely)
```

### Production Deployment
```
AI Tools Launcher (Single Binary)
└── Wails App for AI tool management
    (No project management - that was just for development)
```

## Implementation

### Development Services (Docker)
- **PostgreSQL**: Project data persistence
- **Redis**: Caching layer
- **MinIO**: File storage
- **Go Service**: Simple web server with API and basic UI
- **CLI Tools**: For AI agent interaction

### Main Application (Wails)
- **Independent**: No project management code
- **Focused**: Pure AI tools launcher functionality
- **Clean**: No development-only features

## Benefits

### ✅ **Perfect Separation**
- Development tools stay in development
- Product focuses on core functionality
- Clean architecture boundaries

### ✅ **Development Workflow**
- Project management always available
- Main app can restart frequently
- No interference between tools

### ✅ **Simplified Production**
- No unnecessary project management features in product
- Smaller binary size
- Focused user experience

### ✅ **Tech Stack Clarity**
- Development tools can use different stack if needed
- Main product maintains clean Go + React architecture
- No confusion about what's product vs. tooling

## Migration Path

1. **Immediate**: Keep current infrastructure and CLI tools
2. **Development**: Create simple Go web service for UI access
3. **Production**: Build AI tools launcher without any project management
4. **Long-term**: Development tooling evolves independently of product

## Related ADRs

- **ADR 007**: Established infrastructure and CLI tools
- **ADR 008**: Explored integration approaches (now superseded)
- **Future ADRs**: Will focus on AI tools launcher features, not project management

## Summary

This decision dramatically simplifies our architecture by recognizing that project management is a development concern, not a product feature. The AI tools launcher can focus purely on its core mission: making AI tools accessible and manageable.
