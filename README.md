# AI Development Tools

A collection of AI development tools designed to streamline workflows and enhance productivity.

## 🛠️ Tools Included

# AI Development Tools

A comprehensive suite of AI development tools designed to streamline workflows and enhance productivity.

## 🛠️ Tools Included

### � [AI Studio](ai-studio/)
Universal desktop application for managing AI development tools.
- Native cross-platform app (Wails + React)
- Supports ComfyUI, Automatic1111, Ollama, LM Studio, and more
- Real-time monitoring and configuration management
- Modern, responsive interface

### �🎯 [AI Project Manager](ai-pm/)
Web-based project management system optimized for AI development workflows.
- Task tracking with AI agent integration
- Workflow automation and status management  
- Real-time collaboration features
- CLI integration for automated workflows

### 🖼️ [ComfyUI Components](comfy-ui/)
Legacy ComfyUI launcher components (being replaced by AI Studio).
- Python-based ComfyUI management
- Will be deprecated in favor of AI Studio

## 🚀 Quick Start

### AI Studio (Recommended)
```bash
# Build the universal AI tools desktop app
cd ai-studio
wails dev

# Or build for production
wails build
```

### AI Project Manager
```bash
# Setup the web-based project management system
cd ai-pm
./scripts/setup.sh

# Use the CLI
./scripts/project-manager.sh list-tasks
```

## 📁 Repository Structure

This is organized as a monorepo for easier development:
- `ai-studio/` - Universal AI tools desktop application
- `ai-pm/` - Web-based project management system 
- `comfy-ui/` - Legacy ComfyUI components (deprecated)
- `shared/` - Common utilities and documentation

Each tool can be used independently and has its own documentation.

## 🔧 Development

See individual tool READMEs for specific setup instructions.

For general development utilities, see [`shared/`](shared/) directory.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]
