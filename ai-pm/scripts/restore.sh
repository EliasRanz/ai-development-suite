#!/bin/bash
# AI PM Database Restore Script
# Restores from a backup archive

set -euo pipefail

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

# Check if backup file is provided
if [ $# -eq 0 ]; then
    print_error "Usage: $0 <backup-file.tar.gz>"
    echo "Available backups:"
    ls -la ./backups/*.tar.gz 2>/dev/null || echo "No backups found"
    exit 1
fi

BACKUP_FILE="$1"

# Check if backup file exists
if [ ! -f "$BACKUP_FILE" ]; then
    print_error "Backup file not found: $BACKUP_FILE"
    exit 1
fi

print_warning "This will completely replace the current data directory!"
print_warning "Current data will be backed up before restore."
read -p "Are you sure you want to continue? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "Restore cancelled"
    exit 0
fi

# Stop services if running
if docker-compose ps | grep -q "Up"; then
    print_info "Stopping services..."
    docker-compose stop
fi

# Backup current data if it exists
if [ -d "./data" ]; then
    CURRENT_BACKUP="./backups/pre-restore-backup-$(date +"%Y%m%d_%H%M%S").tar.gz"
    print_info "Backing up current data to: $CURRENT_BACKUP"
    mkdir -p ./backups
    tar -czf "$CURRENT_BACKUP" -C . data
fi

# Remove current data directory
print_info "Removing current data directory..."
rm -rf ./data

# Extract backup
print_info "Extracting backup: $BACKUP_FILE"
tar -xzf "$BACKUP_FILE" -C .

# Set proper permissions
print_info "Setting proper permissions..."
chmod -R 755 ./data

print_success "Restore completed from: $BACKUP_FILE"
print_info "You can now start services with: docker-compose up -d"
