"""Pydantic models for API request/response validation"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class DeviceCreate(BaseModel):
    """Request model for creating a device"""
    id: str = Field(..., description="Unique device identifier")
    name: str = Field(..., description="Device name")
    type: str = Field(..., description="Device type (DWDM, OTN, SONET, MPLS, GPON_OLT, GPON_ONT, FTTH)")
    capacity: float = Field(..., gt=0, description="Device capacity in Gbps")
    location: Optional[str] = Field(None, description="Physical location")
    
    # Device-specific optional fields
    wavelengths: Optional[int] = Field(None, description="Number of wavelengths for DWDM devices")
    is_olt: Optional[bool] = Field(None, description="Whether GPON device is OLT (True) or ONT (False)")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "R1",
                "name": "Core Router 1",
                "type": "MPLS",
                "capacity": 100.0,
                "location": "DataCenter-A"
            }
        }


class DeviceResponse(BaseModel):
    """Response model for device data"""
    id: str
    name: str
    type: str
    capacity: float
    location: Optional[str] = None
    status: str
    utilization: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "R1",
                "name": "Core Router 1",
                "type": "MPLS",
                "capacity": 100.0,
                "location": "DataCenter-A",
                "status": "active",
                "utilization": 0.0
            }
        }


class LinkCreate(BaseModel):
    """Request model for creating a link"""
    id: str = Field(..., description="Unique link identifier")
    source_device_id: str = Field(..., description="Source device ID")
    target_device_id: str = Field(..., description="Target device ID")
    bandwidth: float = Field(..., gt=0, description="Link bandwidth in Gbps")
    type: str = Field(..., description="Link type (fiber, ethernet, wireless)")
    latency: float = Field(default=0.0, ge=0, description="Link latency in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "L1",
                "source_device_id": "R1",
                "target_device_id": "R2",
                "bandwidth": 10.0,
                "type": "fiber",
                "latency": 5.0
            }
        }


class LinkResponse(BaseModel):
    """Response model for link data"""
    id: str
    source: str
    target: str
    bandwidth: float
    type: str
    latency: float
    utilization: float
    status: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "L1",
                "source": "R1",
                "target": "R2",
                "bandwidth": 10.0,
                "type": "fiber",
                "latency": 5.0,
                "utilization": 0.0,
                "status": "active"
            }
        }


class ServiceProvisionRequest(BaseModel):
    """Request model for provisioning a service"""
    id: str = Field(..., description="Unique service identifier")
    service_type: str = Field(..., description="Service type (MPLS_VPN, OTN_CIRCUIT, GPON_ACCESS, FTTH_SERVICE)")
    source_device_id: str = Field(..., description="Source device ID")
    target_device_id: str = Field(..., description="Target device ID")
    bandwidth: float = Field(..., gt=0, description="Required bandwidth in Gbps")
    latency_requirement: Optional[float] = Field(None, ge=0, description="Maximum acceptable latency in milliseconds")
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "S1",
                "service_type": "MPLS_VPN",
                "source_device_id": "R1",
                "target_device_id": "R2",
                "bandwidth": 5.0,
                "latency_requirement": 10.0
            }
        }


class ServiceResponse(BaseModel):
    """Response model for service data"""
    id: str
    service_type: str
    source_device_id: str
    target_device_id: str
    bandwidth: float
    latency_requirement: Optional[float] = None
    status: str
    path: List[str]
    created_at: Optional[datetime] = None
    activated_at: Optional[datetime] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "id": "S1",
                "service_type": "MPLS_VPN",
                "source_device_id": "R1",
                "target_device_id": "R2",
                "bandwidth": 5.0,
                "latency_requirement": 10.0,
                "status": "active",
                "path": ["R1", "R2"],
                "created_at": "2024-01-01T00:00:00",
                "activated_at": "2024-01-01T00:00:01"
            }
        }


class TopologyResponse(BaseModel):
    """Response model for complete topology"""
    devices: List[DeviceResponse]
    links: List[LinkResponse]
    
    class Config:
        json_schema_extra = {
            "example": {
                "devices": [
                    {
                        "id": "R1",
                        "name": "Core Router 1",
                        "type": "MPLS",
                        "capacity": 100.0,
                        "location": "DataCenter-A",
                        "status": "active",
                        "utilization": 0.0
                    }
                ],
                "links": [
                    {
                        "id": "L1",
                        "source": "R1",
                        "target": "R2",
                        "bandwidth": 10.0,
                        "type": "fiber",
                        "latency": 5.0,
                        "utilization": 0.0,
                        "status": "active"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Standardized error response"""
    error: dict
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": {
                    "code": "VALIDATION_ERROR",
                    "message": "Service bandwidth exceeds device capacity",
                    "details": {
                        "rule_id": "BW001",
                        "requested_bandwidth": 100,
                        "available_capacity": 50
                    }
                }
            }
        }


class SuccessResponse(BaseModel):
    """Standardized success response"""
    success: bool
    message: str
    data: Optional[dict] = None
    
    class Config:
        json_schema_extra = {
            "example": {
                "success": True,
                "message": "Device created successfully",
                "data": {"id": "R1"}
            }
        }


class MetricsResponse(BaseModel):
    """Response model for device metrics"""
    device_id: str
    metrics: List[dict]
    
    class Config:
        json_schema_extra = {
            "example": {
                "device_id": "R1",
                "metrics": [
                    {
                        "timestamp": "2024-01-01T00:00:00",
                        "utilization": 0.5,
                        "status": "active"
                    }
                ]
            }
        }


class AnalyticsStatusResponse(BaseModel):
    """Response model for analytics status"""
    total_devices: int
    active_devices: int
    total_links: int
    total_services: int
    average_utilization: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "total_devices": 10,
                "active_devices": 8,
                "total_links": 15,
                "total_services": 5,
                "average_utilization": 0.45
            }
        }


class PathOptimizationResponse(BaseModel):
    """Response model for path optimization"""
    source: str
    target: str
    path: List[str]
    total_latency: float
    available_bandwidth: float
    
    class Config:
        json_schema_extra = {
            "example": {
                "source": "R1",
                "target": "R3",
                "path": ["R1", "R2", "R3"],
                "total_latency": 15.0,
                "available_bandwidth": 8.0
            }
        }


class LoginRequest(BaseModel):
    """Request model for user login"""
    username: str = Field(..., description="Username")
    password: str = Field(..., description="Password")
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "password": "admin123"
            }
        }


class TokenResponse(BaseModel):
    """Response model for authentication token"""
    access_token: str
    token_type: str = "bearer"
    username: str
    role: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
                "token_type": "bearer",
                "username": "admin",
                "role": "admin"
            }
        }


class UserResponse(BaseModel):
    """Response model for user data"""
    username: str
    role: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: bool = False
    
    class Config:
        json_schema_extra = {
            "example": {
                "username": "admin",
                "role": "admin",
                "email": "admin@intellinet.com",
                "full_name": "System Administrator",
                "disabled": False
            }
        }
