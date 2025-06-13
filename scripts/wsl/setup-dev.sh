#!/bin/bash
set -euo pipefail

# ComfyUI Launcher - WSL Development Environment Setup
# This script sets up a complete development environment for Wails + React

echo "🚀 ComfyUI Launcher - WSL Development Setup"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Logging functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running in WSL
check_wsl() {
    if ! grep -q Microsoft /proc/version; then
        log_error "This script is designed for WSL (Windows Subsystem for Linux)"
        log_info "Please run this script from within WSL"
        exit 1
    fi
    log_success "Running in WSL environment"
}

# Update system packages
update_system() {
    log_info "Updating system packages..."
    sudo apt-get update -qq
    sudo apt-get upgrade -y -qq
    log_success "System packages updated"
}

# Install essential build tools
install_build_tools() {
    log_info "Installing build tools and dependencies..."
    
    sudo apt-get install -y \
        build-essential \
        pkg-config \
        libgtk-3-dev \
        libwebkit2gtk-4.0-dev \
        git \
        curl \
        wget \
        unzip \
        software-properties-common \
        apt-transport-https \
        ca-certificates \
        gnupg \
        lsb-release > /dev/null 2>&1
    
    log_success "Build tools installed"
}

# Install Go
install_go() {
    local GO_VERSION="1.21.5"
    
    if command -v go &> /dev/null; then
        local current_version=$(go version | awk '{print $3}' | sed 's/go//')
        log_info "Go $current_version is already installed"
        
        if [[ "$current_version" < "$GO_VERSION" ]]; then
            log_warning "Go version is outdated, updating to $GO_VERSION"
        else
            log_success "Go version is current"
            return 0
        fi
    fi
    
    log_info "Installing Go $GO_VERSION..."
    
    # Download and install Go
    cd /tmp
    wget -q "https://golang.org/dl/go${GO_VERSION}.linux-amd64.tar.gz"
    
    # Remove existing installation
    sudo rm -rf /usr/local/go
    
    # Extract new version
    sudo tar -C /usr/local -xzf "go${GO_VERSION}.linux-amd64.tar.gz"
    
    # Add to PATH
    if ! grep -q "/usr/local/go/bin" ~/.bashrc; then
        echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.bashrc
    fi
    
    if ! grep -q "/usr/local/go/bin" ~/.zshrc 2>/dev/null; then
        echo 'export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin' >> ~/.zshrc 2>/dev/null || true
    fi
    
    # Source the PATH for current session
    export PATH=$PATH:/usr/local/go/bin:$HOME/go/bin
    
    # Verify installation
    if /usr/local/go/bin/go version &> /dev/null; then
        log_success "Go $GO_VERSION installed successfully"
    else
        log_error "Go installation failed"
        exit 1
    fi
    
    # Clean up
    rm -f "/tmp/go${GO_VERSION}.linux-amd64.tar.gz"
}

# Install Node.js
install_nodejs() {
    local NODE_VERSION="18"
    
    if command -v node &> /dev/null; then
        local current_version=$(node --version | cut -d'v' -f2 | cut -d'.' -f1)
        log_info "Node.js v$current_version is already installed"
        
        if [[ "$current_version" -ge "$NODE_VERSION" ]]; then
            log_success "Node.js version is current"
            return 0
        else
            log_warning "Node.js version is outdated, updating to v$NODE_VERSION"
        fi
    fi
    
    log_info "Installing Node.js $NODE_VERSION..."
    
    # Install Node.js via NodeSource repository
    curl -fsSL https://deb.nodesource.com/setup_${NODE_VERSION}.x | sudo -E bash - > /dev/null 2>&1
    sudo apt-get install -y nodejs > /dev/null 2>&1
    
    # Verify installation
    if command -v node &> /dev/null && command -v npm &> /dev/null; then
        local node_ver=$(node --version)
        local npm_ver=$(npm --version)
        log_success "Node.js $node_ver and npm $npm_ver installed successfully"
    else
        log_error "Node.js installation failed"
        exit 1
    fi
}

# Install Wails CLI
install_wails() {
    if command -v wails &> /dev/null; then
        local current_version=$(wails version 2>/dev/null | head -n1 | awk '{print $2}' || echo "unknown")
        log_info "Wails $current_version is already installed"
        
        # Update to latest version anyway
        log_info "Updating Wails to latest version..."
    else
        log_info "Installing Wails CLI..."
    fi
    
    # Install/update Wails
    go install github.com/wailsapp/wails/v2/cmd/wails@latest > /dev/null 2>&1
    
    # Verify installation
    if command -v wails &> /dev/null; then
        local wails_version=$(wails version 2>/dev/null | head -n1 | awk '{print $2}' || echo "installed")
        log_success "Wails $wails_version installed successfully"
    else
        log_error "Wails installation failed"
        log_error "Make sure \$HOME/go/bin is in your PATH"
        exit 1
    fi
}

# Install Go development tools
install_go_tools() {
    log_info "Installing Go development tools..."
    
    local tools=(
        "github.com/golangci/golangci-lint/cmd/golangci-lint@latest"
        "github.com/axw/gocov/gocov@latest"
        "github.com/matm/gocov-html@latest"
        "golang.org/x/tools/cmd/goimports@latest"
        "honnef.co/go/tools/cmd/staticcheck@latest"
    )
    
    for tool in "${tools[@]}"; do
        log_info "Installing $tool..."
        go install "$tool" > /dev/null 2>&1
    done
    
    log_success "Go development tools installed"
}

# Install frontend dependencies
install_frontend_deps() {
    if [[ ! -d "frontend" ]]; then
        log_warning "Frontend directory not found, skipping frontend dependencies"
        return 0
    fi
    
    log_info "Installing frontend dependencies..."
    
    cd frontend
    
    # Install npm dependencies
    npm install > /dev/null 2>&1
    
    # Install Playwright
    log_info "Installing Playwright and browsers..."
    npm install -g @playwright/test > /dev/null 2>&1
    npx playwright install > /dev/null 2>&1
    
    cd ..
    
    log_success "Frontend dependencies installed"
}

# Create development configuration
create_dev_config() {
    log_info "Creating development configuration..."
    
    # Create directories
    mkdir -p configs/logging
    mkdir -p logs
    
    # Create development logging config
    cat > configs/logging/development.json << 'EOF'
{
  "level": "debug",
  "format": "pretty",
  "output": "stdout",
  "file": {
    "enabled": true,
    "path": "logs/development.log",
    "maxSize": "10MB",
    "maxBackups": 5,
    "maxAge": 7
  }
}
EOF
    
    # Create Makefile if it doesn't exist
    if [[ ! -f "Makefile" ]]; then
        cat > Makefile << 'EOF'
.PHONY: dev test build lint fmt coverage clean

# Development
dev:
	@echo "🚀 Starting development server..."
	wails dev

# Testing
test:
	@echo "🧪 Running all tests..."
	make test-go
	make test-frontend

test-go:
	@echo "🔧 Running Go tests..."
	go test -v -race -coverprofile=coverage.out ./...

test-frontend:
	@echo "⚛️ Running React tests..."
	cd frontend && npm test -- --coverage --watchAll=false

test-e2e:
	@echo "🎭 Running E2E tests..."
	cd frontend && npx playwright test

# Building
build:
	@echo "📦 Building for Windows..."
	wails build -platform windows/amd64

build-all:
	@echo "📦 Building for all platforms..."
	wails build -platform windows/amd64
	wails build -platform linux/amd64

# Code Quality
lint:
	@echo "🔍 Running linters..."
	golangci-lint run
	cd frontend && npm run lint

fmt:
	@echo "🎨 Formatting code..."
	go fmt ./...
	goimports -w .
	cd frontend && npm run format

coverage:
	@echo "📊 Generating coverage report..."
	go test -coverprofile=coverage.out ./...
	go tool cover -html=coverage.out -o coverage.html
	@echo "Coverage report: coverage.html"

# Cleanup
clean:
	@echo "🧹 Cleaning build artifacts..."
	rm -rf build/
	rm -rf frontend/dist/
	rm -f coverage.out coverage.html

# WSL specific
wsl-setup:
	@echo "🐧 Setting up WSL environment..."
	./scripts/wsl/setup-dev.sh

# Help
help:
	@echo "Available commands:"
	@echo "  dev          - Start development server"
	@echo "  test         - Run all tests"
	@echo "  build        - Build for Windows"
	@echo "  lint         - Run code linters"
	@echo "  fmt          - Format code"
	@echo "  coverage     - Generate test coverage report"
	@echo "  clean        - Clean build artifacts"
	@echo "  help         - Show this help"
EOF
    fi
    
    log_success "Development configuration created"
}

# Validate installation
validate_installation() {
    log_info "Validating installation..."
    
    local errors=0
    
    # Check Go
    if ! command -v go &> /dev/null; then
        log_error "Go is not installed or not in PATH"
        errors=$((errors + 1))
    else
        log_success "Go: $(go version | awk '{print $3}')"
    fi
    
    # Check Node.js
    if ! command -v node &> /dev/null; then
        log_error "Node.js is not installed"
        errors=$((errors + 1))
    else
        log_success "Node.js: $(node --version)"
    fi
    
    # Check npm
    if ! command -v npm &> /dev/null; then
        log_error "npm is not installed"
        errors=$((errors + 1))
    else
        log_success "npm: $(npm --version)"
    fi
    
    # Check Wails
    if ! command -v wails &> /dev/null; then
        log_error "Wails is not installed or not in PATH"
        errors=$((errors + 1))
    else
        local wails_ver=$(wails version 2>/dev/null | head -n1 | awk '{print $2}' || echo "unknown")
        log_success "Wails: $wails_ver"
    fi
    
    # Check golangci-lint
    if ! command -v golangci-lint &> /dev/null; then
        log_warning "golangci-lint is not installed"
    else
        log_success "golangci-lint: available"
    fi
    
    if [[ $errors -eq 0 ]]; then
        log_success "All tools installed successfully!"
        return 0
    else
        log_error "$errors tools failed to install"
        return 1
    fi
}

# Print final instructions
print_instructions() {
    echo ""
    echo "🎉 Setup Complete!"
    echo "================="
    echo ""
    echo "To start developing:"
    echo "  1. Restart your shell or run: source ~/.bashrc"
    echo "  2. Initialize a new Wails project: wails init -n comfy-launcher-wails -t typescript"
    echo "  3. Start development server: make dev"
    echo ""
    echo "Available commands:"
    echo "  make dev      - Start development server"
    echo "  make test     - Run all tests"
    echo "  make build    - Build Windows executable"
    echo "  make lint     - Run code quality checks"
    echo ""
    echo "Documentation:"
    echo "  docs/WSL_SETUP.md       - Detailed setup guide"
    echo "  docs/DEVELOPMENT.md     - Development workflow"
    echo "  ADRs/                   - Architecture decisions"
    echo ""
    echo "Happy coding! 🚀"
}

# Main execution
main() {
    log_info "Starting ComfyUI Launcher development environment setup..."
    
    check_wsl
    update_system
    install_build_tools
    install_go
    install_nodejs
    install_wails
    install_go_tools
    install_frontend_deps
    create_dev_config
    
    if validate_installation; then
        print_instructions
    else
        log_error "Setup completed with errors. Please check the error messages above."
        exit 1
    fi
}

# Run main function
main "$@"
