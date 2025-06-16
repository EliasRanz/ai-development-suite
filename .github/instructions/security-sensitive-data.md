# Sensitive Data Handling for AI Agents

## Critical Security Rule
**NEVER commit sensitive data to version control**

## Environment Configuration
**See `environment-setup.md` for detailed setup instructions**

### Quick Reference
- Use `.env.template` as the source of truth
- Copy to `.env` and customize with secure values
- **NEVER commit `.env` files**

## 🚨 Security Rules

### NEVER Include in Git:
- Real passwords or API tokens
- Personal filesystem paths (`/home/username`, `/Users/name`, etc.)
- Email addresses or personal information
- Database connection strings with credentials
- Private keys or certificates

### ALWAYS Use:
- Template files with placeholder values
- Environment variables for sensitive data
- Generic examples (`your-password-here`, `example@domain.com`)
- Relative paths instead of absolute paths

## 📝 AI Agent Session Setup

```bash
# 1. Copy templates
cp .env.template .env.local
cp .env.local.template .env.session

# 2. Edit with your actual values
# Replace all placeholder values with real configuration

# 3. Reference in AI session
# Use the values from .env.local for actual development commands
```

## 🔧 Development Commands

```bash
# Start AI Project Manager
cd ai-pm && ./scripts/setup.sh

# Use CLI (requires services running)
./scripts/project-manager.sh list-tasks

# Build AI Studio
cd ai-studio && make build
```

## 📋 File Status

### Tracked Files (Safe for GitHub):
- `.env.template` - Template with placeholders
- `.env.local.template` - AI agent configuration guide
- `ai-pm/docker-compose.yml` - Uses environment variables
- `ai-studio/wails.json` - Generic author information

### NOT Tracked (Contains Secrets):
- `.env` - Actual environment variables
- `.env.local` - AI agent local configuration
- `*.key`, `*.pem` - Private keys
- `*secret*`, `*password*` - Any files with credentials

This ensures the repository can be safely shared publicly while maintaining local development flexibility.
