# Development Guidelines for AI Agents

## Platform Requirements
- **Environment**: WSL development recommended for performance
- **Requirements**: Go 1.21+, Node.js 18+, Wails v2

## Development Commands
**Note**: Service management commands are in `project-management.md`

```bash
# Testing & Building
make test               # Run all tests
make build             # Build production
make build-windows      # Build Windows executable from WSL
```

## Monorepo Structure (FOLLOW STRICTLY)
```
ai-tools/                    # Root monorepo
├── ai-studio/              # Desktop application (Wails + React)
│   ├── backend/           # Go backend with Clean Architecture
│   ├── frontend/          # React TypeScript UI
│   └── main.go           # Wails entry point
├── ai-pm/                 # Project management system
│   ├── backend/          # Go backend with PostgreSQL
│   ├── frontend/         # React TypeScript UI
│   └── scripts/          # Setup and management scripts
├── scripts/              # Global utility scripts
├── .github/instructions/ # AI agent instructions
├── ADRs/                # Architecture Decision Records
├── shared/              # Common utilities and docs
└── tests/               # Global test suites
```

## Code Organization (ENFORCED)

### File Size Limits (IMMEDIATE ACTION REQUIRED)
- **MAXIMUM 500 lines per file**
- **REFACTOR at 300+ lines**  
- **BREAK UP monolithic files**

### Refactoring Triggers
- **File > 300 lines**: Plan refactoring
- **File > 500 lines**: Immediate refactoring required
- **Function > 50 lines**: Consider breaking down
- **Duplicate code**: Extract to shared functions

### Go Service Structure Template
```
service/
├── main.go              # Entry point (<50 lines)
├── config/
│   └── config.go        # Configuration and environment
├── models/
│   ├── project.go       # Project struct and methods
│   ├── task.go         # Task struct and methods
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

### Best Practices
- **Single Responsibility**: Each file/package has one clear purpose
- **Consistent Naming**: Use Go conventions (PascalCase for exports)
- **Error Handling**: Always handle errors explicitly
- **Documentation**: Add comments for exported functions and types

## AI Agent Checklist
- [ ] Environment properly set up
- [ ] Project structure followed
- [ ] File size limits respected  
- [ ] Code organization standards met
- [ ] Tests written for new code
