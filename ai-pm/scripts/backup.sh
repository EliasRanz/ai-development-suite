#!/bin/bash
# AI PM Database Backup Script
# Creates timestamped backups of the entire data directory

set -euo pipefail

# Configuration
BACKUP_DIR="./backups"
DATA_DIR="./data"
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
BACKUP_NAME="ai-pm-backup-${TIMESTAMP}"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_info() { echo -e "${BLUE}ℹ${NC} $1"; }
print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

print_info "Starting backup of AI PM data..."

# Check if services are running
if docker-compose ps | grep -q "Up"; then
    print_warning "Services are running. Stopping for consistent backup..."
    docker-compose stop
    RESTART_SERVICES=true
else
    RESTART_SERVICES=false
fi

# Create the backup
print_info "Creating backup: $BACKUP_NAME"
tar -czf "$BACKUP_DIR/$BACKUP_NAME.tar.gz" -C . "$DATA_DIR"

# Restart services if they were running
if [ "$RESTART_SERVICES" = true ]; then
    print_info "Restarting services..."
    docker-compose up -d
fi

# Cleanup old backups (keep last 10)
print_info "Cleaning up old backups (keeping last 10)..."
cd "$BACKUP_DIR"
ls -t ai-pm-backup-*.tar.gz | tail -n +11 | xargs -r rm --

print_success "Backup completed: $BACKUP_DIR/$BACKUP_NAME.tar.gz"
print_info "Backup size: $(du -h "$BACKUP_DIR/$BACKUP_NAME.tar.gz" | cut -f1)"
