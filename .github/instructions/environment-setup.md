# Environment Configuration Guidelines

This document outlines the standardized approach to environment configuration across the AI tools suite.

## File Structure

### Primary Template
- **`.env.template`** - The single source of truth for environment configuration
  - Contains comprehensive settings for all tools
  - Includes detailed documentation and security notes
  - Should be the only root-level environment template

### Service-Specific Templates
- **`comfy-ui/launcher/.env.example`** - ComfyUI-specific settings
- Service directories may have their own `.env.example` files for tool-specific settings

### Ignored Files
The following environment files are automatically ignored by git:
- `.env`
- `.env.local`
- `.env.production`
- `.env.development`
- `.env.staging`
- `*.env`

## Setup Process

### 1. Initial Configuration
```bash
# Copy the primary template
cp .env.template .env

# For service-specific tools (e.g., ComfyUI)
cp comfy-ui/launcher/.env.example comfy-ui/launcher/.env
```

### 2. Customize Settings

#### Required Changes
- **Database passwords**: Update all `AI_PM_DB_PASSWORD` and storage passwords
- **Secret keys**: Generate secure keys using `openssl rand -base64 32`
- **Paths**: Update `PROJECT_ROOT` and related paths for your system
- **API tokens**: Set actual API tokens for services you use

#### Security Requirements
- Use strong, unique passwords (minimum 16 characters)
- Generate cryptographically secure secret keys
- Never use default passwords in production
- Regularly rotate credentials

### 3. Validation
```bash
# Check that .env is properly ignored
git status

# Verify no sensitive data is tracked
git check-ignore .env
```

## Configuration Sections

### AI Project Manager
Core project management system configuration:
- Database connection settings
- API endpoints and authentication
- Storage and backup settings

### AI Studio
Desktop application configuration:
- Data and configuration directories
- Logging levels and debug settings
- API endpoints for integrations

### Development
Development-specific settings:
- Environment modes (development/production)
- Debug flags and logging
- Local path overrides

## Best Practices

### ✅ Do
- Use the primary `.env.template` as the authoritative source
- Document environment variables with clear comments
- Group related variables into logical sections
- Include setup instructions and security notes
- Use descriptive variable names with consistent prefixes
- Validate that `.env` files are properly ignored by git

### ❌ Don't
- Create multiple root-level environment templates
- Commit actual `.env` files to version control
- Use default passwords in production
- Store sensitive data in template files
- Create redundant or overlapping templates

## Anti-Patterns

### Multiple Templates
**Problem**: Having multiple root-level templates (`.env.example`, `.env.template`, `.env.local.template`)
**Solution**: Use a single comprehensive `.env.template` file

### Scattered Configuration
**Problem**: Environment variables spread across multiple undocumented files
**Solution**: Centralize common settings in the main template, use service-specific files only when necessary

### Weak Security Defaults
**Problem**: Using weak default passwords or secrets in templates
**Solution**: Use placeholder values that clearly indicate they must be changed

## Maintenance

### Adding New Variables
1. Add to the appropriate section in `.env.template`
2. Include descriptive comments
3. Use secure placeholder values
4. Update this documentation if needed

### Removing Variables
1. Remove from `.env.template`
2. Check for usage across all tools
3. Update documentation
4. Consider backward compatibility

### Regular Audits
- Review environment templates quarterly
- Ensure all sensitive defaults are placeholders
- Verify documentation is current
- Check for unused or obsolete variables

## Integration with Tools

### Scripts
- Main CLI script: `scripts/project-manager.sh`
- Sources environment variables automatically
- Validates required settings before execution

### Docker Compose
- Services use environment variables from `.env`
- Override files can provide service-specific defaults
- Production configurations should use separate mechanisms

### Development Tools
- VS Code tasks can reference environment variables
- Build scripts should validate environment setup
- Testing should use isolated environment configuration

---

This standardized approach ensures consistent, secure, and maintainable environment configuration across the entire AI tools suite.
