# IntelliNet Orchestrator Deployment Script (PowerShell)
# This script sets up the environment and deploys the application

param(
    [string]$Environment = "production"
)

$ErrorActionPreference = "Stop"

Write-Host "==========================================" -ForegroundColor Cyan
Write-Host "IntelliNet Orchestrator Deployment" -ForegroundColor Cyan
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""

function Write-Info {
    param([string]$Message)
    Write-Host "[INFO] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WARNING] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[ERROR] $Message" -ForegroundColor Red
}

# Check if Docker is installed
try {
    docker --version | Out-Null
} catch {
    Write-Error "Docker is not installed. Please install Docker Desktop first."
    exit 1
}

# Check if Docker Compose is available
try {
    docker-compose --version | Out-Null
    $composeCmd = "docker-compose"
} catch {
    try {
        docker compose version | Out-Null
        $composeCmd = "docker compose"
    } catch {
        Write-Error "Docker Compose is not available. Please install Docker Compose."
        exit 1
    }
}

Write-Info "Deploying for environment: $Environment"

# Check if .env file exists
if (-not (Test-Path .env)) {
    Write-Warning ".env file not found. Creating from .env.example..."
    Copy-Item .env.example .env
    Write-Warning "Please update .env file with your configuration before proceeding."
    Read-Host "Press Enter to continue after updating .env file"
}

# Load and validate environment variables
Write-Info "Validating environment variables..."
Get-Content .env | ForEach-Object {
    if ($_ -match '^([^=]+)=(.*)$') {
        $name = $matches[1]
        $value = $matches[2]
        [Environment]::SetEnvironmentVariable($name, $value, "Process")
    }
}

$neo4jPassword = [Environment]::GetEnvironmentVariable("NEO4J_PASSWORD", "Process")
$jwtSecret = [Environment]::GetEnvironmentVariable("JWT_SECRET", "Process")

if ([string]::IsNullOrEmpty($neo4jPassword) -or $neo4jPassword -eq "your_neo4j_password_here") {
    Write-Error "NEO4J_PASSWORD is not set or using default value. Please update .env file."
    exit 1
}

if ([string]::IsNullOrEmpty($jwtSecret) -or $jwtSecret -eq "your_jwt_secret_key_here_change_in_production") {
    Write-Error "JWT_SECRET is not set or using default value. Please update .env file."
    exit 1
}

Write-Info "Environment variables validated successfully."

# Create necessary directories
Write-Info "Creating data directories..."
New-Item -ItemType Directory -Force -Path data | Out-Null
New-Item -ItemType Directory -Force -Path logs | Out-Null

# Pull latest images
Write-Info "Pulling latest Docker images..."
& $composeCmd pull

# Build images
Write-Info "Building Docker images..."
& $composeCmd build --no-cache

# Stop existing containers
Write-Info "Stopping existing containers..."
& $composeCmd down

# Start services
Write-Info "Starting services..."
& $composeCmd up -d

# Wait for services to be healthy
Write-Info "Waiting for services to be healthy..."
Start-Sleep -Seconds 10

# Check service health
Write-Info "Checking service health..."

# Check Backend
try {
    $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Info "✓ Backend is healthy"
    }
} catch {
    Write-Warning "✗ Backend health check failed (may still be starting)"
}

# Check Frontend
try {
    $response = Invoke-WebRequest -Uri "http://localhost/health" -UseBasicParsing -TimeoutSec 5
    if ($response.StatusCode -eq 200) {
        Write-Info "✓ Frontend is healthy"
    }
} catch {
    Write-Warning "✗ Frontend health check failed (may still be starting)"
}

# Show running containers
Write-Info "Running containers:"
& $composeCmd ps

Write-Host ""
Write-Host "==========================================" -ForegroundColor Cyan
Write-Info "Deployment completed!"
Write-Host "==========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Access the application at:"
Write-Host "  Frontend: http://localhost"
Write-Host "  Backend API: http://localhost:8000"
Write-Host "  Neo4j Browser: http://localhost:7474"
Write-Host ""
Write-Host "To view logs: $composeCmd logs -f"
Write-Host "To stop services: $composeCmd down"
Write-Host ""
