#!/bin/bash

# AI Project Manager Setup Script
# Sets up the AI-driven project management system

set -e

echo "🤖 AI Project Manager Setup"
echo "============================"

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker Desktop and try again."
    exit 1
fi

echo "✅ Docker is running"

# Create .env file if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file with secure credentials..."
    
    # Generate secure random passwords
    AI_PM_DB_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-25)
    AI_PM_STORAGE_PASSWORD=$(openssl rand -base64 20 | tr -d "=+/" | cut -c1-25)
    AI_PM_SECRET_KEY=$(openssl rand -base64 32)
    
    cat > .env << EOF
# Environment variables for development
# Copy to .env and update with your actual values

# AI Project Manager Configuration
AI_PM_URL=http://localhost:8000
AI_PM_API_TOKEN=your-api-token-here
AI_PM_WORKSPACE_ID=your-workspace-id
AI_PM_PROJECT_ID=your-project-id

# AI Project Manager Infrastructure (change these passwords!)
AI_PM_DB_USER=aipm
AI_PM_DB_PASSWORD=${AI_PM_DB_PASSWORD}
AI_PM_DB_NAME=ai_project_manager
AI_PM_STORAGE_USER=aipm
AI_PM_STORAGE_PASSWORD=${AI_PM_STORAGE_PASSWORD}
AI_PM_SECRET_KEY=${AI_PM_SECRET_KEY}

# Development
NODE_ENV=development
GO_ENV=development
EOF
    
    echo "✅ Created .env file with secure credentials"
else
    echo "✅ .env file already exists"
fi

# Start the services
echo "🚀 Starting AI Project Manager services..."
docker compose -f docker-compose.ai-pm.yml up -d

echo ""
echo "✅ AI Project Manager setup complete!"
echo ""
echo "📋 Next steps:"
echo "  1. Wait for services to start (may take a few minutes)"
echo "  2. Check status: make ai-pm-status"
echo "  3. Access web interface: http://localhost:3000"
echo "  4. Access API: http://localhost:8000"
echo "  5. Access MinIO console: http://localhost:9090"
echo ""
echo "🔧 Useful commands:"
echo "  - Check logs: docker compose -f docker-compose.ai-pm.yml logs"
echo "  - Stop services: make ai-pm-stop"
echo "  - Restart services: make ai-pm-start"
