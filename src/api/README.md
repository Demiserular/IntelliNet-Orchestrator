# IntelliNet Orchestrator API

FastAPI REST API layer for the IntelliNet Orchestrator network service orchestration platform.

## Overview

This module provides RESTful API endpoints for managing network topology, provisioning services, and accessing analytics.

## Components

### Application (`app.py`)
- FastAPI application initialization with lifespan management
- CORS middleware configuration
- Dependency injection setup for repositories and services
- Global exception handlers and logging middleware

### Request/Response Models (`models.py`)
- Pydantic models for request validation
- Standardized response formats
- Models include:
  - `DeviceCreate`, `DeviceResponse`
  - `LinkCreate`, `LinkResponse`
  - `ServiceProvisionRequest`, `ServiceResponse`
  - `TopologyResponse`, `AnalyticsStatusResponse`
  - `ErrorResponse`, `SuccessResponse`

### Routes

#### Topology Management (`routes/topology.py`)
- `POST /api/topology/device` - Create a network device
- `GET /api/topology/device/{device_id}` - Get device by ID
- `DELETE /api/topology/device/{device_id}` - Delete a device
- `POST /api/topology/link` - Create a link between devices
- `GET /api/topology/` - Get complete network topology

#### Service Provisioning (`routes/services.py`)
- `POST /api/service/provision` - Provision a new service
- `GET /api/service/{service_id}` - Get service by ID
- `DELETE /api/service/{service_id}` - Decommission a service

#### Analytics & Optimization (`routes/analytics.py`)
- `GET /api/analytics/status` - Get aggregated network status
- `GET /api/optimization/path/{source}/{target}` - Find optimal path
- `GET /api/analytics/device/{device_id}/metrics` - Get device metrics

### Middleware (`middleware.py`)
- Global exception handler for unhandled errors
- HTTP exception handler for standardized error responses
- Validation exception handler for Pydantic validation errors
- Request/response logging middleware

## Error Handling

All errors return a standardized format:

```json
{
  "error": {
    "code": "ERROR_CODE",
    "message": "Human-readable error message",
    "details": {
      "additional": "context"
    }
  }
}
```

## Running the API

```bash
# Development mode with auto-reload
uvicorn src.api.app:app --reload --host 0.0.0.0 --port 8000

# Production mode
uvicorn src.api.app:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Documentation

Once running, access:
- Swagger UI: http://localhost:8000/api/docs
- ReDoc: http://localhost:8000/api/redoc
- OpenAPI JSON: http://localhost:8000/api/openapi.json

## Testing

Integration tests are located in `tests/test_api/`:

```bash
# Run all API tests
pytest tests/test_api/ -v

# Run specific test file
pytest tests/test_api/test_topology_endpoints.py -v

# Run with coverage
pytest tests/test_api/ --cov=src.api --cov-report=html
```

## Configuration

API configuration is managed through environment variables or `config.yaml`:

- `API_HOST` - Server host (default: 0.0.0.0)
- `API_PORT` - Server port (default: 8000)
- `API_CORS_ORIGINS` - Comma-separated list of allowed origins
- `NEO4J_URI` - Neo4j connection URI
- `NEO4J_USER` - Neo4j username
- `NEO4J_PASSWORD` - Neo4j password
- `METRICS_PATH` - Path to metrics database

## Dependencies

The API uses dependency injection to provide:
- `Neo4jRepository` - Topology data persistence
- `MetricsRepository` - Metrics and logs storage
- `RuleEngine` - Service validation rules
- `ServiceOrchestrator` - Service provisioning workflow

## Status Codes

- `200 OK` - Successful GET/DELETE operations
- `201 Created` - Successful POST operations
- `400 Bad Request` - Validation errors or business logic failures
- `404 Not Found` - Resource not found
- `409 Conflict` - Resource already exists
- `500 Internal Server Error` - Unexpected server errors
