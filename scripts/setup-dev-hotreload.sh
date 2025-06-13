#!/bin/bash

# AI Project Manager Development Setup Script
# Sets up hot reload environment for rapid development

set -e

echo "🚀 Setting up AI Project Manager Development Environment"
echo "======================================================"

# Check if Docker is running
if ! docker ps >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop first."
    exit 1
fi

# Check if we're in the right directory
if [ ! -f "ai-pm/docker-compose.yml" ]; then
    echo "❌ Please run this script from the ai-tools root directory"
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Found AI PM configuration"

# Create development network if it doesn't exist
echo "📡 Setting up Docker network..."
docker network create ai-pm_default 2>/dev/null || echo "Network already exists"

# Build development images
echo "🔨 Building development Docker images..."
cd ai-pm
docker-compose -f docker-compose.yml -f docker-compose.dev.yml build ai-pm-api-dev ai-pm-ui-dev

echo "🎉 Development environment setup complete!"
echo ""
echo "Quick Start Commands:"
echo "==================="
echo "make ai-pm-dev-start     # Start with hot reload"
echo "make ai-pm-dev-backend   # Backend only"
echo "make ai-pm-dev-frontend  # Frontend only" 
echo "make ai-pm-dev-logs      # View logs"
echo "make ai-pm-dev-stop      # Stop dev services"
echo ""
echo "🔥 Hot Reload Features:"
echo "- Backend: Go files auto-rebuild with Air"
echo "- Frontend: React HMR with Vite"
echo "- No more manual Docker rebuilds!"
echo ""
echo "Ready to start development? Run: make ai-pm-dev-start"
