# Contributing to AI Development Suite

Thank you for your interest in contributing to the AI Development Suite! This project embraces AI-assisted development and values clean, maintainable code.

## 🤖 AI-Assisted Development

This project is built with AI assistance and we encourage contributors to leverage AI tools for:
- Code generation and refactoring
- Documentation writing
- Test creation
- Code review and optimization

Please document any significant AI assistance in your PR descriptions.

## 🚀 Getting Started

1. **Fork the repository**
2. **Clone your fork:**
   ```bash
   git clone https://github.com/your-username/ai-development-suite.git
   cd ai-development-suite
   ```
3. **Set up your development environment** (see individual tool READMEs)
4. **Create a feature branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

## 📝 Pull Request Process

### 1. PR Requirements
- **Clear title**: Describe what the PR accomplishes
- **Detailed description**: Explain the changes and why they're needed
- **Link issues**: Reference any related issues with `Fixes #123` or `Closes #123`
- **Test coverage**: Include tests for new functionality
- **Documentation**: Update relevant documentation

### 2. Merge Strategy
**This repository uses SQUASH MERGING only.** Your PR will be squashed into a single commit when merged.

**Why squash merging?**
- Clean, linear git history
- Each feature becomes one logical commit
- Easy to revert if needed
- Clear blame/bisect for debugging

**PR Title Guidelines:**
Since your PR title becomes the commit message, make it:
- Descriptive and concise
- Start with a verb (Add, Fix, Update, Remove, etc.)
- Examples:
  - ✅ `Add user authentication to AI Studio`
  - ✅ `Fix memory leak in ComfyUI launcher`
  - ✅ `Update dependency management documentation`
  - ❌ `changes`
  - ❌ `fix stuff`

## 🏗️ Project Structure

This is a monorepo with multiple tools:

```
ai-studio/          # Main AI development interface
ai-pm/             # AI-powered project management
comfy-ui/          # ComfyUI integration and launcher
shared/            # Shared utilities and configurations
.github/           # GitHub workflows and templates
```

## 🧪 Testing

- **Run tests before submitting:**
  ```bash
  # For Go components
  go test ./...
  
  # For frontend components
  npm test
  ```
- **Add tests** for new features
- **Update tests** when modifying existing functionality

## 📚 Documentation

- Keep documentation **focused and valuable**
- Avoid documentation bloat
- Update relevant READMEs when adding features
- Follow the documentation policy in `.github/instructions/documentation.md`

## 🔒 Security

- **Never commit secrets** or personal information
- Use `.env.example` templates for configuration
- Follow security guidelines in `.github/instructions/security.md`
- Report security issues privately (see SECURITY.md)

## 💾 Code Standards

### General
- **Clean, readable code** over clever code
- **Meaningful variable and function names**
- **Comments for complex logic**
- **Consistent formatting** (use project linters/formatters)

### Go Code
- Follow standard Go conventions
- Use `gofmt` and `golint`
- Include error handling
- Write tests for public functions

### TypeScript/React
- Use TypeScript strictly
- Follow React best practices
- Use provided ESLint configuration
- Include prop types and interfaces

### Python
- Follow PEP 8
- Use type hints where appropriate
- Include docstrings for functions/classes

## 🐛 Bug Reports

When reporting bugs, include:
- **Clear description** of the issue
- **Steps to reproduce** the problem
- **Expected vs actual behavior**
- **Environment details** (OS, versions, etc.)
- **Screenshots/logs** if relevant

## 💡 Feature Requests

For new features:
- **Check existing issues** first
- **Describe the use case** and problem solved
- **Propose a solution** if you have one
- **Consider backwards compatibility**

## 📞 Getting Help

- **Check the documentation** first
- **Search existing issues** for similar problems
- **Create an issue** with detailed information
- **Be patient and respectful** in all interactions

## 🎯 AI Development Philosophy

This project believes in:
- **Transparency** in AI-assisted development
- **Human oversight** of AI-generated code
- **Quality over speed**
- **Learning and improvement** through AI collaboration

## 📄 License

By contributing, you agree that your contributions will be licensed under the same license as this project.

---

Thank you for contributing to the AI Development Suite! Together, we're building the future of AI-assisted development. 🚀
