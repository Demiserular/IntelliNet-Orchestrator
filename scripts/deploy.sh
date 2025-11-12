#!/bin/bash

# IntelliNet Orchestrator Deployment Script
# This script sets up the environment and deploys the application

set -e  # Exit on error

echo "=========================================="
echo "IntelliNet Orchestrator Deployment"
echo "=========================================="

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print colored messages
print_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed. Please install Docker first."
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    print_error "Docker Compose is not installed. Please install Docker Compose first."
    exit 1
fi

# Determine environment (default to production)
ENVIRONMENT=${1:-production}
print_info "Deploying for environment: $ENVIRONMENT"

# Check if .env file exists
if [ ! -f .env ]; then
    print_warning ".env file not found. Creating from .env.example..."
    cp .env.example .env
    print_warning "Please update .env file with your configuration before proceeding."
    read -p "Press enter to continue after updating .env file..."
fi

# Validate required environment variables
print_info "Validating environment variables..."
source .env

if [ -z "$NEO4J_PASSWORD" ] || [ "$NEO4J_PASSWORD" == "your_neo4j_password_here" ]; then
    print_error "NEO4J_PASSWORD is not set or using default value. Please update .env file."
    exit 1
fi

if [ -z "$JWT_SECRET" ] || [ "$JWT_SECRET" == "your_jwt_secret_key_here_change_in_production" ]; then
    print_error "JWT_SECRET is not set or using default value. Please update .env file."
    exit 1
fi

print_info "Environment variables validated successfully."

# Create necessary directories
print_info "Creating data directories..."
mkdir -p data
mkdir -p logs

# Pull latest images
print_info "Pulling latest Docker images..."
docker-compose pull

# Build images
print_info "Building Docker images..."
docker-compose build --no-cache

# Stop existing containers
print_info "Stopping existing containers..."
docker-compose down

# Start services
print_info "Starting services..."
docker-compose up -d

# Wait for services to be healthy
print_info "Waiting for services to be healthy..."
sleep 10

# Check service health
print_info "Checking service health..."

# Check Neo4j
if docker-compose exec -T neo4j cypher-shell -u "$NEO4J_USER" -p "$NEO4J_PASSWORD" "RETURN 1" &> /dev/null; then
    print_info "✓ Neo4j is healthy"
else
    print_error "✗ Neo4j is not responding"
fi

# Check Backend
if curl -f http://localhost:8000/health &> /dev/null; then
    print_info "✓ Backend is healthy"
else
    print_warning "✗ Backend health check failed (may still be starting)"
fi

# Check Frontend
if curl -f http://localhost/health &> /dev/null; then
    print_info "✓ Frontend is healthy"
else
    print_warning "✗ Frontend health check failed (may still be starting)"
fi

# Show running containers
print_info "Running containers:"
docker-compose ps

echo ""
echo "=========================================="
print_info "Deployment completed!"
echo "=========================================="
echo ""
echo "Access the application at:"
echo "  Frontend: http://localhost"
echo "  Backend API: http://localhost:8000"
echo "  Neo4j Browser: http://localhost:7474"
echo ""
echo "To view logs: docker-compose logs -f"
echo "To stop services: docker-compose down"
echo ""
