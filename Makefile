# ComfyUI Launcher - Wails Implementation
# Development automation

.PHONY: help dev build test clean install setup

# Default target
help: ## Show this help message
	@echo "ComfyUI Launcher - Development Commands"
	@echo "======================================"
	@grep -E '^[a-zA-Z_-]+:.*?## .*$$' $(MAKEFILE_LIST) | sort | awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m%-20s\033[0m %s\n", $$1, $$2}'

# Development
setup: ## Set up development environment (WSL recommended)
	@echo "Setting up development environment..."
	@chmod +x scripts/wsl/setup-dev.sh
	@./scripts/wsl/setup-dev.sh

dev: ## Start development server with hot reload
	@echo "Starting Wails development server..."
	wails dev

build: ## Build production binary
	@echo "Building production binary..."
	wails build -clean

build-windows: ## Build Windows executable (from WSL)
	@echo "Building Windows executable..."
	wails build -platform windows/amd64 -clean

build-all: ## Build for all platforms
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
	cd frontend && npm test -- --coverage --watchAll=false

test-e2e: ## Run end-to-end tests
	@echo "Running E2E tests..."
	cd frontend && npx playwright test

test-integration: ## Run integration tests
	@echo "Running integration tests..."
	go test -tags=integration ./tests/integration/...

# Code Quality
lint: ## Run all linters
	@echo "Running linters..."
	golangci-lint run
	cd frontend && npm run lint

fmt: ## Format code
	@echo "Formatting code..."
	go fmt ./...
	cd frontend && npm run format

coverage: ## Generate coverage report
	@echo "Generating coverage report..."
	go tool cover -html=coverage.out -o coverage.html
	cd frontend && npm run coverage:report
	@echo "Coverage report generated: coverage.html"

# Dependencies
deps: ## Install/update dependencies
	@echo "Installing dependencies..."
	go mod download
	go mod tidy
	cd frontend && npm install

deps-update: ## Update all dependencies
	@echo "Updating dependencies..."
	go get -u ./...
	go mod tidy
	cd frontend && npm update

# Database/Config
migrate-config: ## Migrate configuration from PyWebView format
	@echo "Migrating configuration..."
	go run cmd/migrate/main.go

# Cleaning
clean: ## Clean build artifacts
	@echo "Cleaning build artifacts..."
	rm -rf build/
	rm -rf dist/
	rm -rf frontend/dist/
	rm -rf frontend/node_modules/.cache/
	rm -f coverage.out coverage.html

clean-all: clean ## Clean everything including dependencies
	@echo "Cleaning dependencies..."
	rm -rf frontend/node_modules/
	go clean -modcache

# Security
security-audit: ## Run security audit
	@echo "Running security audit..."
	go list -json -m all | nancy sleuth
	cd frontend && npm audit

security-validate: ## Validate WSL permissions and security
	@echo "Validating security setup..."
	@chmod +x scripts/security/validate-permissions.sh
	@./scripts/security/validate-permissions.sh

# Installation
install: build ## Install binary to system PATH
	@echo "Installing ComfyUI Launcher..."
	sudo cp build/bin/ComfyUI-Launcher /usr/local/bin/
	@echo "Installed to /usr/local/bin/ComfyUI-Launcher"

uninstall: ## Remove binary from system PATH
	@echo "Uninstalling ComfyUI Launcher..."
	sudo rm -f /usr/local/bin/ComfyUI-Launcher
	@echo "Uninstalled"

# Documentation
docs: ## Generate documentation
	@echo "Generating documentation..."
	go doc -all ./... > docs/api.md
	@echo "Documentation generated in docs/"

docs-serve: ## Serve documentation locally
	@echo "Serving documentation at http://localhost:6060"
	godoc -http=:6060

# Docker (future)
docker-build: ## Build Docker image
	@echo "Building Docker image..."
	docker build -t comfyui-launcher .

docker-run: ## Run in Docker container
	@echo "Running in Docker..."
	docker run -it --rm -p 8080:8080 comfyui-launcher

# Release
release: clean test build ## Prepare release build
	@echo "Creating release build..."
	mkdir -p dist/
	cp build/bin/ComfyUI-Launcher* dist/
	cd dist && sha256sum * > checksums.txt
	@echo "Release build ready in dist/"

# Performance
benchmark: ## Run performance benchmarks
	@echo "Running benchmarks..."
	go test -bench=. -benchmem ./...

profile: ## Run with profiling
	@echo "Starting with profiling enabled..."
	go run -race cmd/app/main.go -profile

# Version
version: ## Show version information
	@echo "ComfyUI Launcher - Wails Implementation"
	@echo "Go version: $$(go version)"
	@echo "Node version: $$(node --version)"
	@echo "Wails version: $$(wails version 2>/dev/null || echo 'Not installed')"

# Environment validation
check-env: ## Check development environment
	@echo "Checking development environment..."
	@command -v go >/dev/null 2>&1 || { echo "Go is not installed"; exit 1; }
	@command -v node >/dev/null 2>&1 || { echo "Node.js is not installed"; exit 1; }
	@command -v wails >/dev/null 2>&1 || { echo "Wails is not installed"; exit 1; }
	@echo "✅ Environment looks good!"

# AI Project Management
ai-pm-setup: ## Set up AI Project Manager
	@echo "Setting up AI Project Manager..."
	@./scripts/setup-ai-pm.sh

ai-pm-start: ## Start AI Project Manager services
	@docker compose -f docker-compose.ai-pm.yml up -d

ai-pm-stop: ## Stop AI Project Manager services
	@docker compose -f docker-compose.ai-pm.yml down

ai-pm-status: ## Check AI Project Manager service status
	@docker compose -f docker-compose.ai-pm.yml ps

ai-pm-dev-ui: ## Start PM UI in development mode
	@echo "Starting Project Management UI in development mode..."
	cd pm-ui && npm run dev

ai-pm-build-ui: ## Build PM UI for production
	@echo "Building Project Management UI..."
	cd pm-ui && npm run build

ai-pm-restart: ## Restart AI Project Manager services
	@docker compose -f docker-compose.ai-pm.yml down
	@docker compose -f docker-compose.ai-pm.yml up -d

ai-pm-logs: ## Show AI Project Manager logs
	@docker compose -f docker-compose.ai-pm.yml logs -f

ai-pm-cli: ## Open AI Project Manager CLI
	@echo "Opening AI Project Manager CLI..."
	@./scripts/project-manager.sh

# AI Project Manager Development
ai-pm-dev-start: ## Start AI PM services with hot reload for development
	@echo "Starting AI Project Manager in development mode..."
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up -d ai-pm-database ai-pm-cache ai-pm-storage
	@echo "Waiting for services to be ready..."
	@sleep 5
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up ai-pm-api-dev ai-pm-ui-dev

ai-pm-dev-backend: ## Start only backend with hot reload
	@echo "Starting AI PM backend with hot reload..."
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up ai-pm-api-dev

ai-pm-dev-frontend: ## Start only frontend with hot reload  
	@echo "Starting AI PM frontend with hot reload..."
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml up ai-pm-ui-dev

ai-pm-dev-logs: ## View development logs
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml logs -f ai-pm-api-dev ai-pm-ui-dev

ai-pm-dev-stop: ## Stop development services
	cd ai-pm && docker-compose -f docker-compose.yml -f docker-compose.dev.yml down ai-pm-api-dev ai-pm-ui-dev

# Quick start for new developers
quick-start: check-env deps test ## Quick start for new developers
	@echo ""
	@echo "🎉 Setup complete! Next steps:"
	@echo "  1. Start development: make dev"
	@echo "  2. Run tests: make test"
	@echo "  3. Build: make build"
	@echo "  4. Set up project management: make ai-pm-setup"
	@echo ""
