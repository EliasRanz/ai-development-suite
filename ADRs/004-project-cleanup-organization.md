# ADR-004: Project Cleanup and Organization Strategy

**Status**: Accepted  
**Date**: 2025-06-12  
**Deciders**: Development Team  

## Context

The current repository contains legacy Python implementation, build artifacts, test files mixed with source code, and various experimental files that should be cleaned up for production-ready Wails implementation.

### Current Issues:
- **Mixed Test Files**: Tests scattered throughout source directories
- **Legacy Code**: Python implementation no longer needed
- **Build Artifacts**: Compiled files committed to repository
- **Experimental Files**: Multiple analysis and implementation plan files
- **Unclear Structure**: Hard to distinguish production vs development files

### Requirements:
- **Clean Production Code**: Only ship necessary files in final binary
- **Separated Concerns**: Tests, docs, and source code in dedicated directories
- **Minimal Dependencies**: Separate runtime from development dependencies
- **Easy Navigation**: Clear project structure for developers and AI agents
- **Fast Builds**: No unnecessary files slowing down compilation

## Decision

**Implement clean project structure with separated concerns and minimal production footprint**

### Target Project Structure:

```
comfyui-launcher-wails/          # New clean repository
├── cmd/                         # Application entry points
│   └── app/
│       └── main.go             # Main application entry
├── internal/                    # Private application code
│   ├── app/                    # Application layer (orchestration)
│   │   ├── handlers/           # Wails API handlers
│   │   └── services/           # Application services
│   ├── domain/                 # Domain layer (business logic)
│   │   ├── server/             # Server management domain
│   │   ├── config/             # Configuration domain
│   │   └── events/             # Event system domain
│   ├── infrastructure/         # Infrastructure layer
│   │   ├── filesystem/         # File operations
│   │   ├── process/            # Process management
│   │   └── logging/            # Logging implementation
│   └── interfaces/             # Interface adapters
│       ├── wails/              # Wails-specific adapters
│       └── cli/                # CLI interface (future)
├── pkg/                        # Public packages (if needed)
├── frontend/                   # React application
│   ├── src/                   # Production source code
│   │   ├── components/        # Reusable UI components
│   │   ├── pages/             # Page components
│   │   ├── hooks/             # Custom React hooks
│   │   ├── services/          # API services
│   │   ├── types/             # TypeScript type definitions
│   │   └── utils/             # Utility functions
│   ├── public/                # Static assets
│   ├── package.json           # Dependencies (dev deps separated)
│   └── vite.config.ts         # Build configuration
├── tests/                     # All tests (separate from production)
│   ├── unit/                  # Unit tests mirroring internal/ structure
│   ├── integration/           # Integration tests
│   ├── e2e/                   # End-to-end Playwright tests
│   ├── fixtures/              # Test data and mocks
│   └── utils/                 # Test utilities and helpers
├── docs/                      # Documentation
│   ├── development/           # Development guides
│   ├── deployment/            # Deployment guides
│   └── api/                   # API documentation
├── scripts/                   # Build and utility scripts
│   ├── build/                 # Build scripts
│   ├── dev/                   # Development scripts
│   └── deploy/                # Deployment scripts
├── configs/                   # Configuration files
├── assets/                    # Application assets (icons, etc.)
├── ADRs/                      # Architecture Decision Records
├── go.mod                     # Go dependencies
├── go.sum                     # Go dependency checksums
├── wails.json                 # Wails configuration
├── Makefile                   # Build automation
└── README.md                  # Project documentation
```

### Files to Remove from Current Repository:

#### Legacy Python Implementation:
```bash
# Remove entire Python codebase
rm -rf comfy_launcher/
rm -rf tests/test_*.py
rm -rf tests/__pycache__/
rm -f requirements.txt requirements.in
rm -f concept_web_server.py
```

#### Build Artifacts:
```bash
# Remove all build artifacts
rm -rf build/
rm -rf web-ui/dist/
rm -rf comfy_launcher/web_dist/
rm -rf **/__pycache__/
rm -rf **/*.pyc
```

#### Experimental/Analysis Files:
```bash
# Keep as reference but move to docs/archive/
mkdir -p docs/archive/analysis/
mv ELECTRON_OPTION.md docs/archive/analysis/
mv LIGHTWEIGHT_ANALYSIS.md docs/archive/analysis/
mv MULTI_FRONTEND_PLAN.md docs/archive/analysis/
mv TAURI_MIGRATION_PLAN.md docs/archive/analysis/
mv WAILS_OPTION.md docs/archive/analysis/
mv PERFORMANCE_ROADMAP.md docs/archive/analysis/
mv EXTREME_PERFORMANCE_ADDONS.md docs/archive/analysis/
mv ULTRA_PERFORMANCE_WAILS.md docs/archive/analysis/
mv WAILS_IMPLEMENTATION.md docs/archive/analysis/
mv WAILS_TRAY_OVERLAY_FEATURES.md docs/archive/analysis/
mv PRODUCTION_IMPLEMENTATION_PLAN.md docs/archive/analysis/
mv REACT_MIGRATION.md docs/archive/analysis/
```

#### Development Files:
```bash
# Remove Windows-specific scripts (will recreate cross-platform versions)
rm -f *.bat *.ps1
rm -f start_comfyui.bat
```

### Build Configuration for Clean Artifacts:

#### .gitignore (Enhanced):
```gitignore
# Build artifacts
/build/
/dist/
*.exe
*.app
*.dmg
*.deb
*.rpm

# Development artifacts
coverage.out
coverage.html
*.test
*.prof

# Frontend artifacts
node_modules/
frontend/dist/
frontend/build/

# IDE and editor files
.vscode/
.idea/
*.swp
*.swo
*~

# OS-specific files
.DS_Store
Thumbs.db

# Logs
*.log
logs/

# Temporary files
*.tmp
*.temp
```

#### Frontend package.json (Clean Dependencies):
```json
{
  "name": "comfyui-launcher-frontend",
  "version": "1.0.0",
  "type": "module",
  "dependencies": {
    "react": "^18.3.1",
    "react-dom": "^18.3.1",
    "lucide-react": "^0.263.1"
  },
  "devDependencies": {
    "@types/react": "^18.3.3",
    "@types/react-dom": "^18.3.0",
    "@typescript-eslint/eslint-plugin": "^6.14.0",
    "@typescript-eslint/parser": "^6.14.0",
    "@vitejs/plugin-react": "^4.2.1",
    "eslint": "^8.55.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.4.5",
    "typescript": "^5.2.2",
    "vite": "^5.0.8",
    "@testing-library/react": "^13.4.0",
    "@testing-library/jest-dom": "^6.1.4",
    "@playwright/test": "^1.40.0",
    "jest": "^29.7.0",
    "jsdom": "^23.0.1",
    "vitest": "^1.0.0"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "test:e2e": "playwright test",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0"
  }
}
```

#### Wails Configuration (Clean Build):
```json
{
  "$schema": "https://wails.io/schemas/config.v2.json",
  "name": "ComfyUI Launcher",
  "outputfilename": "comfyui-launcher",
  "frontend": {
    "dir": "./frontend",
    "install": "npm install",
    "build": "npm run build",
    "dev": "npm run dev",
    "package": {
      "exclude": [
        "tests",
        "coverage",
        "node_modules/.cache",
        "*.test.ts",
        "*.spec.ts"
      ]
    }
  },
  "backend": {
    "go": {
      "tags": ["production"],
      "ldflags": [
        "-s",
        "-w"
      ]
    }
  },
  "build": {
    "dir": "./build",
    "clean": true,
    "excludes": [
      "tests/",
      "docs/",
      "scripts/",
      "*.md",
      ".git/",
      "coverage.*"
    ]
  }
}
```

### Production Build Process:

#### Makefile (Clean Builds):
```makefile
.PHONY: clean build test lint

# Clean all build artifacts
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf frontend/dist/
	rm -rf coverage.*
	go clean -cache -testcache -modcache

# Production build (minimal binary)
build-prod:
	@echo "🏗️ Building production binary..."
	wails build -clean -s -trimpath

# Development build
build-dev:
	@echo "🔧 Building development binary..."
	wails build

# Test (separate from production)
test:
	@echo "🧪 Running tests..."
	go test ./tests/... -v
	cd frontend && npm test

# Lint code
lint:
	@echo "🔍 Linting code..."
	golangci-lint run
	cd frontend && npm run lint

# Package for distribution
package: clean test lint build-prod
	@echo "📦 Creating distribution package..."
	./scripts/package.sh
```

### Migration Script:

```bash
#!/bin/bash
# scripts/migrate-to-clean-structure.sh

set -e

echo "🚀 Migrating to clean project structure..."

# Create new directory structure
mkdir -p {cmd/app,internal/{app/{handlers,services},domain/{server,config,events},infrastructure/{filesystem,process,logging},interfaces/{wails,cli}}}
mkdir -p {tests/{unit,integration,e2e,fixtures,utils},docs/{development,deployment,api},scripts/{build,dev,deploy}}
mkdir -p {frontend/src/{components,pages,hooks,services,types,utils},frontend/public}
mkdir -p {configs,assets,ADRs}

# Archive analysis files
mkdir -p docs/archive/analysis
mv *.md docs/archive/analysis/ 2>/dev/null || true
mv ADRs/*.md ./ADRs/ 2>/dev/null || true

# Remove legacy files
echo "🗑️ Removing legacy Python implementation..."
rm -rf comfy_launcher/ || true
rm -rf build/ || true
rm -f requirements.* || true
rm -f *.bat *.ps1 || true
rm -f concept_web_server.py || true

# Create initial Go files
cat > cmd/app/main.go << 'EOF'
package main

import (
    "context"
    "log"

    "github.com/wailsapp/wails/v2"
    "github.com/wailsapp/wails/v2/pkg/options"
)

func main() {
    app := NewApp()

    err := wails.Run(&options.App{
        Title:  "ComfyUI Launcher",
        Width:  1024,
        Height: 768,
        AssetServer: &assetserver.Options{
            Assets: assets,
        },
        OnStartup:        app.startup,
        OnDomReady:       app.domReady,
        OnBeforeClose:    app.beforeClose,
        OnShutdown:       app.shutdown,
    })

    if err != nil {
        log.Fatalf("Error running application: %v", err)
    }
}
EOF

echo "✅ Clean project structure created successfully!"
echo "📝 Next steps:"
echo "   1. Initialize Go module: go mod init comfyui-launcher"
echo "   2. Install Wails: go install github.com/wailsapp/wails/v2/cmd/wails@latest"
echo "   3. Initialize frontend: cd frontend && npm init"
echo "   4. Run: make build-dev"
```

## Benefits

### Development Benefits:
- ✅ **Clear Structure**: Easy to navigate and understand
- ✅ **Fast Builds**: No unnecessary files processed
- ✅ **Clean Tests**: All tests separate from production code
- ✅ **Minimal Dependencies**: Only ship what's needed

### Production Benefits:
- ✅ **Small Binary**: Only necessary code included
- ✅ **Fast Startup**: No test code loaded
- ✅ **Security**: No development tools in production
- ✅ **Clean Distribution**: Professional package structure

### Maintenance Benefits:
- ✅ **Easy Refactoring**: Clear boundaries between layers
- ✅ **AI-Friendly**: Logical structure for AI assistance
- ✅ **Documentation**: Self-documenting project structure
- ✅ **Onboarding**: New developers can quickly understand layout

## Implementation Plan

### Phase 1: Repository Cleanup (1 day)
- [ ] Archive analysis files to docs/archive/
- [ ] Remove legacy Python implementation
- [ ] Remove build artifacts and temporary files
- [ ] Create clean .gitignore

### Phase 2: Structure Creation (1 day)
- [ ] Create new directory structure
- [ ] Set up Go module and basic structure
- [ ] Configure frontend with clean dependencies
- [ ] Create build scripts and Makefile

### Phase 3: Migration (2-3 days)
- [ ] Port essential functionality to new structure
- [ ] Set up testing framework in separate directory
- [ ] Configure CI/CD for clean builds
- [ ] Create documentation

### Phase 4: Validation (1 day)
- [ ] Verify build process works
- [ ] Test cross-platform compilation
- [ ] Validate binary size and startup time
- [ ] Ensure all tests pass

## Related ADRs

- **ADR-001**: Technology Stack Selection
- **ADR-002**: Project Structure Architecture  
- **ADR-003**: Testing Strategy and Quality

---

**This ADR establishes**: Clean project organization with separated concerns and minimal production footprint for professional, maintainable codebase.
