"""
Integration tests for ServiceOrchestrator

These tests verify the end-to-end service provisioning and decommissioning
workflows, including integration with Neo4j, metrics repository, and rule engine.
"""

import pytest
import os
import tempfile
from unittest.mock import Mock, MagicMock, patch

from src.services.service_orchestrator import ServiceOrchestrator
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.rule_engine import RuleEngine
from src.models.service import Service, ServiceType, ServiceStatus
from src.models.device import DeviceType
from src.models.specialized_devices import MPLSRouter, DWDMDevice
from src.models.link import Link, LinkType


@pytest.fixture
def temp_db():
    """Create a temporary database file for testing"""
    fd, path = tempfile.mkstemp(suffix=".db")
    os.close(fd)
    yield path
    # Cleanup
    if os.path.exists(path):
        os.remove(path)


@pytest.fixture
def metrics_repo(temp_db):
    """Create a MetricsRepository instance with temporary database"""
    return MetricsRepository(db_path=temp_db)


@pytest.fixture
def rule_engine():
    """Create a RuleEngine instance"""
    return RuleEngine()


@pytest.fixture
def mock_neo4j_repo():
    """Create a mock Neo4jRepository for testing"""
    mock_repo = Mock(spec=Neo4jRepository)
    mock_repo.driver = MagicMock()
    return mock_repo


@pytest.fixture
def orchestrator(mock_neo4j_repo, metrics_repo, rule_engine):
    """Create a ServiceOrchestrator instance with dependencies"""
    return ServiceOrchestrator(mock_neo4j_repo, metrics_repo, rule_engine)


class TestServiceOrchestratorInitialization:
    """Test ServiceOrchestrator initialization"""
    
    def test_initialization_with_dependencies(self, mock_neo4j_repo, metrics_repo, rule_engine):
        """Test that ServiceOrchestrator initializes with all dependencies"""
        orchestrator = ServiceOrchestrator(mock_neo4j_repo, metrics_repo, rule_engine)
        
        assert orchestrator.neo4j_repo == mock_neo4j_repo
        assert orchestrator.metrics_repo == metrics_repo
        assert orchestrator.rule_engine == rule_engine


class TestServiceProvisioning:
    """Test service provisioning workflow"""
    
    def test_provision_service_success(self, orchestrator, mock_neo4j_repo):
        """Test successful end-to-end service provisioning"""
        # Setup
        service = Service(
            id="S001",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R3",
            bandwidth=50.0,
            latency_requirement=10.0
        )
        
        # Mock Neo4j responses
        mock_neo4j_repo.find_shortest_path.return_value = ["R1", "R2", "R3"]
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "name": "Router1",
            "type": "MPLS",
            "capacity": 100.0,
            "utilization": 0.3,
            "status": "active"
        }
        
        # Mock Neo4j session for service creation
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"s": {"id": "S001"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        mock_neo4j_repo.get_links_for_device.return_value = [
            {
                "id": "L1",
                "source": "R1",
                "target": "R2",
                "utilization": 0.2,
                "latency": 5.0
            }
        ]
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert
        assert success is True
        assert "provisioned successfully" in message
        assert service.status == ServiceStatus.ACTIVE
        assert service.path == ["R1", "R2", "R3"]
        assert service.activated_at is not None
        
        # Verify Neo4j interactions
        mock_neo4j_repo.find_shortest_path.assert_called_once_with("R1", "R3")
        assert mock_neo4j_repo.get_device.call_count >= 1
    
    def test_provision_service_no_path(self, orchestrator, mock_neo4j_repo):
        """Test provisioning fails when no path exists"""
        # Setup
        service = Service(
            id="S002",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R99",
            bandwidth=50.0
        )
        
        # Mock Neo4j to return no path
        mock_neo4j_repo.find_shortest_path.return_value = None
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert
        assert success is False
        assert "No path found" in message
        assert service.status == ServiceStatus.FAILED
    
    def test_provision_service_validation_failure(self, mock_neo4j_repo, metrics_repo):
        """Test provisioning fails when rule validation fails"""
        # Create a custom rule that will fail
        from src.services.rule_engine import RuleEngine, RuleCondition
        
        rule_engine = RuleEngine()
        # Add a custom rule that always rejects
        rule_engine.add_rule(RuleCondition(
            rule_id="TEST001",
            name="Test Rejection Rule",
            condition=lambda service, device, link: service.bandwidth > 100.0,
            action="reject",
            priority=0
        ))
        
        orchestrator = ServiceOrchestrator(mock_neo4j_repo, metrics_repo, rule_engine)
        
        # Setup
        service = Service(
            id="S003",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R2",
            bandwidth=150.0  # Exceeds threshold
        )
        
        # Mock Neo4j responses
        mock_neo4j_repo.find_shortest_path.return_value = ["R1", "R2"]
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "name": "Router1",
            "type": "MPLS",
            "capacity": 100.0,
            "utilization": 0.5,
            "status": "active"
        }
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert
        assert success is False
        assert "Validation failed" in message or "TEST001" in message
        assert service.status == ServiceStatus.FAILED
    
    def test_provision_service_neo4j_creation_failure(self, orchestrator, mock_neo4j_repo):
        """Test error handling when Neo4j service creation fails"""
        # Setup
        service = Service(
            id="S004",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R2",
            bandwidth=50.0
        )
        
        # Mock Neo4j responses
        mock_neo4j_repo.find_shortest_path.return_value = ["R1", "R2"]
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "capacity": 100.0,
            "utilization": 0.3,
            "status": "active"
        }
        
        # Mock Neo4j session to fail service creation
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = None  # Simulate creation failure
        mock_session.run.return_value = mock_result
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert
        assert success is False
        assert "Failed to create service" in message
        assert service.status == ServiceStatus.FAILED


class TestMetricsRecording:
    """Test metrics recording during provisioning"""
    
    def test_metrics_recorded_during_provisioning(self, orchestrator, mock_neo4j_repo, metrics_repo):
        """Test that device and link metrics are recorded during provisioning"""
        # Setup
        service = Service(
            id="S005",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R2",
            bandwidth=50.0
        )
        
        # Mock Neo4j responses
        mock_neo4j_repo.find_shortest_path.return_value = ["R1", "R2"]
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "capacity": 100.0,
            "utilization": 0.3,
            "status": "active"
        }
        
        # Mock Neo4j session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"s": {"id": "S005"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        mock_neo4j_repo.get_links_for_device.return_value = [
            {
                "id": "L1",
                "source": "R1",
                "target": "R2",
                "utilization": 0.2,
                "latency": 5.0
            }
        ]
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert
        assert success is True
        
        # Verify metrics were recorded
        device_metrics = metrics_repo.get_device_metrics("R1", limit=10)
        assert len(device_metrics) > 0
        
        link_metrics = metrics_repo.get_link_metrics("L1", limit=10)
        assert len(link_metrics) > 0
        
        service_logs = metrics_repo.get_service_logs("S005", limit=10)
        assert len(service_logs) > 0
        assert any(log["event_type"] == "provisioned" for log in service_logs)


class TestServiceDecommissioning:
    """Test service decommissioning workflow"""
    
    def test_decommission_service_success(self, orchestrator, mock_neo4j_repo):
        """Test successful service decommissioning"""
        # Setup
        service_id = "S006"
        
        # Mock Neo4j session for service retrieval
        mock_session = MagicMock()
        
        # First call returns service data
        mock_get_result = MagicMock()
        mock_get_result.single.return_value = {
            "s": {
                "id": service_id,
                "path": ["R1", "R2", "R3"],
                "status": "active"
            }
        }
        
        # Second call returns deletion confirmation
        mock_delete_result = MagicMock()
        mock_delete_result.single.return_value = {"deleted_count": 1}
        
        mock_session.run.side_effect = [mock_get_result, mock_delete_result]
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "utilization": 0.3,
            "status": "active"
        }
        
        # Execute
        success, message = orchestrator.decommission_service(service_id)
        
        # Assert
        assert success is True
        assert "decommissioned successfully" in message
    
    def test_decommission_service_not_found(self, orchestrator, mock_neo4j_repo):
        """Test decommissioning fails when service doesn't exist"""
        # Setup
        service_id = "S999"
        
        # Mock Neo4j session to return no service
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = None
        mock_session.run.return_value = mock_result
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        # Execute
        success, message = orchestrator.decommission_service(service_id)
        
        # Assert
        assert success is False
        assert "not found" in message
    
    def test_decommission_updates_metrics(self, orchestrator, mock_neo4j_repo, metrics_repo):
        """Test that device metrics are updated during decommissioning"""
        # Setup
        service_id = "S007"
        
        # Mock Neo4j session
        mock_session = MagicMock()
        
        mock_get_result = MagicMock()
        mock_get_result.single.return_value = {
            "s": {
                "id": service_id,
                "path": ["R1", "R2"],
                "status": "active"
            }
        }
        
        mock_delete_result = MagicMock()
        mock_delete_result.single.return_value = {"deleted_count": 1}
        
        mock_session.run.side_effect = [mock_get_result, mock_delete_result]
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "utilization": 0.5,
            "status": "active"
        }
        
        # Execute
        success, message = orchestrator.decommission_service(service_id)
        
        # Assert
        assert success is True
        
        # Verify service log was recorded
        service_logs = metrics_repo.get_service_logs(service_id, limit=10)
        assert len(service_logs) > 0
        assert any(log["event_type"] == "decommissioned" for log in service_logs)


class TestRuleValidationIntegration:
    """Test integration with rule engine"""
    
    def test_rule_validation_integration(self, mock_neo4j_repo, metrics_repo):
        """Test that rule engine is properly integrated in provisioning workflow"""
        # Create a custom rule engine with a specific rule
        rule_engine = RuleEngine()
        orchestrator = ServiceOrchestrator(mock_neo4j_repo, metrics_repo, rule_engine)
        
        # Setup service that should pass validation
        service = Service(
            id="S008",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="R1",
            target_device_id="R2",
            bandwidth=30.0  # Within capacity
        )
        
        # Mock Neo4j responses
        mock_neo4j_repo.find_shortest_path.return_value = ["R1", "R2"]
        mock_neo4j_repo.get_device.return_value = {
            "id": "R1",
            "capacity": 100.0,
            "utilization": 0.2,
            "status": "active"
        }
        
        # Mock Neo4j session
        mock_session = MagicMock()
        mock_result = MagicMock()
        mock_result.single.return_value = {"s": {"id": "S008"}}
        mock_session.run.return_value = mock_result
        mock_neo4j_repo.driver.session.return_value.__enter__.return_value = mock_session
        
        mock_neo4j_repo.get_links_for_device.return_value = []
        
        # Execute
        success, message = orchestrator.provision_service(service)
        
        # Assert - should succeed because bandwidth is within capacity
        assert success is True
