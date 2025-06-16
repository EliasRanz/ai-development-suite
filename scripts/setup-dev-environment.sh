#!/bin/bash

# AI Tools Development Environment Setup
# Cross-platform setup script for development environment
# Supports Windows (WSL), macOS, and Linux

set -e

# Default settings
SKIP_TESTS=false
VERBOSE=false
DRY_RUN=false

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse command line arguments
parse_args() {
    while [[ $# -gt 0 ]]; do
        case $1 in
            --help|-h)
                show_help
                exit 0
                ;;
            --skip-tests)
                SKIP_TESTS=true
                shift
                ;;
            --verbose|-v)
                VERBOSE=true
                shift
                ;;
            --dry-run)
                DRY_RUN=true
                shift
                ;;
            *)
                echo "Unknown option: $1"
                show_help
                exit 1
                ;;
        esac
    done
}

# Show help
show_help() {
    echo "AI Tools Development Environment Setup"
    echo ""
    echo "Usage: $0 [OPTIONS]"
    echo ""
    echo "Options:"
    echo "  -h, --help        Show this help message"
    echo "  --skip-tests      Skip the setup validation tests"
    echo "  -v, --verbose     Enable verbose output"
    echo "  --dry-run         Show what would be done without making changes"
    echo ""
    echo "This script will:"
    echo "  • Detect your OS and install prerequisites"
    echo "  • Set up AI Project Manager with secure credentials"
    echo "  • Install AI Studio dependencies"
    echo "  • Install development tools (Air, Wails)"
    echo "  • Test the complete setup"
    echo ""
    echo "Platform support:"
    echo "  ✅ Linux (native package managers)"
    echo "  ✅ WSL2 (auto-detected)"
    echo "  ✅ macOS (via Homebrew)"
    echo "  ⚠️  Windows (manual installation required for some tools)"
}

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
    if [[ "$VERBOSE" == "true" ]]; then
        echo "  └─ $(date '+%H:%M:%S')"
    fi
}

print_success() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

print_section() {
    echo ""
    echo -e "${BLUE}================================${NC}"
    echo -e "${BLUE}$1${NC}"
    echo -e "${BLUE}================================${NC}"
}

# Detect operating system
detect_os() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        if grep -q Microsoft /proc/version; then
            OS="wsl"
            print_status "Detected Windows Subsystem for Linux (WSL)"
        else
            OS="linux"
            print_status "Detected Linux"
        fi
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        OS="macos"
        print_status "Detected macOS"
    elif [[ "$OSTYPE" == "msys" ]] || [[ "$OSTYPE" == "cygwin" ]]; then
        OS="windows"
        print_status "Detected Windows (Git Bash/Cygwin)"
    else
        print_error "Unsupported operating system: $OSTYPE"
        exit 1
    fi
}

# Check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Execute command with dry-run support
safe_execute() {
    local cmd="$1"
    local description="$2"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would execute: $description"
        print_status "  Command: $cmd"
        return 0
    fi
    
    if [[ "$VERBOSE" == "true" ]]; then
        print_status "Executing: $description"
        print_status "  Command: $cmd"
    fi
    
    eval "$cmd"
}

# Install function for different package managers
install_package() {
    local package=$1
    print_status "Installing $package..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would install package: $package"
        return 0
    fi
    
    case $OS in
        "macos")
            if command_exists brew; then
                safe_execute "brew install \"$package\"" "Install $package via Homebrew"
            else
                print_error "Homebrew not found. Please install Homebrew first."
                echo "Run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
                exit 1
            fi
            ;;
        "linux"|"wsl")
            if command_exists apt-get; then
                safe_execute "sudo apt-get update && sudo apt-get install -y \"$package\"" "Install $package via apt"
            elif command_exists yum; then
                safe_execute "sudo yum install -y \"$package\"" "Install $package via yum"
            elif command_exists pacman; then
                safe_execute "sudo pacman -S --noconfirm \"$package\"" "Install $package via pacman"
            else
                print_error "No supported package manager found"
                exit 1
            fi
            ;;
        "windows")
            print_warning "Please install $package manually on Windows"
            print_status "Consider using WSL2 for better development experience"
            ;;
    esac
}

# Check and install prerequisites
check_prerequisites() {
    print_section "Checking Prerequisites"
    
    # Check Git
    if command_exists git; then
        local git_version=$(git --version | cut -d' ' -f3)
        print_success "Git $git_version is installed"
    else
        print_warning "Git not found, attempting to install..."
        install_package git
    fi
    
    # Check Docker
    if command_exists docker; then
        if docker info > /dev/null 2>&1; then
            local docker_version=$(docker --version | cut -d' ' -f3 | tr -d ',')
            print_success "Docker $docker_version is running"
        else
            print_error "Docker is installed but not running. Please start Docker and try again."
            exit 1
        fi
    else
        print_error "Docker not found. Please install Docker Desktop for your platform:"
        echo "  - Windows: https://docs.docker.com/desktop/install/windows-install/"
        echo "  - macOS: https://docs.docker.com/desktop/install/mac-install/"
        echo "  - Linux: https://docs.docker.com/desktop/install/linux-install/"
        exit 1
    fi
    
    # Check Docker Compose
    if docker compose version > /dev/null 2>&1; then
        local compose_version=$(docker compose version --short)
        print_success "Docker Compose $compose_version is available"
    else
        print_error "Docker Compose not found. Please update Docker to latest version."
        exit 1
    fi
    
    # Check Node.js (for AI Studio development)
    if command_exists node; then
        local node_version=$(node --version)
        print_success "Node.js $node_version is installed"
        
        # Check npm
        if command_exists npm; then
            local npm_version=$(npm --version)
            print_success "npm $npm_version is installed"
        else
            print_error "npm not found. Please reinstall Node.js with npm."
            exit 1
        fi
    else
        print_warning "Node.js not found. Installing via package manager..."
        case $OS in
            "macos")
                brew install node
                ;;
            "linux"|"wsl")
                curl -fsSL https://deb.nodesource.com/setup_lts.x | sudo -E bash -
                sudo apt-get install -y nodejs
                ;;
            "windows")
                print_error "Please install Node.js from https://nodejs.org/"
                exit 1
                ;;
        esac
    fi
    
    # Check Go (for backend development)
    if command_exists go; then
        local go_version=$(go version | cut -d' ' -f3)
        print_success "Go $go_version is installed"
    else
        print_warning "Go not found. Installing..."
        case $OS in
            "macos")
                brew install go
                ;;
            "linux"|"wsl")
                local go_version="1.21.5"
                wget -q "https://golang.org/dl/go${go_version}.linux-amd64.tar.gz"
                sudo rm -rf /usr/local/go
                sudo tar -C /usr/local -xzf "go${go_version}.linux-amd64.tar.gz"
                rm "go${go_version}.linux-amd64.tar.gz"
                
                # Add to PATH if not already there
                if ! grep -q "/usr/local/go/bin" ~/.bashrc; then
                    echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
                    echo 'export PATH=$PATH:$(go env GOPATH)/bin' >> ~/.bashrc
                    print_status "Added Go to PATH in ~/.bashrc"
                fi
                
                export PATH=$PATH:/usr/local/go/bin
                ;;
            "windows")
                print_error "Please install Go from https://golang.org/dl/"
                exit 1
                ;;
        esac
    fi
    
    # Check Make
    if command_exists make; then
        print_success "Make is installed"
    else
        print_warning "Make not found, installing..."
        case $OS in
            "macos")
                # Usually comes with Xcode command line tools
                xcode-select --install 2>/dev/null || true
                ;;
            "linux"|"wsl")
                install_package build-essential
                ;;
            "windows")
                print_error "Please install Make or use WSL for development"
                ;;
        esac
    fi
}

# Setup AI Project Manager environment
setup_ai_pm() {
    print_section "Setting up AI Project Manager"
    
    cd ai-pm
    
    # Create .env file if it doesn't exist
    if [ ! -f .env ]; then
        print_status "Creating .env file with secure credentials..."
        
        if [[ "$DRY_RUN" == "true" ]]; then
            print_status "[DRY RUN] Would create .env file with generated credentials"
            cd ..
            return 0
        fi
        
        # Generate secure random passwords
        if command_exists openssl; then
            AI_PM_DB_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-25)
            AI_PM_SECRET_KEY=$(openssl rand -base64 32)
        else
            # Fallback for systems without openssl
            AI_PM_DB_PASSWORD="aipm_$(date +%s | sha256sum | base64 | head -c 12)"
            AI_PM_SECRET_KEY="secret_$(date +%s | sha256sum | base64 | head -c 20)"
        fi
        
        cat > .env << EOF
# Environment variables for development
# Generated by setup script - modify as needed

# AI Project Manager Infrastructure
AI_PM_DB_USER=aipm
AI_PM_DB_PASSWORD=${AI_PM_DB_PASSWORD}
AI_PM_DB_NAME=ai_project_manager
AI_PM_SECRET_KEY=${AI_PM_SECRET_KEY}

# Development
NODE_ENV=development
GO_ENV=development
EOF
        
        print_success "Created .env file with secure credentials"
        print_status "💡 Tip: You can modify ai-pm/.env to customize your setup"
    else
        print_success ".env file already exists"
    fi
    
    cd ..
}

# Setup AI Studio dependencies
setup_ai_studio() {
    print_section "Setting up AI Studio"
    
    if [ -d "ai-studio" ]; then
        cd ai-studio
        
        # Install Go dependencies
        if [ -f "go.mod" ]; then
            print_status "Installing Go dependencies..."
            go mod download
            go mod tidy
            print_success "Go dependencies installed"
        fi
        
        # Install frontend dependencies
        if [ -d "frontend" ] && [ -f "frontend/package.json" ]; then
            print_status "Installing frontend dependencies..."
            cd frontend
            npm install
            cd ..
            print_success "Frontend dependencies installed"
        fi
        
        cd ..
    else
        print_warning "AI Studio directory not found, skipping setup"
    fi
}

# Install development tools
install_dev_tools() {
    print_section "Installing Development Tools"
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would install Air and Wails"
        return 0
    fi
    
    # Install Air for Go hot reload (updated package)
    if ! command_exists air; then
        print_status "Installing Air for Go hot reload..."
        # Air has moved to a new repository
        safe_execute "go install github.com/air-verse/air@latest" "Install Air hot reload tool"
        print_success "Air installed"
    else
        print_success "Air already installed"
    fi
    
    # Install Wails for AI Studio development
    if ! command_exists wails; then
        print_status "Installing Wails..."
        safe_execute "go install github.com/wailsapp/wails/v2/cmd/wails@latest" "Install Wails framework"
        print_success "Wails installed"
    else
        print_success "Wails already installed"
    fi
    
    # Verify tools are in PATH
    if ! command_exists air; then
        print_warning "Air not found in PATH. You may need to add \$GOPATH/bin to your PATH"
        echo "Run: export PATH=\$PATH:\$(go env GOPATH)/bin"
    fi
    
    if ! command_exists wails; then
        print_warning "Wails not found in PATH. You may need to add \$GOPATH/bin to your PATH"
        echo "Run: export PATH=\$PATH:\$(go env GOPATH)/bin"
    fi
    
    # Check Go version for Air compatibility
    local go_version=$(go version | grep -oE 'go[0-9]+\.[0-9]+\.[0-9]+' | sed 's/go//')
    if [[ "$go_version" < "1.22" ]]; then
        print_warning "Go version $go_version detected. Some tools may require Go 1.22+"
        print_status "Consider updating Go for the best experience"
    fi
}

# Test the setup
test_setup() {
    if [[ "$SKIP_TESTS" == "true" ]]; then
        print_section "Skipping Setup Tests (--skip-tests)"
        return 0
    fi
    
    print_section "Testing Setup"
    
    print_status "Testing Makefile commands..."
    
    if [[ "$DRY_RUN" == "true" ]]; then
        print_status "[DRY RUN] Would test Makefile commands and start services"
        return 0
    fi
    
    # Test help command
    if make help > /dev/null 2>&1; then
        print_success "Makefile commands working"
    else
        print_error "Makefile commands failed"
        exit 1
    fi
    
    # Test environment check
    if make check-env > /dev/null 2>&1; then
        print_success "Environment check passed"
    else
        print_warning "Environment check failed - some tools may be missing"
    fi
    
    print_status "Starting AI Project Manager to verify setup..."
    
    # Try to start AI PM services
    if make ai-pm-start > /dev/null 2>&1; then
        print_success "AI Project Manager started successfully"
        
        # Give services time to start
        print_status "Waiting for services to initialize..."
        sleep 10
        
        # Check if services are healthy
        if make ai-pm-status > /dev/null 2>&1; then
            print_success "Services are running properly"
            
            # Test basic connectivity
            if curl -s http://localhost:8000/api/health > /dev/null 2>&1; then
                print_success "API health check passed"
            else
                print_warning "API not responding (may still be starting up)"
            fi
            
            # Stop services to clean up
            make ai-pm-stop > /dev/null 2>&1
            print_status "Stopped test services"
        else
            print_warning "Services started but status check failed"
        fi
    else
        print_error "Failed to start AI Project Manager"
        print_status "Check Docker is running and try again"
        print_status "💡 Debug with: make ai-pm-logs"
    fi
}

# Generate summary
generate_summary() {
    print_section "Setup Complete!"
    
    echo ""
    echo "🎉 Your AI Tools development environment is ready!"
    echo ""
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🏃 This was a dry run - no changes were made"
        echo "💡 Run without --dry-run to perform the actual setup"
        echo ""
        return 0
    fi
    
    echo "📚 Quick Start Guide:"
    echo "  1. Choose your development focus:"
    echo "     💼 Project Management: AI_PM_MODE=dev make ai-pm-start"
    echo "     🖥️  AI Studio: make dev"
    echo "     🔧 Other tools: make ai-pm-start"
    echo ""
    echo "  2. Access the applications:"
    echo "     🌐 Project Management UI:"
    echo "        • Production: http://localhost:3000"
    echo "        • Development: http://localhost:3002"
    echo "     🔌 Project Management API:"
    echo "        • Production: http://localhost:8000"
    echo "        • Development: http://localhost:8001"
    echo ""
    echo "  3. Use the CLI tools:"
    echo "     📋 Project management: ./scripts/project-manager.sh help"
    echo "     📊 Environment status: make ai-pm-status"
    echo "     📜 View logs: make ai-pm-logs"
    echo ""
    echo "  4. Read the documentation:"
    echo "     📖 Project management: .github/instructions/project-management.md"
    echo "     🔧 Development setup: ai-pm/docs/DEVELOPMENT_SETUP.md"
    echo "     🏗️  Architecture: ADRs/ directory"
    echo ""
    echo "🆘 Need help?"
    echo "   • Run 'make help' to see all available commands"
    echo "   • Check 'make ai-pm-status' if services aren't working"
    echo "   • Use 'make ai-pm-logs' to debug issues"
    echo ""
    print_success "Happy coding! 🚀"
    
    if [[ "$VERBOSE" == "true" ]]; then
        echo ""
        echo "🔍 Setup completed at: $(date)"
        echo "💻 Platform: $OS"
        echo "🏠 Working directory: $(pwd)"
    fi
}

# Main execution
main() {
    # Parse command line arguments first
    parse_args "$@"
    
    echo ""
    echo "🛠️  AI Tools Development Environment Setup"
    echo "=========================================="
    echo ""
    
    if [[ "$DRY_RUN" == "true" ]]; then
        echo "🏃 DRY RUN MODE - No changes will be made"
        echo ""
    fi
    
    echo "This script will set up your development environment for:"
    echo "  • AI Project Management System"
    echo "  • AI Studio Desktop Application"
    echo "  • Supporting tools and dependencies"
    echo ""
    
    if [[ "$DRY_RUN" != "true" ]]; then
        echo "⚠️  This script will install software and modify your system."
        echo "   Press Ctrl+C to cancel, or Enter to continue..."
        read -r
    fi
    
    detect_os
    check_prerequisites
    setup_ai_pm
    setup_ai_studio
    install_dev_tools
    test_setup
    generate_summary
}

# Run main function
main "$@"
