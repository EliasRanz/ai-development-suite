#!/bin/bash

# Plane Project Management Setup for AI Agents
echo "Setting up Plane project management..."

# Check if .env exists, if not create from example
if [ ! -f .env ]; then
    echo "Creating .env from template..."
    cp .env.example .env
    
    # Generate secure passwords
    DB_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    MINIO_PASSWORD=$(openssl rand -base64 32 | tr -d "=+/" | cut -c1-25)
    SECRET_KEY=$(openssl rand -base64 64 | tr -d "=+/" | cut -c1-50)
    
    # Update .env with generated passwords
    sed -i "s/change-this-password/$DB_PASSWORD/g" .env
    sed -i "s/change-this-minio-password/$MINIO_PASSWORD/g" .env
    sed -i "s|change-this-secret-key-to-something-secure|$SECRET_KEY|g" .env
    
    echo "Generated secure passwords in .env file"
fi

# Start Plane services
echo "Starting Plane services..."
docker compose -f docker-compose.plane.yml up -d

# Wait for services to be ready
echo "Waiting for services to initialize..."
sleep 30

# Check if API is responding
echo "Checking API health..."
curl -f http://localhost:8000/api/health/ || {
    echo "API not ready yet, waiting longer..."
    sleep 30
}

echo "Plane setup complete!"
echo "Access Plane at: http://localhost:3000"
echo "API endpoint: http://localhost:8000"
echo ""
echo "Next steps:"
echo "1. Open http://localhost:3000 in your browser"
echo "2. Create admin account"
echo "3. Create workspace and project"
echo "4. Generate API token in Settings > API Tokens"
echo "5. Update .env with PLANE_API_TOKEN=your-token"
