"""
Unit tests for Link model
Tests Requirements: 2.1, 2.5
"""
import pytest
from src.models.link import Link, LinkType


class TestLinkCreation:
    """Test Link object creation and initialization"""
    
    def test_link_initialization_with_all_parameters(self):
        """Test link is initialized correctly with all parameters"""
        link = Link(
            id="L1",
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=10.0,
            link_type=LinkType.FIBER,
            latency=5.0
        )
        
        assert link.id == "L1"
        assert link.source_device_id == "D1"
        assert link.target_device_id == "D2"
        assert link.bandwidth == 10.0
        assert link.link_type == LinkType.FIBER
        assert link.latency == 5.0
        assert link.utilization == 0.0
        assert link.status == "active"
    
    def test_link_initialization_with_default_latency(self):
        """Test link uses default latency of 0.0"""
        link = Link(
            id="L1",
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=10.0,
            link_type=LinkType.ETHERNET
        )
        
        assert link.latency == 0.0
    
    def test_link_with_fiber_type(self):
        """Test link creation with FIBER type"""
        link = Link("L1", "D1", "D2", 100.0, LinkType.FIBER)
        
        assert link.link_type == LinkType.FIBER
        assert link.link_type.value == "fiber"
    
    def test_link_with_ethernet_type(self):
        """Test link creation with ETHERNET type"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.ETHERNET)
        
        assert link.link_type == LinkType.ETHERNET
        assert link.link_type.value == "ethernet"
    
    def test_link_with_wireless_type(self):
        """Test link creation with WIRELESS type"""
        link = Link("L1", "D1", "D2", 1.0, LinkType.WIRELESS)
        
        assert link.link_type == LinkType.WIRELESS
        assert link.link_type.value == "wireless"


class TestLinkBandwidthCalculation:
    """Test link available bandwidth calculation"""
    
    def test_calculate_available_bandwidth_no_utilization(self):
        """Test bandwidth calculation with zero utilization"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        
        available = link.calculate_available_bandwidth()
        
        assert available == 10.0
    
    def test_calculate_available_bandwidth_partial_utilization(self):
        """Test bandwidth calculation with partial utilization"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        link.utilization = 0.5  # 50% utilized
        
        available = link.calculate_available_bandwidth()
        
        assert available == 5.0
    
    def test_calculate_available_bandwidth_high_utilization(self):
        """Test bandwidth calculation with high utilization"""
        link = Link("L1", "D1", "D2", 100.0, LinkType.FIBER)
        link.utilization = 0.8  # 80% utilized
        
        available = link.calculate_available_bandwidth()
        
        assert abs(available - 20.0) < 0.001  # Float comparison with tolerance
    
    def test_calculate_available_bandwidth_full_utilization(self):
        """Test bandwidth calculation with full utilization"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        link.utilization = 1.0  # 100% utilized
        
        available = link.calculate_available_bandwidth()
        
        assert available == 0.0
    
    def test_calculate_available_bandwidth_low_utilization(self):
        """Test bandwidth calculation with low utilization"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        link.utilization = 0.1  # 10% utilized
        
        available = link.calculate_available_bandwidth()
        
        assert available == 9.0
    
    def test_calculate_available_bandwidth_various_capacities(self):
        """Test bandwidth calculation with different link capacities"""
        test_cases = [
            (10.0, 0.5, 5.0),
            (100.0, 0.3, 70.0),
            (1.0, 0.9, 0.1),
            (50.0, 0.0, 50.0),
        ]
        
        for bandwidth, utilization, expected in test_cases:
            link = Link("L1", "D1", "D2", bandwidth, LinkType.FIBER)
            link.utilization = utilization
            
            available = link.calculate_available_bandwidth()
            
            assert abs(available - expected) < 0.001  # Float comparison with tolerance


class TestLinkSerialization:
    """Test Link to_dict() serialization"""
    
    def test_link_to_dict_complete(self):
        """Test link serialization with all fields"""
        link = Link(
            id="L1",
            source_device_id="D1",
            target_device_id="D2",
            bandwidth=10.0,
            link_type=LinkType.FIBER,
            latency=5.0
        )
        link.utilization = 0.3
        link.status = "active"
        
        result = link.to_dict()
        
        assert result["id"] == "L1"
        assert result["source"] == "D1"
        assert result["target"] == "D2"
        assert result["bandwidth"] == 10.0
        assert result["type"] == "fiber"
        assert result["latency"] == 5.0
        assert result["utilization"] == 0.3
        assert result["status"] == "active"
    
    def test_link_to_dict_with_default_values(self):
        """Test link serialization with default values"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.ETHERNET)
        
        result = link.to_dict()
        
        assert result["latency"] == 0.0
        assert result["utilization"] == 0.0
        assert result["status"] == "active"
    
    def test_link_to_dict_different_link_types(self):
        """Test serialization preserves link type correctly"""
        link_types = [
            (LinkType.FIBER, "fiber"),
            (LinkType.ETHERNET, "ethernet"),
            (LinkType.WIRELESS, "wireless")
        ]
        
        for link_type, expected_value in link_types:
            link = Link("L1", "D1", "D2", 10.0, link_type)
            result = link.to_dict()
            
            assert result["type"] == expected_value
    
    def test_link_to_dict_modified_status(self):
        """Test serialization with modified status"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        link.status = "maintenance"
        
        result = link.to_dict()
        
        assert result["status"] == "maintenance"
    
    def test_link_to_dict_high_latency(self):
        """Test serialization with high latency value"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.WIRELESS, latency=100.5)
        
        result = link.to_dict()
        
        assert result["latency"] == 100.5
    
    def test_link_to_dict_returns_dict_type(self):
        """Test that to_dict returns a dictionary"""
        link = Link("L1", "D1", "D2", 10.0, LinkType.FIBER)
        
        result = link.to_dict()
        
        assert isinstance(result, dict)
        assert len(result) == 8  # Should have 8 keys (id, source, target, bandwidth, type, latency, utilization, status)


class TestLinkTypeEnum:
    """Test LinkType enumeration"""
    
    def test_link_type_enum_values(self):
        """Test LinkType enum has correct values"""
        assert LinkType.FIBER.value == "fiber"
        assert LinkType.ETHERNET.value == "ethernet"
        assert LinkType.WIRELESS.value == "wireless"
    
    def test_link_type_enum_members(self):
        """Test LinkType enum has all expected members"""
        members = [member.name for member in LinkType]
        
        assert "FIBER" in members
        assert "ETHERNET" in members
        assert "WIRELESS" in members
        assert len(members) == 3
