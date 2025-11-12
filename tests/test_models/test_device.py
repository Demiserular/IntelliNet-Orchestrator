"""
Unit tests for device models including inheritance and polymorphism
Tests Requirements: 2.1, 2.2, 2.3, 2.4, 2.5
"""
import pytest
from src.models.device import Device, DeviceType, DeviceStatus
from src.models.specialized_devices import DWDMDevice, MPLSRouter, GPONDevice
from src.models.service import Service, ServiceType


class TestDeviceInheritanceAndPolymorphism:
    """Test device class inheritance and polymorphic behavior"""
    
    def test_device_is_abstract_class(self):
        """Test that Device cannot be instantiated directly"""
        with pytest.raises(TypeError):
            Device("D1", "TestDevice", DeviceType.MPLS, 100.0)
    
    def test_dwdm_device_inherits_from_device(self):
        """Test DWDM device inherits from Device base class"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0)
        assert isinstance(dwdm, Device)
        assert isinstance(dwdm, DWDMDevice)
    
    def test_mpls_router_inherits_from_device(self):
        """Test MPLS router inherits from Device base class"""
        router = MPLSRouter("R1", "Router1", 100.0)
        assert isinstance(router, Device)
        assert isinstance(router, MPLSRouter)
    
    def test_gpon_device_inherits_from_device(self):
        """Test GPON device inherits from Device base class"""
        gpon = GPONDevice("G1", "GPON1", 10.0, is_olt=True)
        assert isinstance(gpon, Device)
        assert isinstance(gpon, GPONDevice)
    
    def test_polymorphic_provision_method(self):
        """Test that provision method works polymorphically across device types"""
        devices = [
            DWDMDevice("D1", "DWDM1", 100.0),
            MPLSRouter("R1", "Router1", 100.0),
            GPONDevice("G1", "GPON1", 10.0, is_olt=True)
        ]
        
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 50.0)
        
        # All devices should have provision method
        for device in devices:
            assert hasattr(device, 'provision')
            assert callable(device.provision)
            result = device.provision(service)
            assert isinstance(result, bool)
    
    def test_polymorphic_calculate_available_capacity(self):
        """Test that calculate_available_capacity works polymorphically"""
        devices = [
            DWDMDevice("D1", "DWDM1", 100.0),
            MPLSRouter("R1", "Router1", 100.0),
            GPONDevice("G1", "GPON1", 10.0, is_olt=True)
        ]
        
        for device in devices:
            assert hasattr(device, 'calculate_available_capacity')
            assert callable(device.calculate_available_capacity)
            capacity = device.calculate_available_capacity()
            assert isinstance(capacity, float)
            assert capacity >= 0


class TestDWDMDevice:
    """Test DWDM device specific functionality"""
    
    def test_dwdm_device_initialization(self):
        """Test DWDM device is initialized correctly"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80, location="Site A")
        
        assert dwdm.id == "D1"
        assert dwdm.name == "DWDM1"
        assert dwdm.device_type == DeviceType.DWDM
        assert dwdm.capacity == 100.0
        assert dwdm.location == "Site A"
        assert dwdm.status == DeviceStatus.ACTIVE
        assert dwdm.utilization == 0.0
        assert dwdm.wavelengths == 80
        assert dwdm.active_wavelengths == []
    
    def test_dwdm_device_default_wavelengths(self):
        """Test DWDM device uses default 80 wavelengths"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0)
        assert dwdm.wavelengths == 80
    
    def test_dwdm_provision_allocates_wavelength(self):
        """Test provisioning allocates a wavelength"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80)
        service = Service("S1", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
        
        result = dwdm.provision(service)
        
        assert result is True
        assert len(dwdm.active_wavelengths) == 1
        assert dwdm.active_wavelengths[0] == "λ1"
    
    def test_dwdm_provision_multiple_wavelengths(self):
        """Test provisioning multiple services allocates multiple wavelengths"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80)
        
        for i in range(5):
            service = Service(f"S{i}", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
            result = dwdm.provision(service)
            assert result is True
        
        assert len(dwdm.active_wavelengths) == 5
        assert dwdm.active_wavelengths == ["λ1", "λ2", "λ3", "λ4", "λ5"]
    
    def test_dwdm_provision_fails_when_wavelengths_exhausted(self):
        """Test provisioning fails when all wavelengths are used"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=2)
        
        # Provision 2 services successfully
        service1 = Service("S1", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
        service2 = Service("S2", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
        assert dwdm.provision(service1) is True
        assert dwdm.provision(service2) is True
        
        # Third provision should fail
        service3 = Service("S3", ServiceType.OTN_CIRCUIT, "D1", "D2", 10.0)
        assert dwdm.provision(service3) is False
        assert len(dwdm.active_wavelengths) == 2
    
    def test_dwdm_calculate_available_capacity_full(self):
        """Test capacity calculation when no wavelengths are used"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80)
        
        available = dwdm.calculate_available_capacity()
        
        assert available == 100.0
    
    def test_dwdm_calculate_available_capacity_partial(self):
        """Test capacity calculation with partial wavelength usage"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80)
        
        # Use 40 wavelengths (50%)
        for i in range(40):
            service = Service(f"S{i}", ServiceType.OTN_CIRCUIT, "D1", "D2", 1.0)
            dwdm.provision(service)
        
        available = dwdm.calculate_available_capacity()
        
        assert available == 50.0
    
    def test_dwdm_calculate_available_capacity_empty(self):
        """Test capacity calculation when all wavelengths are used"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80)
        
        # Use all wavelengths
        for i in range(80):
            service = Service(f"S{i}", ServiceType.OTN_CIRCUIT, "D1", "D2", 1.0)
            dwdm.provision(service)
        
        available = dwdm.calculate_available_capacity()
        
        assert available == 0.0


class TestMPLSRouter:
    """Test MPLS router specific functionality"""
    
    def test_mpls_router_initialization(self):
        """Test MPLS router is initialized correctly"""
        router = MPLSRouter("R1", "Router1", 100.0, location="Site B")
        
        assert router.id == "R1"
        assert router.name == "Router1"
        assert router.device_type == DeviceType.MPLS
        assert router.capacity == 100.0
        assert router.location == "Site B"
        assert router.status == DeviceStatus.ACTIVE
        assert router.utilization == 0.0
        assert router.label_table == {}
        assert router.vpn_instances == []
    
    def test_mpls_provision_within_capacity(self):
        """Test provisioning succeeds when bandwidth is within capacity"""
        router = MPLSRouter("R1", "Router1", 100.0)
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 50.0)
        
        result = router.provision(service)
        
        assert result is True
        assert "S1" in router.vpn_instances
        assert router.utilization == 50.0
    
    def test_mpls_provision_multiple_services(self):
        """Test provisioning multiple services updates utilization correctly"""
        router = MPLSRouter("R1", "Router1", 100.0)
        
        service1 = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 30.0)
        service2 = Service("S2", ServiceType.MPLS_VPN, "R1", "R3", 20.0)
        
        assert router.provision(service1) is True
        assert router.provision(service2) is True
        
        assert len(router.vpn_instances) == 2
        assert router.utilization == 50.0
    
    def test_mpls_provision_fails_when_exceeds_capacity(self):
        """Test provisioning fails when bandwidth exceeds available capacity"""
        router = MPLSRouter("R1", "Router1", 100.0)
        
        # Use 80 Gbps
        service1 = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 80.0)
        assert router.provision(service1) is True
        
        # Try to provision 30 Gbps (exceeds remaining 20 Gbps)
        service2 = Service("S2", ServiceType.MPLS_VPN, "R1", "R3", 30.0)
        assert router.provision(service2) is False
        
        assert len(router.vpn_instances) == 1
        assert router.utilization == 80.0
    
    def test_mpls_provision_exact_capacity(self):
        """Test provisioning succeeds when using exact remaining capacity"""
        router = MPLSRouter("R1", "Router1", 100.0)
        
        service1 = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 70.0)
        service2 = Service("S2", ServiceType.MPLS_VPN, "R1", "R3", 30.0)
        
        assert router.provision(service1) is True
        assert router.provision(service2) is True
        assert router.utilization == 100.0
    
    def test_mpls_calculate_available_capacity_full(self):
        """Test capacity calculation when router is unused"""
        router = MPLSRouter("R1", "Router1", 100.0)
        
        available = router.calculate_available_capacity()
        
        assert available == 100.0
    
    def test_mpls_calculate_available_capacity_partial(self):
        """Test capacity calculation with partial utilization"""
        router = MPLSRouter("R1", "Router1", 100.0)
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 40.0)
        router.provision(service)
        
        available = router.calculate_available_capacity()
        
        assert available == 60.0
    
    def test_mpls_calculate_available_capacity_empty(self):
        """Test capacity calculation when fully utilized"""
        router = MPLSRouter("R1", "Router1", 100.0)
        service = Service("S1", ServiceType.MPLS_VPN, "R1", "R2", 100.0)
        router.provision(service)
        
        available = router.calculate_available_capacity()
        
        assert available == 0.0


class TestGPONDevice:
    """Test GPON device specific functionality"""
    
    def test_gpon_olt_initialization(self):
        """Test GPON OLT is initialized correctly"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True, location="Site C")
        
        assert olt.id == "G1"
        assert olt.name == "OLT1"
        assert olt.device_type == DeviceType.GPON_OLT
        assert olt.capacity == 10.0
        assert olt.location == "Site C"
        assert olt.status == DeviceStatus.ACTIVE
        assert olt.is_olt is True
        assert olt.connected_onts == []
        assert olt.split_ratio == 32
    
    def test_gpon_ont_initialization(self):
        """Test GPON ONT is initialized correctly"""
        ont = GPONDevice("G2", "ONT1", 1.0, is_olt=False, location="Customer Site")
        
        assert ont.id == "G2"
        assert ont.name == "ONT1"
        assert ont.device_type == DeviceType.GPON_ONT
        assert ont.capacity == 1.0
        assert ont.is_olt is False
        assert ont.connected_onts is None
        assert ont.split_ratio is None
    
    def test_gpon_olt_provision_within_split_ratio(self):
        """Test OLT provisioning succeeds within split ratio"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        service = Service("S1", ServiceType.GPON_ACCESS, "G1", "G2", 1.0)
        
        result = olt.provision(service)
        
        assert result is True
    
    def test_gpon_olt_provision_at_split_ratio_limit(self):
        """Test OLT provisioning fails when split ratio is reached"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        olt.split_ratio = 2  # Set low split ratio for testing
        
        # Add 2 ONTs
        olt.connected_onts.append("ONT1")
        olt.connected_onts.append("ONT2")
        
        service = Service("S1", ServiceType.GPON_ACCESS, "G1", "G3", 1.0)
        result = olt.provision(service)
        
        assert result is False
    
    def test_gpon_ont_provision_fails(self):
        """Test ONT provisioning returns False (ONTs don't provision)"""
        ont = GPONDevice("G2", "ONT1", 1.0, is_olt=False)
        service = Service("S1", ServiceType.GPON_ACCESS, "G1", "G2", 1.0)
        
        result = ont.provision(service)
        
        assert result is False
    
    def test_gpon_olt_calculate_available_capacity_full(self):
        """Test OLT capacity calculation when no ONTs connected"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        
        available = olt.calculate_available_capacity()
        
        assert available == 10.0
    
    def test_gpon_olt_calculate_available_capacity_partial(self):
        """Test OLT capacity calculation with partial ONT connections"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        olt.split_ratio = 32
        
        # Connect 16 ONTs (50%)
        for i in range(16):
            olt.connected_onts.append(f"ONT{i}")
        
        available = olt.calculate_available_capacity()
        
        assert available == 5.0
    
    def test_gpon_olt_calculate_available_capacity_empty(self):
        """Test OLT capacity calculation when all ONT slots used"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        olt.split_ratio = 32
        
        # Connect all 32 ONTs
        for i in range(32):
            olt.connected_onts.append(f"ONT{i}")
        
        available = olt.calculate_available_capacity()
        
        assert available == 0.0
    
    def test_gpon_ont_calculate_available_capacity(self):
        """Test ONT capacity calculation based on utilization"""
        ont = GPONDevice("G2", "ONT1", 1.0, is_olt=False)
        ont.utilization = 0.5
        
        available = ont.calculate_available_capacity()
        
        assert available == 0.5


class TestDeviceSerialization:
    """Test device to_dict() serialization"""
    
    def test_dwdm_device_to_dict(self):
        """Test DWDM device serialization to dictionary"""
        dwdm = DWDMDevice("D1", "DWDM1", 100.0, wavelengths=80, location="Site A")
        
        result = dwdm.to_dict()
        
        assert result["id"] == "D1"
        assert result["name"] == "DWDM1"
        assert result["type"] == "DWDM"
        assert result["capacity"] == 100.0
        assert result["location"] == "Site A"
        assert result["status"] == "active"
        assert result["utilization"] == 0.0
    
    def test_mpls_router_to_dict(self):
        """Test MPLS router serialization to dictionary"""
        router = MPLSRouter("R1", "Router1", 100.0, location="Site B")
        router.status = DeviceStatus.MAINTENANCE
        router.utilization = 45.5
        
        result = router.to_dict()
        
        assert result["id"] == "R1"
        assert result["name"] == "Router1"
        assert result["type"] == "MPLS"
        assert result["capacity"] == 100.0
        assert result["location"] == "Site B"
        assert result["status"] == "maintenance"
        assert result["utilization"] == 45.5
    
    def test_gpon_olt_to_dict(self):
        """Test GPON OLT serialization to dictionary"""
        olt = GPONDevice("G1", "OLT1", 10.0, is_olt=True)
        
        result = olt.to_dict()
        
        assert result["id"] == "G1"
        assert result["name"] == "OLT1"
        assert result["type"] == "GPON_OLT"
        assert result["capacity"] == 10.0
        assert result["status"] == "active"
    
    def test_gpon_ont_to_dict(self):
        """Test GPON ONT serialization to dictionary"""
        ont = GPONDevice("G2", "ONT1", 1.0, is_olt=False)
        
        result = ont.to_dict()
        
        assert result["id"] == "G2"
        assert result["name"] == "ONT1"
        assert result["type"] == "GPON_ONT"
        assert result["capacity"] == 1.0
    
    def test_device_to_dict_with_none_location(self):
        """Test device serialization with None location"""
        router = MPLSRouter("R1", "Router1", 100.0)
        
        result = router.to_dict()
        
        assert result["location"] is None
