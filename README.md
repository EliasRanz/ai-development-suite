# AI Development Tools

A collection of AI development tools designed to streamline workflows and enhance productivity.

## 🛠️ Tools Included

# AI Development Tools

A comprehensive suite of AI development tools designed to streamline workflows and enhance productivity.

> **🤖 AI-Assisted Development**: This project is actively developed with AI assistance (GitHub Copilot, Claude, and other AI tools). The commit history, code architecture, and documentation reflect collaborative human-AI development practices.

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

## 🤖 AI-Assisted Development Methodology

This project demonstrates modern AI-assisted software development practices:

### Human-AI Collaboration Model
- **Strategic Direction**: Human-defined requirements and architecture decisions
- **Implementation**: AI-assisted code generation, refactoring, and documentation
- **Quality Assurance**: Human review of AI-generated code and architectural choices
- **Continuous Improvement**: Iterative development with AI suggestions and human validation

### AI Contributions in This Project
- **Code Architecture**: Clean architecture patterns implemented with AI assistance
- **Documentation**: README files, ADRs, and inline documentation largely AI-generated
- **Commit Messages**: Detailed, structured commit messages created with AI assistance
- **Testing Strategy**: Test structures and patterns designed collaboratively
- **Repository Organization**: Monorepo structure and file organization optimized through AI consultation

### Transparency
The commit history provides a transparent view of the human-AI development process, including:
- Major architectural decisions made through AI consultation
- Code refactoring and optimization performed with AI assistance
- Documentation improvements and standardization via AI assistance
- Security audits and best practice implementation guided by AI

This serves as a real-world example of how AI can accelerate development while maintaining code quality and architectural integrity.

## 🔧 Development

See individual tool READMEs for specific setup instructions.

For general development utilities, see [`shared/`](shared/) directory.

## Contributing

This project welcomes contributions and demonstrates AI-assisted development practices.

### Development Approach
- **Human-AI Collaboration**: Features and architecture are designed through human guidance with AI implementation assistance
- **AI-Generated Content**: Large portions of code, documentation, and commit messages are AI-generated with human review
- **Transparent Process**: Commit history reflects the collaborative nature of human-AI development

### How to Contribute
1. Fork the repository
2. Create a feature branch
3. Make your changes (AI assistance encouraged!)
4. Run tests and ensure code quality
5. Submit a pull request with clear description of changes

**Note**: When using AI assistance, please mention it in your commit messages or PR description for transparency.

---

**Note**: This project serves as an example of modern AI-assisted software development, where human creativity and AI capabilities combine to create robust, well-documented software.
