#!/bin/bash

# Repository Restructure Script
# Reorganizes the current mixed repository into a clean monorepo structure

set -e

echo "🔄 Restructuring repository into organized monorepo..."

# Create new directory structure
echo "📁 Creating new directory structure..."
mkdir -p ai-pm/{backend,frontend,scripts,docs}
mkdir -p comfy-ui/{launcher,gui,scripts}
mkdir -p shared/{scripts,configs,docs}

# Move AI Project Manager components
echo "🎯 Moving AI Project Manager components..."
if [ -d "pm-service" ]; then
    mv pm-service/* ai-pm/backend/
    rmdir pm-service
fi

if [ -d "pm-ui" ]; then
    mv pm-ui/* ai-pm/frontend/
    rmdir pm-ui
fi

# Move AI PM specific files
mv docker-compose.ai-pm.yml ai-pm/docker-compose.yml

# Move AI PM scripts
cp scripts/project-manager.sh ai-pm/scripts/
cp scripts/setup-ai-pm.sh ai-pm/scripts/setup.sh
cp scripts/ai-pm-api.sh ai-pm/scripts/api-test.sh

# Move ComfyUI components
echo "🖼️ Moving ComfyUI Launcher components..."
if [ -d "comfy_launcher" ]; then
    mv comfy_launcher/* comfy-ui/launcher/
    rmdir comfy_launcher
fi

if [ -d "frontend" ]; then
    mv frontend/* comfy-ui/gui/
    rmdir frontend
fi

# Move shared utilities
echo "🔧 Moving shared components..."
mv scripts/cleanup-repository.sh shared/scripts/
mv scripts/fix-permissions.sh shared/scripts/
cp -r scripts/security shared/scripts/
cp -r scripts/wsl shared/scripts/

# Create project-specific documentation
echo "📚 Creating project documentation..."

# AI PM README
cat > ai-pm/README.md << 'EOF'
# AI Project Manager

A modern, AI-driven project management system designed for development workflows.

## Features

- ✅ Task and project tracking with soft delete
- 🔄 Workflow status management (todo, in_progress, validation, done, blocked)
- 🏷️ Task type classification (feature, bug, maintenance, research)
- 📊 Real-time dashboard and analytics
- 🔗 CLI integration for AI agents
- 🐳 Docker-based infrastructure

## Quick Start

```bash
# Setup the system
./scripts/setup.sh

# Use the CLI
./scripts/project-manager.sh list-tasks
```

## Architecture

- **Backend**: Go API service with PostgreSQL
- **Frontend**: React + TypeScript UI
- **Infrastructure**: Docker Compose with Redis caching
- **CLI**: Bash script for automation

See [documentation](docs/) for detailed information.
EOF

# ComfyUI README
cat > comfy-ui/README.md << 'EOF'
# ComfyUI Launcher

A desktop application for managing and launching ComfyUI workflows with an integrated GUI.

## Features

- 🖥️ Native desktop application (Wails framework)
- 🎨 Modern React frontend
- 🔧 Integrated ComfyUI server management
- 📱 System tray integration
- 📊 Real-time monitoring and logging

## Quick Start

```bash
# Build the application
make build

# Run in development mode
make dev
```

## Architecture

- **Desktop App**: Wails (Go + React)
- **Backend**: Python server management
- **Frontend**: React + TypeScript
- **Integration**: System tray and native OS features

See [documentation](../shared/docs/) for detailed information.
EOF

# Update root README
cat > README.md << 'EOF'
# AI Development Tools

A collection of AI development tools designed to streamline workflows and enhance productivity.

## 🛠️ Tools Included

### 🎯 [AI Project Manager](ai-pm/)
Modern project management system optimized for AI development workflows.
- Task tracking with AI agent integration
- Workflow automation and status management  
- Real-time collaboration features

### 🖼️ [ComfyUI Launcher](comfy-ui/)
Desktop application for managing ComfyUI workflows.
- Native desktop integration
- Server management and monitoring
- User-friendly GUI interface

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>
cd ai-tools

# Setup AI Project Manager
cd ai-pm && ./scripts/setup.sh

# Or build ComfyUI Launcher
cd comfy-ui && make build
```

## 📁 Repository Structure

This is organized as a monorepo for easier development:
- `ai-pm/` - AI Project Manager (standalone)
- `comfy-ui/` - ComfyUI Launcher (standalone) 
- `shared/` - Common utilities and documentation

Each tool can be used independently and has its own documentation.

## 🔧 Development

See individual tool READMEs for specific setup instructions.

For general development utilities, see [`shared/`](shared/) directory.
EOF

echo "✅ Repository restructure complete!"
echo ""
echo "📋 Next steps:"
echo "1. Review the new structure"
echo "2. Update any remaining file references"
echo "3. Test both tools work in new locations"  
echo "4. Commit the restructured repository"
echo ""
echo "🎯 Each tool now has its own directory and can be distributed independently!"
