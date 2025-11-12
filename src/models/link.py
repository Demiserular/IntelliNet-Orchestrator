from enum import Enum
from typing import Dict, Any


class LinkType(Enum):
    """Enumeration of link types"""
    FIBER = "fiber"
    ETHERNET = "ethernet"
    WIRELESS = "wireless"


class Link:
    """Represents a connection between two devices"""
    
    def __init__(self, id: str, source_device_id: str, target_device_id: str,
                 bandwidth: float, link_type: LinkType, latency: float = 0.0):
        self.id = id
        self.source_device_id = source_device_id
        self.target_device_id = target_device_id
        self.bandwidth = bandwidth  # in Gbps
        self.link_type = link_type
        self.latency = latency  # in ms
        self.utilization = 0.0
        self.status = "active"
    
    def calculate_available_bandwidth(self) -> float:
        """
        Calculate available bandwidth on this link
        
        Returns:
            float: Available bandwidth in Gbps
        """
        return self.bandwidth * (1 - self.utilization)
    
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert link to dictionary for JSON serialization
        
        Returns:
            Dict[str, Any]: Dictionary representation of link
        """
        return {
            "id": self.id,
            "source": self.source_device_id,
            "target": self.target_device_id,
            "bandwidth": self.bandwidth,
            "type": self.link_type.value,
            "latency": self.latency,
            "utilization": self.utilization,
            "status": self.status
        }
