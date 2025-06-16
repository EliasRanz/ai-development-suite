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
	@echo "Checking for conflicting environments..."
	@cd ai-pm && { \
		if [ "$(AI_PM_MODE)" = "dev" ]; then \
			RUNNING_PROD=$$(docker compose ps --services --filter "status=running" | grep -E "(ai-pm-api|ai-pm-ui)$$" | wc -l); \
			if [ $$RUNNING_PROD -gt 0 ]; then \
				echo "⚠️  Production environment is running. Stopping it to avoid conflicts..."; \
				docker compose stop ai-pm-api ai-pm-ui; \
				docker compose rm -f ai-pm-api ai-pm-ui; \
			fi; \
		else \
			RUNNING_DEV=$$(docker compose ps --services --filter "status=running" | grep -E "(ai-pm-api-dev|ai-pm-ui-dev)" | wc -l); \
			if [ $$RUNNING_DEV -gt 0 ]; then \
				echo "⚠️  Development environment is running. Stopping it to avoid conflicts..."; \
				docker compose stop ai-pm-api-dev ai-pm-ui-dev; \
				docker compose rm -f ai-pm-api-dev ai-pm-ui-dev; \
			fi; \
		fi; \
	}
	@cd ai-pm && docker compose --profile $(AI_PM_PROFILE) up -d
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✅ Services started: $(AI_PM_PORT_INFO)"

ai-pm-stop: ## Stop AI Project Manager services (stops both environments, preserves database)
	@echo "Stopping AI Project Manager services (preserving database)..."
	@cd ai-pm && docker compose stop ai-pm-api ai-pm-ui ai-pm-api-dev ai-pm-ui-dev
	@cd ai-pm && docker compose rm -f ai-pm-api ai-pm-ui ai-pm-api-dev ai-pm-ui-dev

ai-pm-stop-prod: ## Stop only production environment (preserves database)
	@echo "Stopping AI Project Manager production environment..."
	@cd ai-pm && docker compose stop ai-pm-api ai-pm-ui
	@cd ai-pm && docker compose rm -f ai-pm-api ai-pm-ui

ai-pm-stop-dev: ## Stop only development environment (preserves database)
	@echo "Stopping AI Project Manager development environment..."
	@cd ai-pm && docker compose stop ai-pm-api-dev ai-pm-ui-dev
	@cd ai-pm && docker compose rm -f ai-pm-api-dev ai-pm-ui-dev

ai-pm-stop-all: ## Stop ALL services including database (use with caution)
	@echo "⚠️  Stopping ALL AI Project Manager services INCLUDING DATABASE..."
	@cd ai-pm && docker compose --profile production --profile development down

ai-pm-restart: ## Restart AI Project Manager services (current mode only, preserves database)
	@echo "Restarting AI Project Manager services..."
	@cd ai-pm && { \
		if [ "$(AI_PM_MODE)" = "dev" ]; then \
			docker compose stop ai-pm-api-dev ai-pm-ui-dev; \
			docker compose rm -f ai-pm-api-dev ai-pm-ui-dev; \
		else \
			docker compose stop ai-pm-api ai-pm-ui; \
			docker compose rm -f ai-pm-api ai-pm-ui; \
		fi; \
	}
	@cd ai-pm && docker compose --profile $(AI_PM_PROFILE) up -d
	@echo "✅ Services restarted: $(AI_PM_PORT_INFO)"

ai-pm-switch: ## Switch between development and production modes cleanly (preserves database)
	@echo "Switching AI Project Manager from $(AI_PM_PROFILE) mode..."
	@cd ai-pm && { \
		if [ "$(AI_PM_MODE)" = "dev" ]; then \
			echo "Switching from production to development mode..."; \
			docker compose stop ai-pm-api ai-pm-ui; \
			docker compose rm -f ai-pm-api ai-pm-ui; \
			docker compose --profile development up -d; \
		else \
			echo "Switching from development to production mode..."; \
			docker compose stop ai-pm-api-dev ai-pm-ui-dev; \
			docker compose rm -f ai-pm-api-dev ai-pm-ui-dev; \
			docker compose --profile production up -d; \
		fi; \
	}
	@echo "Waiting for services to be ready..."
	@sleep 5
	@echo "✅ Services switched to $(AI_PM_PROFILE) mode: $(AI_PM_PORT_INFO)"

ai-pm-status: ## Check AI Project Manager service status
	@echo "AI Project Manager Status"
	@echo "============================================================================"
	@cd ai-pm && { \
		PROD_RUNNING=$$(docker compose ps --services --filter "status=running" | grep -E "(ai-pm-api|ai-pm-ui)$$" | wc -l); \
		DEV_RUNNING=$$(docker compose ps --services --filter "status=running" | grep -E "(ai-pm-api-dev|ai-pm-ui-dev)" | wc -l); \
		DB_RUNNING=$$(docker compose ps --services --filter "status=running" | grep "ai-pm-database" | wc -l); \
		echo "Database: $$([ $$DB_RUNNING -gt 0 ] && echo "✅ Running" || echo "❌ Stopped")"; \
		echo "Production (ports 8000/3000): $$([ $$PROD_RUNNING -gt 0 ] && echo "✅ Running" || echo "❌ Stopped")"; \
		echo "Development (ports 8001/3002): $$([ $$DEV_RUNNING -gt 0 ] && echo "✅ Running" || echo "❌ Stopped")"; \
		echo ""; \
		if [ $$PROD_RUNNING -gt 0 ] && [ $$DEV_RUNNING -gt 0 ]; then \
			echo "⚠️  Both environments are running simultaneously"; \
		elif [ $$PROD_RUNNING -gt 0 ]; then \
			echo "🏭 Production environment active"; \
		elif [ $$DEV_RUNNING -gt 0 ]; then \
			echo "🔧 Development environment active"; \
		else \
			echo "💤 No API/UI services running"; \
		fi; \
		echo ""; \
		echo "CONTAINER NAME        STATUS         PORTS"; \
		docker compose ps --format "{{.Name}}	{{.Status}}	{{.Ports}}" 2>/dev/null; \
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
