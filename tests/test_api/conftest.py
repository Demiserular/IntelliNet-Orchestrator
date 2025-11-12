"""Pytest fixtures for API tests"""

import pytest
from fastapi.testclient import TestClient
import os
import tempfile

from src.api.app import app, neo4j_repo, metrics_repo, rule_engine, service_orchestrator
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.rule_engine import RuleEngine
from src.services.service_orchestrator import ServiceOrchestrator


@pytest.fixture(scope="function")
def test_db():
    """Create a temporary test database"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    
    yield db_path
    
    # Cleanup
    if os.path.exists(db_path):
        os.unlink(db_path)


@pytest.fixture(scope="function")
def mock_neo4j_repo(monkeypatch):
    """Mock Neo4j repository for testing"""
    class MockNeo4jRepository:
        def __init__(self):
            self.devices = {}
            self.links = {}
            self.services = {}
        
        def create_device(self, device):
            self.devices[device.id] = device.to_dict()
            return True
        
        def get_device(self, device_id):
            return self.devices.get(device_id)
        
        def delete_device(self, device_id):
            if device_id in self.devices:
                del self.devices[device_id]
                return True
            return False
        
        def create_link(self, link):
            self.links[link.id] = link.to_dict()
            return True
        
        def get_topology_json(self):
            return {
                "devices": list(self.devices.values()),
                "links": list(self.links.values())
            }
        
        def find_shortest_path(self, source_id, target_id):
            # Simple mock: return path if both devices exist
            if source_id in self.devices and target_id in self.devices:
                return [source_id, target_id]
            return None
        
        def find_optimal_path(self, source_id, target_id):
            path = self.find_shortest_path(source_id, target_id)
            if path:
                return {
                    "path": path,
                    "total_latency": 10.0,
                    "available_bandwidth": 50.0
                }
            return None
        
        def get_service(self, service_id):
            return self.services.get(service_id)
        
        def get_all_services(self):
            return list(self.services.values())
        
        def create_service(self, service):
            self.services[service.id] = service.to_dict()
            return True
        
        def delete_service(self, service_id):
            if service_id in self.services:
                del self.services[service_id]
                return True
            return False
        
        def close(self):
            pass
    
    mock_repo = MockNeo4jRepository()
    
    # Patch the global repository
    import src.api.app as app_module
    app_module.neo4j_repo = mock_repo
    
    return mock_repo



@pytest.fixture(scope="function")
def mock_metrics_repo(test_db, monkeypatch):
    """Mock metrics repository for testing"""
    metrics_repo = MetricsRepository(db_path=test_db)
    
    # Patch the global repository
    import src.api.app as app_module
    app_module.metrics_repo = metrics_repo
    
    yield metrics_repo
    
    metrics_repo.close()


@pytest.fixture(scope="function")
def mock_rule_engine(monkeypatch):
    """Mock rule engine for testing"""
    rule_engine = RuleEngine()
    
    # Patch the global rule engine
    import src.api.app as app_module
    app_module.rule_engine = rule_engine
    
    return rule_engine


@pytest.fixture(scope="function")
def mock_service_orchestrator(mock_neo4j_repo, mock_metrics_repo, mock_rule_engine, monkeypatch):
    """Mock service orchestrator for testing"""
    orchestrator = ServiceOrchestrator(
        neo4j_repo=mock_neo4j_repo,
        metrics_repo=mock_metrics_repo,
        rule_engine=mock_rule_engine
    )
    
    # Patch the global orchestrator
    import src.api.app as app_module
    app_module.service_orchestrator = orchestrator
    
    return orchestrator


@pytest.fixture(scope="function")
def client(mock_neo4j_repo, mock_metrics_repo, mock_rule_engine, mock_service_orchestrator):
    """Create a test client with mocked dependencies"""
    # Create a new app instance without lifespan for testing
    from fastapi import FastAPI, Depends
    from fastapi.middleware.cors import CORSMiddleware
    from src.api import app as app_module
    
    test_app = FastAPI(title="Test IntelliNet Orchestrator API")
    
    # Add CORS middleware
    test_app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Override dependency injection functions
    def override_get_neo4j_repository():
        return mock_neo4j_repo
    
    def override_get_metrics_repository():
        return mock_metrics_repo
    
    def override_get_rule_engine():
        return mock_rule_engine
    
    def override_get_service_orchestrator():
        return mock_service_orchestrator
    
    # Import dependency functions
    from src.api.app import (
        get_neo4j_repository,
        get_metrics_repository,
        get_rule_engine,
        get_service_orchestrator
    )
    
    # Import and include routers
    from src.api.routes import topology, services, analytics
    test_app.include_router(topology.router)
    test_app.include_router(services.router)
    test_app.include_router(analytics.router)
    
    # Override dependencies
    test_app.dependency_overrides[get_neo4j_repository] = override_get_neo4j_repository
    test_app.dependency_overrides[get_metrics_repository] = override_get_metrics_repository
    test_app.dependency_overrides[get_rule_engine] = override_get_rule_engine
    test_app.dependency_overrides[get_service_orchestrator] = override_get_service_orchestrator
    
    # Add health endpoint
    @test_app.get("/health")
    async def health_check():
        return {"status": "healthy", "service": "IntelliNet Orchestrator", "version": "1.0.0"}
    
    with TestClient(test_app, raise_server_exceptions=True) as test_client:
        yield test_client
