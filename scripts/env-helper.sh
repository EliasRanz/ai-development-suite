#!/bin/bash

# Simplified Environment Detection Helper
# Provides essential environment detection and configuration loading with minimal complexity

set -euo pipefail

# Constants
readonly DEFAULT_DEV_API="http://localhost:8001/api"
readonly DEFAULT_PROD_API="http://localhost:8000/api"

# Global state
_CONFIG_LOADED=false
AI_PM_API_URL=""
AI_PM_ENV=""

# Core utility functions
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

find_workspace_root() {
    local current_dir="$(pwd)"
    
    # Check current directory first
    [[ -d "ai-pm" ]] && { echo "$current_dir"; return 0; }
    
    # Search parent directories
    while [[ "$current_dir" != "/" ]]; do
        current_dir="$(dirname "$current_dir")"
        [[ -d "$current_dir/ai-pm" ]] && { echo "$current_dir"; return 0; }
    done
    
    return 1
}

# Load configuration from .env file
load_env_config() {
    [[ "$_CONFIG_LOADED" == "true" ]] && return 0
    
    local workspace_root
    if workspace_root=$(find_workspace_root); then
        local env_file="$workspace_root/ai-pm/.env"
        
        if [[ -f "$env_file" ]]; then
            # Load key variables only
            while IFS='=' read -r key value; do
                # Skip comments and empty lines
                [[ "$key" =~ ^[[:space:]]*# ]] && continue
                [[ -z "${key// }" ]] && continue
                
                # Remove quotes and export specific variables
                value="${value%\"}"
                value="${value#\"}"
                value="${value%\'}"
                value="${value#\'}"
                
                case "$key" in
                    AI_PM_API_URL|AI_PM_ENV|AI_PM_DEFAULT_ENV|AI_PM_API_TOKEN)
                        export "$key=$value"
                        ;;
                esac
            done < "$env_file"
        fi
    fi
    
    _CONFIG_LOADED=true
}

# Detect environment from running Docker services
detect_docker_env() {
    command_exists docker || return 1
    
    local workspace_root
    workspace_root=$(find_workspace_root) || return 1
    
    local compose_file="$workspace_root/ai-pm/docker-compose.yml"
    [[ -f "$compose_file" ]] || return 1
    
    local running_services
    running_services=$(docker compose -f "$compose_file" ps --services --filter "status=running" 2>/dev/null) || return 1
    
    if echo "$running_services" | grep -q "ai-pm-api-dev"; then
        echo "development"
    elif echo "$running_services" | grep -q "ai-pm-api"; then
        echo "production"
    else
        return 1
    fi
}

# Get API URL for environment
get_api_url() {
    local env="${1:-}"
    
    load_env_config
    
    # Use explicit API URL if set
    [[ -n "${AI_PM_API_URL:-}" ]] && { echo "$AI_PM_API_URL"; return 0; }
    
    # Determine environment
    if [[ -z "$env" ]]; then
        # Auto-detect from various sources
        if [[ -n "${AI_PM_ENV:-}" ]]; then
            env="$AI_PM_ENV"
        elif env=$(detect_docker_env); then
            # Use detected environment
            :
        else
            env="${AI_PM_DEFAULT_ENV:-production}"
        fi
    fi
    
    # Return appropriate URL
    case "$env" in
        dev|development) echo "$DEFAULT_DEV_API" ;;
        *) echo "$DEFAULT_PROD_API" ;;
    esac
}

# Test API connectivity
test_api() {
    local api_url="$1"
    local timeout="${2:-5}"
    
    load_env_config
    
    if command_exists curl; then
        local curl_args=("-s" "--max-time" "$timeout")
        
        # Add auth if configured
        [[ -n "${AI_PM_API_TOKEN:-}" ]] && curl_args+=("-H" "Authorization: Bearer $AI_PM_API_TOKEN")
        
        curl "${curl_args[@]}" "${api_url}/health" >/dev/null 2>&1
    else
        return 1
    fi
}

# Get environment info with validation
get_env_info() {
    local force_env="${1:-}"
    local interactive="${2:-true}"
    
    load_env_config
    
    local env_type api_url
    
    # Normalize forced environment
    case "$force_env" in
        dev|development) env_type="development" ;;
        prod|production) env_type="production" ;;
        "") 
            # Auto-detect
            if [[ -n "${AI_PM_ENV:-}" ]]; then
                env_type="$AI_PM_ENV"
            elif env_type=$(detect_docker_env); then
                # Use detected
                :
            else
                env_type="${AI_PM_DEFAULT_ENV:-production}"
            fi
            ;;
        *) env_type="$force_env" ;;
    esac
    
    api_url=$(get_api_url "$env_type")
    
    # Test connectivity
    if ! test_api "$api_url"; then
        # Only attempt auto-start for local services
        if [[ "$api_url" == "http://localhost:"* && "$interactive" == "true" ]]; then
            echo "🤔 Services not running. Start them? [y/N]" >&2
            read -r response
            if [[ "$response" =~ ^[Yy]$ ]]; then
                echo "🚀 Starting services..." >&2
                if [[ "$env_type" == "development" ]]; then
                    AI_PM_MODE=dev make ai-pm-start >/dev/null 2>&1
                else
                    make ai-pm-start >/dev/null 2>&1
                fi
                sleep 10
                test_api "$api_url" || { echo "ERROR: Services failed to start" >&2; return 1; }
            else
                echo "ERROR: Services not running" >&2
                return 1
            fi
        else
            echo "ERROR: API not reachable at $api_url" >&2
            return 1
        fi
    fi
    
    echo "${env_type}:${api_url}"
}

# Show current configuration
show_config() {
    load_env_config
    
    echo "Environment Configuration:"
    echo "  Default: ${AI_PM_DEFAULT_ENV:-production}"
    echo "  Current: ${AI_PM_ENV:-auto-detect}"
    echo "  API URL: ${AI_PM_API_URL:-auto-detect}"
    echo
    
    local dev_api prod_api
    dev_api=$(get_api_url "development")
    prod_api=$(get_api_url "production")
    
    echo "API Endpoints:"
    printf "  Development: %s " "$dev_api"
    test_api "$dev_api" 2 && echo "✓" || echo "✗"
    
    printf "  Production:  %s " "$prod_api"
    test_api "$prod_api" 2 && echo "✓" || echo "✗"
}

# Main function for direct execution
main() {
    case "${1:-}" in
        config|show-config) show_config ;;
        test) test_api "${2:-$(get_api_url)}" ;;
        detect) get_env_info "$2" "$3" ;;
        *) 
            echo "Usage: $0 {config|test|detect}"
            echo "  config           Show current configuration"
            echo "  test [url]       Test API connectivity"
            echo "  detect [env]     Detect/validate environment"
            ;;
    esac
}

# Run main if executed directly (not sourced)
if [[ "${BASH_SOURCE[0]}" == "${0}" ]]; then
    main "$@"
fi
