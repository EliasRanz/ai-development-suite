# Local AI Launcher

Universal launcher for local AI tools with cross-platform support and WSL compatibility.

**Supports**: ComfyUI, Automatic1111, Ollama, LM Studio, Text Generation WebUI, and more.

## Quick Start

```bash
# Setup (WSL recommended for Windows)
./scripts/wsl/setup-dev.sh

# Development
make dev

# Build
make build
```

## Status

- 🔄 **Current:** Migrating from ComfyUI-specific to universal AI tool launcher
- ✅ Architecture decided, docs cleaned
- ⏳ Backend implementation, frontend migration

## Key Commands

```bash
make dev        # Start development server
make test       # Run all tests
make build      # Production build
make help       # Show all commands
```

**Performance Target:** 5x faster startup, 3x less memory than current implementation.

**Docs:** [WSL Setup](docs/wsl-setup.md) | [Migration](docs/migration.md) | [ADRs](ADRs/)
