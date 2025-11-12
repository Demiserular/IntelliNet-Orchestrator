"""FastAPI application initialization and configuration"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from contextlib import asynccontextmanager
from typing import Optional
import logging

from src.config import get_config
from src.dependencies import get_container
from src.logging_config import get_logger
from src.api.middleware import (
    global_exception_handler,
    http_exception_handler,
    validation_exception_handler,
    logging_middleware
)

logger = get_logger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management"""
    # Startup: Initialize dependency container
    logger.info("=" * 80)
    logger.info("Starting IntelliNet Orchestrator")
    logger.info("=" * 80)
    
    container = get_container()
    container.initialize()
    
    logger.info("IntelliNet Orchestrator startup complete")
    logger.info("=" * 80)
    
    yield
    
    # Shutdown: Clean up resources
    logger.info("=" * 80)
    logger.info("Shutting down IntelliNet Orchestrator")
    logger.info("=" * 80)
    
    container.shutdown()
    
    logger.info("IntelliNet Orchestrator shutdown complete")
    logger.info("=" * 80)


# Initialize FastAPI application
app = FastAPI(
    title="IntelliNet Orchestrator API",
    description="""
# IntelliNet Orchestrator API

A comprehensive network service orchestration platform for telecommunication infrastructure.

## Features

* **Topology Management**: Create and manage network devices and links
* **Service Provisioning**: Provision network services with automated validation
* **Rule-Based Validation**: Enforce capacity constraints and QoS policies
* **Path Optimization**: Calculate optimal service paths considering latency and utilization
* **Analytics**: Real-time monitoring and historical metrics
* **Role-Based Access Control**: Admin and user roles with JWT authentication

## Authentication

Most endpoints require authentication. Use the `/api/auth/login` endpoint to obtain a JWT token,
then include it in the `Authorization` header as `Bearer <token>`.

## Device Types

* **DWDM**: Dense Wavelength Division Multiplexing
* **OTN**: Optical Transport Network
* **SONET**: Synchronous Optical Networking
* **MPLS**: Multiprotocol Label Switching
* **GPON_OLT**: Gigabit Passive Optical Network - Optical Line Terminal
* **GPON_ONT**: Gigabit Passive Optical Network - Optical Network Terminal
* **FTTH**: Fiber To The Home

## Service Types

* **MPLS_VPN**: MPLS Virtual Private Network
* **OTN_CIRCUIT**: OTN Circuit Service
* **GPON_ACCESS**: GPON Access Service
* **FTTH_SERVICE**: FTTH Service

## Support

For detailed documentation, see `/api/docs` or `/api/redoc`.
    """,
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
    openapi_url="/api/openapi.json",
    lifespan=lifespan,
    contact={
        "name": "IntelliNet Orchestrator Team",
        "email": "support@intellinet.example.com",
    },
    license_info={
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    openapi_tags=[
        {
            "name": "Health",
            "description": "Health check and system status endpoints"
        },
        {
            "name": "Authentication",
            "description": "User authentication and authorization"
        },
        {
            "name": "Topology",
            "description": "Network topology management - devices and links"
        },
        {
            "name": "Services",
            "description": "Network service provisioning and management"
        },
        {
            "name": "Analytics",
            "description": "Network analytics, metrics, and monitoring"
        },
        {
            "name": "Optimization",
            "description": "Path optimization and network planning"
        }
    ]
)

# Configure CORS middleware
config = get_config()
app.add_middleware(
    CORSMiddleware,
    allow_origins=config.api.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

logger.info(f"CORS configured for origins: {config.api.cors_origins}")

# Add logging middleware
app.middleware("http")(logging_middleware)

# Register exception handlers
app.add_exception_handler(Exception, global_exception_handler)
app.add_exception_handler(StarletteHTTPException, http_exception_handler)
app.add_exception_handler(RequestValidationError, validation_exception_handler)

logger.info("Exception handlers and middleware registered")


# Import dependency injection functions
from src.dependencies import (
    get_neo4j_repository,
    get_metrics_repository,
    get_user_repository,
    get_rule_engine,
    get_service_orchestrator,
    get_auth_service
)


# Health check endpoint
@app.get("/health", tags=["Health"])
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": "IntelliNet Orchestrator",
        "version": "1.0.0"
    }


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information"""
    return {
        "message": "IntelliNet Orchestrator API",
        "version": "1.0.0",
        "docs": "/api/docs",
        "health": "/health"
    }


# Add CORS preflight handler for common endpoints
@app.get("/topology")
async def topology_redirect():
    """Redirect /topology to /api/topology/"""
    return {"message": "Use /api/topology/ endpoint", "redirect": "/api/topology/"}

@app.get("/api/auth/status")
async def auth_status():
    """Check authentication status"""
    return {"message": "Use /api/auth/me for user info", "endpoints": ["/api/auth/login", "/api/auth/logout", "/api/auth/me"]}


# Import and include routers
from src.api.routes import topology, services, analytics, auth

app.include_router(auth.router)
app.include_router(topology.router)
app.include_router(services.router)
app.include_router(analytics.router)
