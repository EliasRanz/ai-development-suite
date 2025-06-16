# Architecture Instructions for AI Agents

## Technology Stack
- **Backend**: Go/Wails with React TypeScript frontend
- **Architecture**: Clean Architecture pattern
- **Target**: 4x performance improvement over Python implementation

## Layer Structure (MANDATORY)
```
Frontend (React/TS) 
    ↓
Application Layer (Use cases, services)
    ↓  
Domain Layer (Business logic, entities)
    ↓
Infrastructure Layer (Database, external APIs)
```

## Implementation Rules
1. **Desktop application** - Cross-platform desktop application using Wails
2. **Model-agnostic design** - Common interfaces for different AI model types
3. **Feature flags** - Use for work-in-progress functionality
4. **Clean separation** - Each layer has single responsibility

## AI Agent Guidelines
- FOLLOW Clean Architecture patterns strictly
- CREATE adapters for new AI model types
- USE interfaces for extensibility between different models
- IMPLEMENT feature flags for experimental features
- DESIGN for cross-platform desktop deployment
