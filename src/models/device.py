from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from enum import Enum


class DeviceType(Enum):
    """Enumeration of supported device types"""
    DWDM = "DWDM"
    OTN = "OTN"
    SONET = "SONET"
    MPLS = "MPLS"
    GPON_OLT = "GPON_OLT"
    GPON_ONT = "GPON_ONT"
    FTTH = "FTTH"


class DeviceStatus(Enum):
    """Enumeration of device status values"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    MAINTENANCE = "maintenance"
    FAILED = "failed"


class Device(ABC):
    """Base abstract class for all network devices"""
    
    def __init__(self, id: str, name: str, device_type: DeviceType, 
                 capacity: float, location: Optional[str] = None):
        self.id = id
        self.name = name
        self.device_type = device_type
        self.capacity = capacity  # in Gbps
        self.location = location
        self.status = DeviceStatus.ACTIVE
        self.utilization = 0.0
    
    @abstractmethod
    def provision(self, service: 'Service') -> bool:
        """
        Provision a service on this device
        
        Args:
            service: Service object to provision
            
        Returns:
            bool: True if provisioning successful, False otherwise
        """
        pass
    
    @abstractmethod
    def calculate_available_capacity(self) -> float:
        """
        Calculate remaining capacity on this device
        
        Returns:
            float: Available capacity in Gbps
        """
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert device to dictionary for JSON serialization
        
        Returns:
            Dict[str, Any]: Dictionary representation of device
        """
        return {
            "id": self.id,
            "name": self.name,
            "type": self.device_type.value,
            "capacity": self.capacity,
            "location": self.location,
            "status": self.status.value,
            "utilization": self.utilization
        }
