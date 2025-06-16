# AI Tools Development Environment
# Automation for AI Studio, Project Management, and other tools

.PHONY: help dev build test clean setup

# Default target
help: ## Show this help message
	@echo "AI Tools Development Environment"
	@echo "================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# AI Studio Development (Wails + React)
setup: ## Set up development environment (WSL recommended)
	@echo "Setting up development environment..."
	@chmod +x scripts/wsl/setup-dev.sh
	@./scripts/wsl/setup-dev.sh

dev: ## Start AI Studio development server with hot reload
	@echo "Starting AI Studio development server..."
	wails dev

build: ## Build AI Studio production binary
	@echo "Building AI Studio production binary..."
	wails build -clean

build-windows: ## Build AI Studio Windows executable (from WSL)
	@echo "Building Windows executable..."
	wails build -platform windows/amd64 -clean

build-all: ## Build AI Studio for all platforms
	@echo "Building for all platforms..."
	wails build -platform windows/amd64,linux/amd64,darwin/amd64 -clean

# Testing
test: test-go test-frontend ## Run all tests
	@echo "All tests completed"

test-go: ## Run Go backend tests
	@echo "Running Go tests..."
	go test -race -coverprofile=coverage.out ./...
	go tool cover -func=coverage.out

test-frontend: ## Run React frontend tests
	@echo "Running frontend tests..."
	cd ai-studio/frontend && npm test -- --coverage --watchAll=false

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	go test -tags=integration ./tests/integration/...

# Code Quality
lint: ## Run all linters
	@echo "Running linters..."
	golangci-lint run
	cd ai-studio/frontend && npm run lint

fmt: ## Format code
	@echo "Formatting code..."
	go fmt ./...
	cd ai-studio/frontend && npm run format

coverage: ## Generate coverage report
	@echo "Generating coverage report..."
	go tool cover -html=coverage.out -o coverage.html
	cd ai-studio/frontend && npm run coverage:report
	@echo "Coverage report generated: coverage.html"

# Dependencies
deps: ## Install/update dependencies
	@echo "Installing dependencies..."
	go mod download
	go mod tidy
	cd ai-studio/frontend && npm install

deps-update: ## Update all dependencies
	@echo "Updating dependencies..."
	go get -u ./...
	go mod tidy
	cd ai-studio/frontend && npm update

# Cleaning
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf ai-studio/build/
	rm -rf ai-studio/frontend/dist/
	rm -rf ai-studio/frontend/node_modules/.cache/
	rm -f coverage.out coverage.html

clean-all: clean ## Clean everything including dependencies
	@echo "Cleaning dependencies..."
	rm -rf ai-studio/frontend/node_modules/
	go clean -modcache

# Security
security-audit: ## Run security audit
	@echo "Running security audit..."
	cd ai-studio && go list -json -m all | nancy sleuth
	cd ai-studio/frontend && npm audit

security-validate: ## Validate WSL permissions and security
	@echo "Validating security setup..."
	@chmod +x scripts/security/validate-permissions.sh
	@./scripts/security/validate-permissions.sh

# Environment validation
check-env: ## Check development environment
	@echo "Checking development environment..."
	@command -v go >/dev/null 2>&1 || { echo "Go is not installed"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "Node.js is not installed"; exit 1; }
	@command -v wails >/dev/null 2>&1 || { echo "Wails is not installed"; exit 1; }
	@echo "✅ Environment looks good!"

version: ## Show version information
	@echo "AI Tools Development Environment"
	@echo "Go version: $$(go version)"
	@echo "Node version: $$(node --version)"
	@echo "Wails version: $$(wails version 2>/dev/null || echo 'Not installed')"


# AI Project Manager Commands
# Automatically selects development or production profile based on AI_PM_MODE environment variable
# Set AI_PM_MODE=dev for Project Management tool development (hot reload)
# Set AI_PM_MODE=prod (or leave unset) for all other work (stable)

AI_PM_MODE ?= prod
AI_PM_PROFILE := $(if $(filter dev,$(AI_PM_MODE)),development,production)
AI_PM_PORT_INFO := $(if $(filter dev,$(AI_PM_MODE)),Frontend: http://localhost:3002 (hot reload) | API: http://localhost:8001 (hot reload),Frontend: http://localhost:3000 | API: http://localhost:8000)

ai-pm-start: ## Start AI Project Manager services (auto-selects profile based on AI_PM_MODE)
	@echo "Starting AI Project Manager in $(AI_PM_PROFILE) mode..."
	@cd ai-pm && docker compose --profile $(AI_PM_PROFILE) up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✅ Services started: $(AI_PM_PORT_INFO)"

ai-pm-stop: ## Stop AI Project Manager services
	@echo "Stopping AI Project Manager services..."
	@cd ai-pm && docker compose down

ai-pm-restart: ## Restart AI Project Manager services
	@echo "Restarting AI Project Manager services..."
	@cd ai-pm && docker compose down
	@cd ai-pm && docker compose --profile $(AI_PM_PROFILE) up -d
	@echo "✅ Services restarted: $(AI_PM_PORT_INFO)"

ai-pm-status: ## Check AI Project Manager service status
	@echo "AI Project Manager Status ($(AI_PM_PROFILE) mode)"
	@echo "============================================================================"
	@cd ai-pm && { \
		echo "CONTAINER NAME	STATUS	PORTS"; \
		for service in $$(docker compose --profile $(AI_PM_PROFILE) config --services); do \
			docker compose ps $$service --format "{{.Name}}	{{.Status}}	{{.Ports}}" 2>/dev/null; \
		done; \
	} | column -t -s '	'

ai-pm-logs: ## Show AI Project Manager logs
	@cd ai-pm && docker compose logs -f

ai-pm-cli: ## Open AI Project Manager CLI
	@echo "Opening AI Project Manager CLI..."
	@./scripts/project-manager.sh

# Quick start for new developers
quick-start: check-env deps test ## Quick start for new developers
	@echo ""
	@echo "🎉 Setup complete! Next steps:"
	@echo "  AI Studio Development:"
	@echo "    make dev          # Start AI Studio development server"
	@echo "    make build        # Build AI Studio for production"
	@echo ""
	@echo "  Project Management:"
	@echo "    make ai-pm-start  # Start project management system"
	@echo "    make ai-pm-cli    # Use project management CLI"
	@echo ""
