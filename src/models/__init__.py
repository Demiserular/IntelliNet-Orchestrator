# Domain models package

from .device import Device, DeviceType, DeviceStatus
from .link import Link, LinkType
from .service import Service, ServiceType, ServiceStatus
from .specialized_devices import DWDMDevice, MPLSRouter, GPONDevice

__all__ = [
    'Device',
    'DeviceType',
    'DeviceStatus',
    'Link',
    'LinkType',
    'Service',
    'ServiceType',
    'ServiceStatus',
    'DWDMDevice',
    'MPLSRouter',
    'GPONDevice',
]
