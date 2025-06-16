# AI Tools Repository Structure

This repository contains multiple AI development tools organized as a monorepo for easier development and maintenance.

## 📁 Project Organization

### 🎯 **AI Project Manager** (`ai-pm/`)
The standalone project management system for AI development workflows.

**Components:**
- `ai-pm/backend/` - Go API service (currently `pm-service/`)
- `ai-pm/frontend/` - React UI (currently `pm-ui/`)
- `ai-pm/scripts/` - PM-specific scripts
- `ai-pm/docker-compose.yml` - PM infrastructure
- `ai-pm/README.md` - PM-specific documentation

### 🖼️ **ComfyUI Launcher** (`comfy-ui/`)
Desktop application for managing ComfyUI workflows.

**Components:**
- `comfy-ui/launcher/` - Python launcher (moved from `comfy_launcher/`)
- `comfy-ui/scripts/` - ComfyUI-specific utilities

### 🖥️ **General Frontend** (`frontend/`)
Wails-based frontend framework for the broader AI tools ecosystem.

## 🚀 Distribution Strategy

### Individual Project Releases
Each tool can be packaged and released independently:

```bash
# AI Project Manager release
make release-ai-pm

# ComfyUI Launcher release  
make release-comfy-ui
```

### Repository Benefits
- **Single development environment** - One repo to clone and setup
- **Shared tooling** - Common Makefile, scripts, CI/CD
- **Cross-project utilities** - Reusable components
- **Simplified maintenance** - Single dependency management
- **Better documentation** - Centralized knowledge base

## 📦 Package Distribution

Individual tools will be distributed as:
- **Docker images** for AI Project Manager
- **Binary releases** for ComfyUI Launcher
- **NPM packages** for reusable components
- **Git tags** for version management

This approach provides the benefits of both monorepo development and independent distribution.
