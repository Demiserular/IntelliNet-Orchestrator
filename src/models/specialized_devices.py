from typing import Optional, List
from .device import Device, DeviceType
from .service import Service


class DWDMDevice(Device):
    """Dense Wavelength Division Multiplexing device"""
    
    def __init__(self, id: str, name: str, capacity: float, 
                 wavelengths: int = 80, location: Optional[str] = None):
        super().__init__(id, name, DeviceType.DWDM, capacity, location)
        self.wavelengths = wavelengths
        self.active_wavelengths: List[str] = []
    
    def provision(self, service: Service) -> bool:
        """
        Provision a service on this DWDM device by allocating a wavelength
        
        Args:
            service: Service object to provision
            
        Returns:
            bool: True if wavelength available and allocated, False otherwise
        """
        if len(self.active_wavelengths) < self.wavelengths:
            wavelength_id = f"λ{len(self.active_wavelengths) + 1}"
            self.active_wavelengths.append(wavelength_id)
            return True
        return False
    
    def calculate_available_capacity(self) -> float:
        """
        Calculate remaining capacity based on available wavelengths
        
        Returns:
            float: Available capacity in Gbps
        """
        used = (len(self.active_wavelengths) / self.wavelengths) * self.capacity
        return self.capacity - used


class MPLSRouter(Device):
    """MPLS Label Switching Router"""
    
    def __init__(self, id: str, name: str, capacity: float, 
                 location: Optional[str] = None):
        super().__init__(id, name, DeviceType.MPLS, capacity, location)
        self.label_table = {}
        self.vpn_instances: List[str] = []
    
    def provision(self, service: Service) -> bool:
        """
        Provision a service on this MPLS router
        
        Args:
            service: Service object to provision
            
        Returns:
            bool: True if capacity available and service provisioned, False otherwise
        """
        if service.bandwidth <= self.calculate_available_capacity():
            self.vpn_instances.append(service.id)
            self.utilization += service.bandwidth
            return True
        return False
    
    def calculate_available_capacity(self) -> float:
        """
        Calculate remaining capacity based on current utilization
        
        Returns:
            float: Available capacity in Gbps
        """
        return self.capacity - self.utilization


class GPONDevice(Device):
    """GPON Optical Line Terminal or Optical Network Terminal"""
    
    def __init__(self, id: str, name: str, capacity: float, 
                 is_olt: bool = True, location: Optional[str] = None):
        device_type = DeviceType.GPON_OLT if is_olt else DeviceType.GPON_ONT
        super().__init__(id, name, device_type, capacity, location)
        self.is_olt = is_olt
        self.connected_onts: Optional[List[str]] = [] if is_olt else None
        self.split_ratio: Optional[int] = 32 if is_olt else None
    
    def provision(self, service: Service) -> bool:
        """
        Provision a service on this GPON device
        
        Args:
            service: Service object to provision
            
        Returns:
            bool: True if provisioning successful, False otherwise
        """
        if self.is_olt and self.connected_onts is not None and self.split_ratio is not None:
            if len(self.connected_onts) < self.split_ratio:
                return True
        return False
    
    def calculate_available_capacity(self) -> float:
        """
        Calculate remaining capacity
        
        Returns:
            float: Available capacity in Gbps
        """
        if self.is_olt and self.connected_onts is not None and self.split_ratio is not None:
            return self.capacity * (1 - len(self.connected_onts) / self.split_ratio)
        return self.capacity - self.utilization
