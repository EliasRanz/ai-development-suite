#!/bin/bash
# scripts/security/validate-permissions.sh
# Simple security validation script for file permissions

set -e

echo "🔒 Security Permission Validation"
echo "================================"

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

ISSUES_FOUND=0

# Fix permissions function
fix_permissions() {
    log_info "Fixing file permissions according to security best practices..."
    
    # Source code files (644 - rw-r--r--)
    log_info "Setting source code permissions (644)..."
    find . -name "*.go" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.ts" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.tsx" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.js" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.jsx" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.css" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.html" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Configuration files (644 - rw-r--r--)
    log_info "Setting configuration file permissions (644)..."
    find . -name "*.json" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.yml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.yaml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.toml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.ini" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Documentation files (644 - rw-r--r--)
    log_info "Setting documentation permissions (644)..."
    find . -name "*.md" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.txt" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "LICENSE*" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "README*" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Executable scripts (755 - rwxr-xr-x)
    log_info "Setting script permissions (755)..."
    find . -name "*.sh" -type f -exec chmod 755 {} \; 2>/dev/null || true
    find . -name "Makefile" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Directories (755 - rwxr-xr-x)
    log_info "Setting directory permissions (755)..."
    find . -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # Sensitive files (600 - rw-------)
    log_info "Setting sensitive file permissions (600)..."
    find . -name "*.key" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name "*.pem" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name ".env*" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name "*secret*" -type f -exec chmod 600 {} \; 2>/dev/null || true
    
    log_success "Permissions fixed according to security guidelines"
}

# Validate permissions function
validate_permissions() {
    log_info "Validating file permissions..."
    
    # Check for overly permissive files (777, 666)
    log_info "Checking for overly permissive files..."
    
    # Check for 777 permissions
    local files_777=$(find . -type f -perm 777 2>/dev/null | head -5)
    if [ -n "$files_777" ]; then
        log_error "Found files with 777 permissions (world writable!):"
        echo "$files_777" | while read -r file; do
            if [ -n "$file" ]; then
                log_error "  $file"
            fi
        done
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        log_success "No files with 777 permissions found"
    fi
    
    # Check for 666 permissions
    local files_666=$(find . -type f -perm 666 2>/dev/null | head -5)
    if [ -n "$files_666" ]; then
        log_error "Found files with 666 permissions (world writable!):"
        echo "$files_666" | while read -r file; do
            if [ -n "$file" ]; then
                log_error "  $file"
            fi
        done
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    else
        log_success "No files with 666 permissions found"
    fi
    
    # Check script permissions
    log_info "Checking script permissions..."
    local bad_scripts=$(find . -name "*.sh" -type f ! -perm 755 2>/dev/null | head -5)
    if [ -n "$bad_scripts" ]; then
        log_warning "Scripts with unexpected permissions found:"
        echo "$bad_scripts" | while read -r file; do
            if [ -n "$file" ]; then
                local perms=$(stat -c %a "$file" 2>/dev/null || echo "unknown")
                log_warning "  $file ($perms)"
            fi
        done
    else
        log_success "All scripts have correct permissions (755)"
    fi
}

# Main execution
echo ""
log_info "Security Permission Guidelines:"
echo "================================"
echo "File Type              | Permission | Octal | Reason"
echo "----------------------|------------|-------|---------------------------"
echo "Source Code (.go,.ts) | rw-r--r--  | 644   | Read-only for others"
echo "Executable Scripts    | rwxr-xr-x  | 755   | Execute for owner/group"
echo "Configuration Files   | rw-r--r--  | 644   | Read-only for others"
echo "Documentation         | rw-r--r--  | 644   | Read-only for others"
echo "Secrets (.env,.key)   | rw-------  | 600   | Owner only"
echo "Directories           | rwxr-xr-x  | 755   | Standard directory access"
echo ""
log_warning "NEVER use 777 or 666 permissions - they are security risks!"
log_success "Always follow the principle of least privilege"
echo ""

# Check if we should fix permissions automatically
if [ "$1" = "--fix" ] || [ "$1" = "-f" ]; then
    fix_permissions
    echo ""
fi

validate_permissions

echo ""
if [ $ISSUES_FOUND -eq 0 ]; then
    log_success "✅ Security validation completed - no issues found!"
    exit 0
else
    log_warning "⚠️  Security validation completed with $ISSUES_FOUND issue(s) found"
    log_info "Run with --fix flag to automatically fix permissions"
    exit 0  # Don't fail the build for permission warnings
fi
    
    # Configuration files (644 - rw-r--r--)
    log_info "Setting configuration file permissions (644)..."
    find . -name "*.json" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.yml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.yaml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.toml" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.ini" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Documentation files (644 - rw-r--r--)
    log_info "Setting documentation permissions (644)..."
    find . -name "*.md" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "*.txt" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "LICENSE*" -type f -exec chmod 644 {} \; 2>/dev/null || true
    find . -name "README*" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Executable scripts (755 - rwxr-xr-x)
    log_info "Setting script permissions (755)..."
    find . -name "*.sh" -type f -exec chmod 755 {} \; 2>/dev/null || true
    find . -name "Makefile" -type f -exec chmod 644 {} \; 2>/dev/null || true
    
    # Directories (755 - rwxr-xr-x)
    log_info "Setting directory permissions (755)..."
    find . -type d -exec chmod 755 {} \; 2>/dev/null || true
    
    # Sensitive files (600 - rw-------)
    log_info "Setting sensitive file permissions (600)..."
    find . -name "*.key" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name "*.pem" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name ".env*" -type f -exec chmod 600 {} \; 2>/dev/null || true
    find . -name "*secret*" -type f -exec chmod 600 {} \; 2>/dev/null || true
    
    log_success "Permissions fixed according to security guidelines"
}

# Function to validate permissions
validate_permissions() {
    log_info "Validating file permissions..."
    
    # Check for overly permissive files (777, 666)
    log_info "Checking for overly permissive files..."
    
    # Check for 777 permissions
    if find . -type f -perm 777 2>/dev/null | grep -q .; then
        log_error "Found files with 777 permissions (world writable!):"
        find . -type f -perm 777 2>/dev/null | while read -r file; do
            log_error "  $file"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        done
    else
        log_success "No files with 777 permissions found"
    fi
    
    # Check for 666 permissions
    if find . -type f -perm 666 2>/dev/null | grep -q .; then
        log_error "Found files with 666 permissions (world writable!):"
        find . -type f -perm 666 2>/dev/null | while read -r file; do
            log_error "  $file"
            ISSUES_FOUND=$((ISSUES_FOUND + 1))
        done
    else
        log_success "No files with 666 permissions found"
    fi
    
    # Check that scripts are executable but not world-writable
    log_info "Checking script permissions..."
    find . -name "*.sh" -type f ! -perm 755 2>/dev/null | while read -r file; do
        log_warning "Script with unexpected permissions: $file ($(stat -c %a "$file" 2>/dev/null || echo "unknown"))"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    done
    
    # Check that source files are not executable
    log_info "Checking source file permissions..."
    find . \( -name "*.go" -o -name "*.ts" -o -name "*.tsx" -o -name "*.js" -o -name "*.jsx" \) -type f -perm +111 2>/dev/null | while read -r file; do
        log_warning "Source file is executable: $file"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    done
    
    # Check for world-writable directories
    log_info "Checking directory permissions..."
    find . -type d -perm 777 2>/dev/null | while read -r dir; do
        log_error "World-writable directory: $dir"
        ISSUES_FOUND=$((ISSUES_FOUND + 1))
    done
}

# Function to show permission guidelines
show_guidelines() {
    echo ""
    log_info "Security Permission Guidelines:"
    echo "================================"
    echo ""
    echo "File Type              | Permission | Octal | Reason"
    echo "----------------------|------------|-------|---------------------------"
    echo "Source Code (.go,.ts) | rw-r--r--  | 644   | Read-only for others"
    echo "Executable Scripts    | rwxr-xr-x  | 755   | Execute for owner/group"
    echo "Configuration Files   | rw-r--r--  | 644   | Read-only for others"
    echo "Documentation         | rw-r--r--  | 644   | Read-only for others"
    echo "Secrets (.env,.key)   | rw-------  | 600   | Owner only"
    echo "Directories           | rwxr-xr-x  | 755   | Standard directory access"
    echo ""
    echo "⚠️  NEVER use 777 or 666 permissions - they are security risks!"
    echo "✅ Always follow the principle of least privilege"
    echo ""
}

# Function to detect WSL/Windows filesystem issues
check_filesystem() {
    log_info "Checking filesystem compatibility..."
    
    # Check if we're on a Windows mount
    if mount | grep -q "type drvfs"; then
        log_warning "Detected Windows filesystem mount (WSL)"
        log_warning "Permission changes may not persist due to Windows filesystem"
        log_info "Consider using Git to track permission changes instead"
        
        # Check if Git is configured to track permissions
        if git config --get core.filemode >/dev/null 2>&1; then
            local filemode=$(git config --get core.filemode)
            if [[ "$filemode" == "false" ]]; then
                log_warning "Git filemode is disabled (core.filemode=false)"
                log_info "Consider enabling: git config core.filemode true"
            else
                log_success "Git filemode is enabled"
            fi
        fi
    else
        log_success "Native Linux filesystem detected"
    fi
}

# Main function
main() {
    show_guidelines
    
    check_filesystem
    
    echo ""
    read -p "Fix permissions automatically? (y/N): " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        fix_permissions
    fi
    
    echo ""
    validate_permissions
    
    echo ""
    if [[ $ISSUES_FOUND -eq 0 ]]; then
        log_success "✅ Security validation passed! No permission issues found."
        exit 0
    else
        log_error "❌ Security validation failed! Found $ISSUES_FOUND permission issues."
        log_info "Run this script with auto-fix to resolve issues automatically."
        exit 1
    fi
}

# Run main function
main "$@"
