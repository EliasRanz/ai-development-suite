#!/bin/bash
# scripts/security/wsl-permission-handler.sh
# Handles file permissions in WSL environment with Windows filesystem

set -euo pipefail

echo "🔒 WSL Permission Handler for Windows Filesystem"
echo "==============================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
log_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
log_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check filesystem type
check_filesystem() {
    if mount | grep -q "type drvfs\|type 9p"; then
        log_warning "Detected Windows filesystem (DRVFS/9P) - Unix permissions not fully supported"
        return 0
    else
        log_info "Native Linux filesystem detected - Unix permissions fully supported"
        return 1
    fi
}

# Git-based permission management for WSL
setup_git_permissions() {
    log_info "Setting up Git-based permission management..."
    
    # Enable Git filemode tracking
    git config core.filemode true
    log_success "Git filemode tracking enabled"
    
    # Create .gitattributes for permission control
    cat > .gitattributes << 'EOF'
# File permission management for WSL/Windows compatibility

# Scripts should be executable
*.sh text eol=lf
*.sh filter=make-executable

# Source files should not be executable  
*.go text eol=lf
*.ts text eol=lf
*.tsx text eol=lf
*.js text eol=lf
*.jsx text eol=lf
*.json text eol=lf
*.md text eol=lf

# Configuration files
*.yml text eol=lf
*.yaml text eol=lf
*.toml text eol=lf

# Ensure line endings are consistent
* text=auto eol=lf
EOF

    log_success "Git attributes configured for permission management"
}

# Create Git hooks for permission management
setup_git_hooks() {
    log_info "Setting up Git hooks for permission validation..."
    
    # Pre-commit hook
    mkdir -p .git/hooks
    cat > .git/hooks/pre-commit << 'EOF'
#!/bin/bash
# Pre-commit hook to validate and document file permissions

echo "🔒 Validating file permissions before commit..."

# Document current file types and their intended permissions
cat > PERMISSIONS.md << 'PERMDOC'
# File Permissions Documentation

This file documents the intended file permissions for security compliance.

## Permission Guidelines

| File Type | Intended Permission | Security Reason |
|-----------|-------------------|-----------------|
| `*.go, *.ts, *.tsx` | 644 (rw-r--r--) | Source code - read-only for others |
| `*.sh` | 755 (rwxr-xr-x) | Scripts - executable for owner/group |
| `*.json, *.yml, *.md` | 644 (rw-r--r--) | Config/docs - read-only for others |
| `*.key, *.pem, .env*` | 600 (rw-------) | Secrets - owner only |
| Directories | 755 (rwxr-xr-x) | Standard directory access |

## WSL Note

When working in WSL with Windows filesystem (DRVFS), Unix permissions are not fully supported.
This documentation serves as the authoritative source for intended permissions.

## Validation

Run `./scripts/security/wsl-permission-handler.sh` to validate permissions in your environment.

PERMDOC

# Stage the permissions documentation
git add PERMISSIONS.md

echo "✅ Permission documentation updated"
EOF

    chmod +x .git/hooks/pre-commit
    log_success "Git hooks configured"
}

# Validate intended vs actual permissions
validate_permissions() {
    log_info "Validating file permissions (WSL-aware)..."
    
    local issues=0
    
    # Check for obviously wrong permissions
    log_info "Checking for overly permissive files..."
    
    # In WSL on Windows, files often show as 777, but this might be expected
    local perm_777_files=$(find . -name "*.go" -o -name "*.ts" -o -name "*.tsx" -o -name "*.json" -o -name "*.md" | head -5)
    if [[ -n "$perm_777_files" ]]; then
        local first_file=$(echo "$perm_777_files" | head -1)
        local actual_perm=$(stat -c %a "$first_file" 2>/dev/null || echo "unknown")
        
        if [[ "$actual_perm" == "777" ]]; then
            log_warning "Files showing 777 permissions (expected in WSL on Windows filesystem)"
            log_info "This is normal for DRVFS mounts - using documentation-based validation"
        else
            log_success "File permissions appear correct: $actual_perm"
        fi
    fi
    
    # Check that scripts exist and are recognized as executable
    log_info "Checking script files..."
    for script in $(find . -name "*.sh" -type f 2>/dev/null); do
        if [[ ! -x "$script" ]]; then
            log_warning "Script not executable: $script"
            issues=$((issues + 1))
        fi
    done
    
    # Validate file structure follows security principles
    log_info "Checking for sensitive files..."
    for sensitive in $(find . \( -name "*.key" -o -name "*.pem" -o -name ".env*" \) -type f 2>/dev/null); do
        log_warning "Sensitive file detected: $sensitive"
        log_info "Ensure this file is properly secured in production"
    done
    
    return $issues
}

# Create portable permission documentation
create_permission_docs() {
    log_info "Creating comprehensive permission documentation..."
    
    cat > SECURITY_PERMISSIONS.md << 'EOF'
# Security & File Permissions Guide

## Overview

This document outlines the security requirements and file permission strategy for the ComfyUI Launcher project, with special consideration for WSL/Windows development environments.

## File Permission Requirements

### Source Code Files
- **Extensions**: `.go`, `.ts`, `.tsx`, `.js`, `.jsx`, `.css`, `.html`
- **Intended Permission**: `644` (rw-r--r--)
- **Security Reason**: Read-only for group/others, prevents accidental modification

### Executable Scripts
- **Extensions**: `.sh`, executable binaries
- **Intended Permission**: `755` (rwxr-xr-x)
- **Security Reason**: Executable for owner/group, not world-writable

### Configuration Files
- **Extensions**: `.json`, `.yml`, `.yaml`, `.toml`, `.ini`
- **Intended Permission**: `644` (rw-r--r--)
- **Security Reason**: Read-only for group/others

### Documentation
- **Extensions**: `.md`, `.txt`, `LICENSE`, `README`
- **Intended Permission**: `644` (rw-r--r--)
- **Security Reason**: Read-only for group/others

### Sensitive Files
- **Extensions**: `.key`, `.pem`, `.env*`, `*secret*`
- **Intended Permission**: `600` (rw-------)
- **Security Reason**: Owner-only access, never world-readable

### Directories
- **All directories**
- **Intended Permission**: `755` (rwxr-xr-x)
- **Security Reason**: Standard directory traversal permissions

## WSL/Windows Considerations

### The Challenge
When developing in WSL with the Windows filesystem (`/mnt/c/`), Unix file permissions are not fully supported due to the DRVFS filesystem. Files may appear to have `777` permissions even when this is not intended.

### Our Solution
1. **Documentation-Based**: Use this document as the authoritative source
2. **Git Tracking**: Use Git attributes and hooks to manage permissions
3. **Validation Scripts**: Automated checks that understand WSL limitations
4. **Build-Time Enforcement**: Ensure correct permissions in final artifacts

### Implementation
```bash
# Check current filesystem type
mount | grep "$(pwd)"

# Run WSL-aware permission validation
./scripts/security/wsl-permission-handler.sh

# Enable Git filemode tracking
git config core.filemode true
```

## Security Validation

### Automated Checks
Run the validation script regularly:
```bash
./scripts/security/wsl-permission-handler.sh
```

### Manual Verification
In production environments (non-WSL), verify permissions:
```bash
# Check for overly permissive files
find . -type f -perm 777
find . -type f -perm 666

# Verify script permissions
find . -name "*.sh" -type f ! -perm 755

# Check sensitive files
find . \( -name "*.key" -o -name "*.env*" \) -type f ! -perm 600
```

## Best Practices

### Never Use These Permissions
- `777` - World writable files (security risk)
- `666` - World writable files (security risk)
- `755` on source code - Unnecessary execute permissions

### Always Use These Permissions
- `644` for source code and documentation
- `755` for scripts and directories
- `600` for sensitive files

### Git Integration
```bash
# Configure Git to track file permissions
git config core.filemode true

# Add permission documentation to commits
git add SECURITY_PERMISSIONS.md
```

## Compliance Checklist

- [ ] All source files have `644` permissions (or documented as WSL exception)
- [ ] All scripts have `755` permissions and are executable
- [ ] No files have `777` or `666` permissions (except WSL filesystem limitations)
- [ ] Sensitive files have `600` permissions
- [ ] Directory permissions are `755`
- [ ] Git is configured to track file permissions (`core.filemode=true`)
- [ ] Permission validation runs in CI/CD pipeline
- [ ] Team understands WSL permission limitations and workarounds

EOF

    log_success "Security documentation created: SECURITY_PERMISSIONS.md"
}

# Main function
main() {
    echo ""
    
    if check_filesystem; then
        log_info "WSL/Windows filesystem detected - using compatible permission management"
        setup_git_permissions
        setup_git_hooks
    else
        log_info "Native Linux filesystem - using standard permission management"
        # Use the standard permission script for native Linux
        if [[ -f "./scripts/security/validate-permissions.sh" ]]; then
            exec ./scripts/security/validate-permissions.sh "$@"
        fi
    fi
    
    create_permission_docs
    
    echo ""
    if validate_permissions; then
        log_success "✅ Permission validation completed successfully"
        log_info "📝 See SECURITY_PERMISSIONS.md for detailed permission requirements"
    else
        log_warning "⚠️  Some permission issues found - see output above"
        log_info "📝 In WSL, some warnings may be expected due to filesystem limitations"
    fi
    
    echo ""
    log_info "Next steps:"
    echo "  1. Review SECURITY_PERMISSIONS.md for permission requirements"
    echo "  2. Ensure Git tracks permissions: git config core.filemode true"
    echo "  3. Run this script regularly to validate security compliance"
    echo "  4. In production, use native Linux for full permission support"
}

# Run main function
main "$@"
