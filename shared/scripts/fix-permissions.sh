#!/bin/bash
# Simple permission fix script

echo "🔒 Fixing file permissions..."

# Set proper permissions for source files
find . -name "*.go" -type f -exec chmod 644 {} \; 2>/dev/null || true
find . -name "*.ts" -type f -exec chmod 644 {} \; 2>/dev/null || true
find . -name "*.tsx" -type f -exec chmod 644 {} \; 2>/dev/null || true
find . -name "*.json" -type f -exec chmod 644 {} \; 2>/dev/null || true
find . -name "*.md" -type f -exec chmod 644 {} \; 2>/dev/null || true

# Set proper permissions for scripts (755 instead of 777)
find . -name "*.sh" -type f -exec chmod 755 {} \; 2>/dev/null || true

echo "✅ Permissions fixed!"
echo ""
echo "Current script permissions:"
find . -name "*.sh" -type f -exec ls -la {} \;
