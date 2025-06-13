# AI Studio

A universal desktop application for managing and working with AI development tools.

> **🤖 AI-Assisted Development**: This application is developed using human-AI collaboration, with AI assistance in code generation, architecture design, and documentation.

## Features

- 🎨 **Universal AI Tool Management** - Manage ComfyUI, Automatic1111, Ollama, LM Studio, and more
- 🖥️ **Native Desktop App** - Built with Wails (Go + React) for cross-platform support
- 📊 **Real-time Monitoring** - Monitor status and logs of all your AI tools
- ⚙️ **Configuration Management** - Easy setup and configuration of AI tool instances
- 🔄 **Service Management** - Start, stop, and restart AI services with one click
- 📱 **Modern UI** - Clean, responsive React interface

## Supported AI Tools

- **ComfyUI** - Node-based stable diffusion GUI
- **Automatic1111** - Web UI for Stable Diffusion
- **Ollama** - Local language model runner
- **LM Studio** - Local language model interface
- **Text Generation WebUI** - Advanced text generation interface
- **LocalAI** - Self-hosted OpenAI-compatible API

## Quick Start

### Prerequisites
- Go 1.22+
- Node.js 18+
- Wails v2

### Development

```bash
# Install Wails
go install github.com/wailsapp/wails/v2/cmd/wails@latest

# Install dependencies
cd ai-studio
wails build

# Run in development mode
wails dev
```

### Building

```bash
# Build for current platform
wails build

# Build for all platforms
wails build -platform=darwin/amd64,darwin/arm64,linux/amd64,windows/amd64
```

## Architecture

### Backend (Go)
- **Domain Layer** - Core entities and business logic
- **Application Layer** - Use cases and application services
- **Infrastructure Layer** - External integrations and repositories
- **Interface Layer** - Wails bindings and API

### Frontend (React + TypeScript)
- **Modern React** with hooks and functional components
- **TypeScript** for type safety
- **Vite** for fast development and building
- **Responsive Design** for different screen sizes

## Project Structure

```
ai-studio/
├── backend/                 # Go backend
│   ├── application/        # Application layer (use cases)
│   ├── domain/            # Domain layer (entities, repositories)
│   ├── infrastructure/    # Infrastructure layer (implementations)
│   └── interfaces/        # Interface layer (Wails bindings)
├── frontend/              # React frontend
│   ├── src/              # Source code
│   └── dist/             # Built assets
├── main.go               # Application entry point
├── go.mod                # Go dependencies
└── wails.json            # Wails configuration
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests
5. Submit a pull request

## License

[Your License Here]
