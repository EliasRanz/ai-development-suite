# AI Tools Development Environment Setup

## Quick Start for New Machines

If you're setting up development on a new machine, use our cross-platform setup script:

``## Script Features

- 🌍 **Cross-platform** - Works on Windows, macOS, and Linux
- 🔒 **Secure** - Generates unique passwords and API keys
- 🚀 **Fast** - Installs only what's needed for your platform
- ✅ **Validated** - Tests that everything works correctly
- 📝 **Informative** - Clear status messages and error handling
- 🔧 **Flexible** - Can be run multiple times safely
- 🏃 **Safe** - Dry-run mode to preview changes
- 🔍 **Debuggable** - Verbose mode and comprehensive error reporting
- ⚡ **Efficient** - Skip tests option for faster repeated runsClone the repository
git clone https://github.com/EliasRanz/ai-development-suite.git
cd ai-development-suite

# Run the cross-platform setup script
make setup-dev
# OR directly: ./scripts/setup-dev-environment.sh
```

### Setup Options

The setup script supports several options for different use cases:

```bash
# Basic setup (interactive)
./scripts/setup-dev-environment.sh

# See what would be done without making changes
./scripts/setup-dev-environment.sh --dry-run

# Skip validation tests (faster setup)
./scripts/setup-dev-environment.sh --skip-tests

# Verbose output for debugging
./scripts/setup-dev-environment.sh --verbose

# Get help
./scripts/setup-dev-environment.sh --help
```

## What the Setup Script Does

The `setup-dev-environment.sh` script automatically:

### 🔍 **Environment Detection**
- Detects your operating system (Windows/WSL, macOS, Linux)
- Chooses appropriate installation methods for your platform

### 📦 **Prerequisites Installation**
- **Git** - Version control
- **Docker & Docker Compose** - Container management
- **Node.js & npm** - Frontend development 
- **Go** - Backend development
- **Make** - Build automation

### 🛠️ **Development Tools**
- **Air** - Go hot reload for backend development
- **Wails** - Desktop app framework for AI Studio
- **Environment files** - Secure credential generation

### ⚙️ **Project Setup**
- **AI Project Manager** - Environment configuration with secure credentials
- **AI Studio** - Dependencies installation (Go modules + npm packages)
- **Validation** - Tests that everything works correctly

## Platform Support

| Platform | Support Level | Notes |
|----------|---------------|-------|
| **Linux** | ✅ Full | Native package managers (apt, yum, pacman) |
| **WSL2** | ✅ Full | Detected automatically, Linux tools in Windows |
| **macOS** | ✅ Full | Homebrew-based installation |
| **Windows** | ⚠️ Partial | Manual installation required for some tools |

## Manual Setup (Alternative)

If you prefer manual setup or the script fails:

### 1. Install Prerequisites
```bash
# Install Docker Desktop for your platform
# Install Git, Node.js, Go manually

# Verify installations
docker --version
git --version
node --version
go version
make --version
```

### 2. Install Development Tools
```bash
# Install Go tools
go install github.com/cosmtrek/air@latest
go install github.com/wailsapp/wails/v2/cmd/wails@latest

# Verify tools are in PATH
air -v
wails version
```

### 3. Setup AI Project Manager
```bash
cd ai-pm
cp .env.example .env  # Edit with your credentials
make ai-pm-start
```

### 4. Setup AI Studio
```bash
cd ai-studio
go mod download
cd frontend && npm install
```

## Troubleshooting

### Common Issues

**"Docker not running"**
```bash
# Start Docker Desktop and wait for it to be ready
docker info  # Should show system information
```

**"Command not found: air/wails"**
```bash
# Add Go bin to PATH
export PATH=$PATH:$(go env GOPATH)/bin
# Add to ~/.bashrc or ~/.zshrc to make permanent
```

**"Permission denied"**
```bash
# Make script executable
chmod +x scripts/setup-dev-environment.sh
```

**"Package manager not found"**
- **Linux**: Install `apt-get`, `yum`, or `pacman` for your distribution
- **macOS**: Install Homebrew: `/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"`
- **Windows**: Use WSL2 or install tools manually

### Getting Help

1. **Check Prerequisites**: `make check-env`
2. **View Setup Status**: `make ai-pm-status`
3. **Read Documentation**: `.github/instructions/project-management.md`
4. **Check Logs**: `make ai-pm-logs`

## Next Steps After Setup

Once setup is complete:

```bash
# For Project Management development
AI_PM_MODE=dev make ai-pm-start

# For AI Studio development  
make dev

# For other development work
make ai-pm-start

# Check what's running
make ai-pm-status
```

## Developer Onboarding Experience

### 🎯 **Goal**: Get from "git clone" to "ready to develop" in under 10 minutes

Our cross-platform setup script provides a comprehensive, intelligent onboarding experience:

### ✨ **What Makes It Special**

1. **🎛️ Smart Detection**
   - Automatically detects OS (Linux, WSL2, macOS, Windows)
   - Chooses optimal installation method for your platform
   - Checks existing installations to avoid conflicts

2. **🛡️ Safety First**
   - Interactive confirmation before making changes
   - `--dry-run` mode to preview what will happen
   - Generates secure, unique credentials automatically
   - Never overwrites existing configurations

3. **🧠 Intelligent Error Handling**
   - Automatic troubleshooting tips when issues arise
   - Platform-specific solutions for common problems
   - Verbose mode for debugging complex issues

4. **⚡ Flexibility**
   - `--skip-tests` for faster repeated runs
   - `--verbose` for detailed progress tracking
   - Handles partial setups gracefully
   - Can be run multiple times safely

### 🚀 **New Developer Journey**

1. **First Run**: `./scripts/setup-dev-environment.sh --dry-run`
   - See exactly what will be installed
   - No changes to your system
   - Builds confidence before proceeding

2. **Full Setup**: `make setup-dev`
   - Complete environment setup
   - Secure credential generation
   - Validation and testing

3. **Start Developing**: `AI_PM_MODE=dev make ai-pm-start`
   - Jump straight into development
   - Hot reload and debugging ready
   - All services configured and tested

### 📋 **Supports All Developer Types**

- **Backend Developers**: Go environment, Air hot reload, database ready
- **Frontend Developers**: Node.js, npm packages, dev server with HMR
- **DevOps Engineers**: Docker, Make, all infrastructure automated
- **New Team Members**: Comprehensive documentation and guided setup
- **Cross-Platform Teams**: Windows (WSL), macOS, Linux all supported

### 🔧 **Troubleshooting Built-In**

Common issues are detected and resolved automatically:
- PATH configuration for Go tools
- Docker resource allocation
- Port conflicts
- Package manager issues
- Network connectivity problems

The setup script gets smarter with each improvement, making onboarding easier for everyone.

## Script Features

- 🌍 **Cross-platform** - Works on Windows, macOS, and Linux
- 🔒 **Secure** - Generates unique passwords and API keys
- 🚀 **Fast** - Installs only what's needed for your platform
- ✅ **Validated** - Tests the setup before completing
- 📝 **Informative** - Clear status messages and error handling
- 🔧 **Flexible** - Can be run multiple times safely

Happy coding! 🎉
