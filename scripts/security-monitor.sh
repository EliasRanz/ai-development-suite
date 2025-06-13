#!/bin/bash
# Security Alert Monitor
# Simple script to check GitHub security alerts and create tasks

set -euo pipefail

# Configuration
REPO="EliasRanz/ai-development-suite"
SCRIPT_DIR="$(dirname "$0")"
PROJECT_MANAGER="$SCRIPT_DIR/project-manager.sh"

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_success() { echo -e "${GREEN}✓${NC} $1"; }
print_error() { echo -e "${RED}✗${NC} $1" >&2; }
print_warning() { echo -e "${YELLOW}⚠${NC} $1"; }
print_info() { echo -e "${BLUE}ℹ${NC} $1"; }

# Check if required tools are available
check_deps() {
    for cmd in gh jq; do
        if ! command -v "$cmd" >/dev/null 2>&1; then
            print_error "$cmd is required but not installed"
            exit 1
        fi
    done
    
    if [ ! -f "$PROJECT_MANAGER" ]; then
        print_error "Project manager script not found: $PROJECT_MANAGER"
        exit 1
    fi
}

# Show security summary
show_summary() {
    print_info "Security Alert Summary for $REPO"
    echo "=================================="
    
    # Get alert counts correctly
    local total_alerts=$(gh api "repos/$REPO/dependabot/alerts" --jq 'length' 2>/dev/null || echo "0")
    local open_alerts=$(gh api "repos/$REPO/dependabot/alerts" --jq '[.[] | select(.state == "open")] | length' 2>/dev/null || echo "0")
    local fixed_alerts=$(gh api "repos/$REPO/dependabot/alerts" --jq '[.[] | select(.state == "fixed")] | length' 2>/dev/null || echo "0")
    
    echo "📊 Alert Status:"
    echo "  🔓 Open: $open_alerts"
    echo "  ✅ Fixed: $fixed_alerts"
    echo "  📋 Total: $total_alerts"
    
    if [ "$open_alerts" -gt 0 ]; then
        echo ""
        echo "🚨 Open Alerts:"
        gh api "repos/$REPO/dependabot/alerts" --jq '.[] | select(.state == "open") | "  Alert #\(.number): \(.security_advisory.severity) - \(.dependency.package.name) (\(.dependency.manifest_path))"' 2>/dev/null || echo "  Could not fetch alert details"
    else
        echo ""
        print_success "No open security alerts! 🎉"
    fi
    
    echo ""
    print_info "View details: https://github.com/$REPO/security/dependabot"
}

# List open alerts
list_alerts() {
    print_info "Open Security Alerts:"
    
    local alerts=$(gh api "repos/$REPO/dependabot/alerts" 2>/dev/null || echo "[]")
    
    if [ "$alerts" = "[]" ] || [ -z "$alerts" ]; then
        print_success "No security alerts found!"
        return 0
    fi
    
    # List open alerts in simple format
    echo "$alerts" | jq -r '.[] | select(.state == "open") | "Alert #\(.number): \(.security_advisory.severity) - \(.dependency.package.name)"' 2>/dev/null || echo "Failed to parse alerts"
}

# Create tasks for open alerts
create_tasks() {
    local project_id="${1:-1}"
    
    print_info "Creating tasks for open security alerts..."
    
    # Check if project manager is working
    if ! "$PROJECT_MANAGER" setup >/dev/null 2>&1; then
        print_error "Project Manager API not available. Start with: make ai-pm-start"
        return 1
    fi
    
    local alerts=$(gh api "repos/$REPO/dependabot/alerts" 2>/dev/null || echo "[]")
    
    if [ "$alerts" = "[]" ] || [ -z "$alerts" ]; then
        print_success "No security alerts to process"
        return 0
    fi
    
    local count=0
    
    # Get all open alerts first
    local open_alerts=$(echo "$alerts" | jq -c '.[] | select(.state == "open")' 2>/dev/null)
    
    if [ -z "$open_alerts" ]; then
        print_success "No open security alerts to process"
        return 0
    fi
    
    # Process each open alert
    while IFS= read -r alert; do
        if [ -n "$alert" ]; then
            local number=$(echo "$alert" | jq -r '.number')
            local severity=$(echo "$alert" | jq -r '.security_advisory.severity')
            local package=$(echo "$alert" | jq -r '.dependency.package.name')
            local summary=$(echo "$alert" | jq -r '.security_advisory.summary')
            local manifest=$(echo "$alert" | jq -r '.dependency.manifest_path')
            
            # Create task title and description
            local title="Security Alert #$number: Fix $severity vulnerability in $package"
            local description="🔒 Security vulnerability detected by Dependabot

Package: $package
Severity: $severity
Manifest: $manifest
Summary: $summary

Action required: Update $package to resolve this vulnerability.
View alert: https://github.com/$REPO/security/dependabot/$number"
            
            # Map severity to priority
            local priority="medium"
            case "$severity" in
                "critical") priority="urgent" ;;
                "high") priority="high" ;;
                "medium") priority="medium" ;;
                "low") priority="low" ;;
            esac
            
            # Check if task already exists
            local existing_check=$(echo "$("$PROJECT_MANAGER" list-tasks 2>/dev/null)" | grep "Security Alert #$number:" | wc -l)
            if [ "$existing_check" -gt 0 ]; then
                print_warning "Task already exists for Alert #$number"
            else
                # Create the task
                if "$PROJECT_MANAGER" add-task -p "$project_id" -t "$title" -d "$description" -r "$priority" >/dev/null 2>&1; then
                    print_success "Created task for Alert #$number ($severity - $package)"
                    ((count++))
                else
                    print_error "Failed to create task for Alert #$number"
                fi
            fi
        fi
    done <<< "$open_alerts"
    
    print_success "Created $count new security tasks"
}

# Main monitoring routine
monitor() {
    local project_id="${1:-1}"
    
    print_info "🔍 Running security monitoring routine..."
    echo ""
    
    show_summary
    echo ""
    
    create_tasks "$project_id"
    echo ""
    
    print_info "Next steps:"
    echo "1. Review tasks: $PROJECT_MANAGER list-tasks"
    echo "2. Update vulnerable packages"
    echo "3. Run this again: $0 monitor"
}

# Show help
show_help() {
    echo -e "${BLUE}Security Alert Monitor v1.0${NC}"
    echo "Monitor GitHub Dependabot security alerts and create tasks"
    echo ""
    echo "Usage: $0 <command> [project_id]"
    echo ""
    echo "Commands:"
    echo "  summary         Show security alert summary"
    echo "  list           List open security alerts"
    echo "  create-tasks   Create tasks for open alerts"
    echo "  monitor        Run full monitoring (summary + create tasks)"
    echo "  help           Show this help"
    echo ""
    echo "Examples:"
    echo "  $0 summary"
    echo "  $0 create-tasks 1"
    echo "  $0 monitor"
}

# Main function
main() {
    local command="${1:-help}"
    
    case "$command" in
        "summary") 
            check_deps
            show_summary 
            ;;
        "list")
            check_deps
            list_alerts
            ;;
        "create-tasks")
            check_deps
            create_tasks "${2:-1}"
            ;;
        "monitor")
            check_deps
            monitor "${2:-1}"
            ;;
        "help"|"")
            show_help
            ;;
        *)
            print_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run if executed directly
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
