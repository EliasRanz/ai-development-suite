# AI Agent Security Instructions

This file contains instructions for AI agents working on this project regarding sensitive data handling.

## 🔐 Environment Configuration

### For Local Development:
1. Copy `.env.template` to `.env` 
2. Update all placeholder values with secure credentials
3. **NEVER commit the `.env` file**

### For AI Agent Sessions:
1. Use `.env.local.template` as a guide for configuration
2. Create a local `.env.local` file with your specific settings
3. Reference this file in your session for:
   - Database passwords
   - API tokens
   - File paths
   - Service URLs

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
./ai-pm/scripts/project-manager.sh list-tasks

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
