"""
Unit tests for Service model
Tests Requirements: 2.1, 2.5
"""
import pytest
from src.models.service import Service, ServiceType, ServiceStatus


class TestServiceCreation:
    """Test Service object creation and initialization"""
    
    def test_service_initialization_with_all_parameters(self):
        """Test service is initialized correctly with all parameters"""
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0,
            latency_requirement=10.0
        )
        
        assert service.id == "S1"
        assert service.service_type == ServiceType.MPLS_VPN
        assert service.source_device_id == "D1"
        assert service.target_device_id == "D2"
        assert service.bandwidth == 50.0
        assert service.latency_requirement == 10.0
        assert service.status == ServiceStatus.PENDING
        assert service.path == []
        assert service.created_at is None
        assert service.activated_at is None
    
    def test_service_initialization_without_latency_requirement(self):
        """Test service initialization with None latency requirement"""
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0
        )
        
        assert service.latency_requirement is None
    
    def test_service_with_mpls_vpn_type(self):
        """Test service creation with MPLS_VPN type"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        assert service.service_type == ServiceType.MPLS_VPN
        assert service.service_type.value == "MPLS_VPN"
    
    def test_service_with_otn_circuit_type(self):
        """Test service creation with OTN_CIRCUIT type"""
        service = Service("S1", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
        
        assert service.service_type == ServiceType.OTN_CIRCUIT
        assert service.service_type.value == "OTN_CIRCUIT"
    
    def test_service_with_gpon_access_type(self):
        """Test service creation with GPON_ACCESS type"""
        service = Service("S1", ServiceType.GPON_ACCESS, "G1", "G2", 1.0)
        
        assert service.service_type == ServiceType.GPON_ACCESS
        assert service.service_type.value == "GPON_ACCESS"
    
    def test_service_with_ftth_service_type(self):
        """Test service creation with FTTH_SERVICE type"""
        service = Service("S1", ServiceType.FTTH_SERVICE, "D1", "D2", 1.0)
        
        assert service.service_type == ServiceType.FTTH_SERVICE
        assert service.service_type.value == "FTTH_SERVICE"
    
    def test_service_default_status_is_pending(self):
        """Test service default status is PENDING"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        assert service.status == ServiceStatus.PENDING
        assert service.status.value == "pending"
    
    def test_service_default_path_is_empty_list(self):
        """Test service default path is empty list"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        assert service.path == []
        assert isinstance(service.path, list)


class TestServiceStatusManagement:
    """Test service status changes"""
    
    def test_service_status_change_to_active(self):
        """Test changing service status to ACTIVE"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        service.status = ServiceStatus.ACTIVE
        
        assert service.status == ServiceStatus.ACTIVE
        assert service.status.value == "active"
    
    def test_service_status_change_to_failed(self):
        """Test changing service status to FAILED"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        service.status = ServiceStatus.FAILED
        
        assert service.status == ServiceStatus.FAILED
        assert service.status.value == "failed"
    
    def test_service_status_change_to_decommissioned(self):
        """Test changing service status to DECOMMISSIONED"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        service.status = ServiceStatus.DECOMMISSIONED
        
        assert service.status == ServiceStatus.DECOMMISSIONED
        assert service.status.value == "decommissioned"


class TestServicePathManagement:
    """Test service path management"""
    
    def test_service_path_can_be_set(self):
        """Test service path can be set with device IDs"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        service.path = ["D1", "R1", "R2", "D2"]
        
        assert service.path == ["D1", "R1", "R2", "D2"]
        assert len(service.path) == 4
    
    def test_service_path_can_be_modified(self):
        """Test service path can be modified"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        service.path = ["D1", "R1", "D2"]
        
        service.path.append("R2")
        
        assert "R2" in service.path
        assert len(service.path) == 4
    
    def test_service_path_empty_for_new_service(self):
        """Test new service has empty path"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        assert len(service.path) == 0


class TestServiceSerialization:
    """Test Service to_dict() serialization"""
    
    def test_service_to_dict_complete(self):
        """Test service serialization with all fields"""
        service = Service(
            id="S1",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=50.0,
            latency_requirement=10.0
        )
        service.status = ServiceStatus.ACTIVE
        service.path = ["D1", "R1", "D2"]
        
        result = service.to_dict()
        
        assert result["id"] == "S1"
        assert result["service_type"] == "MPLS_VPN"
        assert result["source"] == "D1"
        assert result["target"] == "D2"
        assert result["bandwidth"] == 50.0
        assert result["latency_requirement"] == 10.0
        assert result["status"] == "active"
        assert result["path"] == ["D1", "R1", "D2"]
    
    def test_service_to_dict_with_none_latency(self):
        """Test service serialization with None latency requirement"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        result = service.to_dict()
        
        assert result["latency_requirement"] is None
    
    def test_service_to_dict_with_empty_path(self):
        """Test service serialization with empty path"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        result = service.to_dict()
        
        assert result["path"] == []
    
    def test_service_to_dict_different_service_types(self):
        """Test serialization preserves service type correctly"""
        service_types = [
            (ServiceType.MPLS_VPN, "MPLS_VPN"),
            (ServiceType.OTN_CIRCUIT, "OTN_CIRCUIT"),
            (ServiceType.GPON_ACCESS, "GPON_ACCESS"),
            (ServiceType.FTTH_SERVICE, "FTTH_SERVICE")
        ]
        
        for service_type, expected_value in service_types:
            service = Service("S1", service_type, "D1", "D2", 10.0)
            result = service.to_dict()
            
            assert result["service_type"] == expected_value
    
    def test_service_to_dict_different_statuses(self):
        """Test serialization with different status values"""
        statuses = [
            (ServiceStatus.PENDING, "pending"),
            (ServiceStatus.ACTIVE, "active"),
            (ServiceStatus.FAILED, "failed"),
            (ServiceStatus.DECOMMISSIONED, "decommissioned")
        ]
        
        for status, expected_value in statuses:
            service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
            service.status = status
            result = service.to_dict()
            
            assert result["status"] == expected_value
    
    def test_service_to_dict_returns_dict_type(self):
        """Test that to_dict returns a dictionary"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        
        result = service.to_dict()
        
        assert isinstance(result, dict)
        assert len(result) == 8  # Should have 8 keys
    
    def test_service_to_dict_with_complex_path(self):
        """Test serialization with complex multi-hop path"""
        service = Service("S1", ServiceType.MPLS_VPN, "D1", "D2", 50.0)
        service.path = ["D1", "R1", "R2", "R3", "R4", "D2"]
        
        result = service.to_dict()
        
        assert result["path"] == ["D1", "R1", "R2", "R3", "R4", "D2"]
        assert len(result["path"]) == 6


class TestServiceTypeEnum:
    """Test ServiceType enumeration"""
    
    def test_service_type_enum_values(self):
        """Test ServiceType enum has correct values"""
        assert ServiceType.MPLS_VPN.value == "MPLS_VPN"
        assert ServiceType.OTN_CIRCUIT.value == "OTN_CIRCUIT"
        assert ServiceType.GPON_ACCESS.value == "GPON_ACCESS"
        assert ServiceType.FTTH_SERVICE.value == "FTTH_SERVICE"
    
    def test_service_type_enum_members(self):
        """Test ServiceType enum has all expected members"""
        members = [member.name for member in ServiceType]
        
        assert "MPLS_VPN" in members
        assert "OTN_CIRCUIT" in members
        assert "GPON_ACCESS" in members
        assert "FTTH_SERVICE" in members
        assert len(members) == 4


class TestServiceStatusEnum:
    """Test ServiceStatus enumeration"""
    
    def test_service_status_enum_values(self):
        """Test ServiceStatus enum has correct values"""
        assert ServiceStatus.PENDING.value == "pending"
        assert ServiceStatus.ACTIVE.value == "active"
        assert ServiceStatus.FAILED.value == "failed"
        assert ServiceStatus.DECOMMISSIONED.value == "decommissioned"
    
    def test_service_status_enum_members(self):
        """Test ServiceStatus enum has all expected members"""
        members = [member.name for member in ServiceStatus]
        
        assert "PENDING" in members
        assert "ACTIVE" in members
        assert "FAILED" in members
        assert "DECOMMISSIONED" in members
        assert len(members) == 4


class TestServiceBandwidthRequirements:
    """Test service bandwidth handling"""
    
    def test_service_with_low_bandwidth(self):
        """Test service with low bandwidth requirement"""
        service = Service("S1", ServiceType.GPON_ACCESS, "G1", "G2", 1.0)
        
        assert service.bandwidth == 1.0
    
    def test_service_with_high_bandwidth(self):
        """Test service with high bandwidth requirement"""
        service = Service("S1", ServiceType.OTN_CIRCUIT, "D1", "D2", 100.0)
        
        assert service.bandwidth == 100.0
    
    def test_service_with_fractional_bandwidth(self):
        """Test service with fractional bandwidth"""
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 2.5)
        
        assert service.bandwidth == 2.5


class TestServiceLatencyRequirements:
    """Test service latency requirement handling"""
    
    def test_service_with_strict_latency(self):
        """Test service with strict latency requirement"""
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 50.0, latency_requirement=5.0)
        
        assert service.latency_requirement == 5.0
    
    def test_service_with_relaxed_latency(self):
        """Test service with relaxed latency requirement"""
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 50.0, latency_requirement=100.0)
        
        assert service.latency_requirement == 100.0
    
    def test_service_without_latency_requirement(self):
        """Test service without latency requirement"""
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 50.0)
        
        assert service.latency_requirement is None
