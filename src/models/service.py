from enum import Enum
from typing import Dict, Any, Optional, List


class ServiceType(Enum):
    """Enumeration of service types"""
    MPLS_VPN = "MPLS_VPN"
    OTN_CIRCUIT = "OTN_CIRCUIT"
    GPON_ACCESS = "GPON_ACCESS"
    FTTH_SERVICE = "FTTH_SERVICE"


class ServiceStatus(Enum):
    """Enumeration of service status values"""
    PENDING = "pending"
    ACTIVE = "active"
    FAILED = "failed"
    DECOMMISSIONED = "decommissioned"


class Service:
    """Represents a network service"""
    
    def __init__(self, id: str, service_type: ServiceType, 
                 source_device_id: str, target_device_id: str,
                 bandwidth: float, latency_requirement: Optional[float] = None):
        self.id = id
        self.service_type = service_type
        self.source_device_id = source_device_id
        self.target_device_id = target_device_id
        self.bandwidth = bandwidth
        self.latency_requirement = latency_requirement
        self.status = ServiceStatus.PENDING
        self.path: List[str] = []  # List of device IDs in the service path
        self.created_at = None
        self.activated_at = None
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert service to dictionary for JSON serialization
        
        Returns:
            Dict[str, Any]: Dictionary representation of service
        """
        return {
            "id": self.id,
            "service_type": self.service_type.value,
            "source": self.source_device_id,
            "target": self.target_device_id,
            "bandwidth": self.bandwidth,
            "latency_requirement": self.latency_requirement,
            "status": self.status.value,
            "path": self.path
        }
