"""Topology management API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Annotated
import logging

from src.api.app import get_neo4j_repository, get_metrics_repository
from src.api.models import (
    DeviceCreate, DeviceResponse, LinkCreate, LinkResponse,
    TopologyResponse, SuccessResponse, ErrorResponse
)
from src.api.dependencies import require_admin, require_user_or_admin
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.models import (
    Device, DeviceType, DeviceStatus, Link, LinkType,
    DWDMDevice, MPLSRouter, GPONDevice
)
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/topology", tags=["Topology"])


def create_device_from_request(device_data: DeviceCreate) -> Device:
    """Factory function to create appropriate device instance"""
    try:
        device_type = DeviceType(device_data.type)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": {
                    "code": "INVALID_DEVICE_TYPE",
                    "message": f"Invalid device type: {device_data.type}",
                    "details": {
                        "valid_types": [dt.value for dt in DeviceType]
                    }
                }
            }
        )
    
    # Create specialized device based on type
    if device_type == DeviceType.DWDM:
        wavelengths = device_data.wavelengths or 80
        return DWDMDevice(
            id=device_data.id,
            name=device_data.name,
            capacity=device_data.capacity,
            wavelengths=wavelengths,
            location=device_data.location
        )
    elif device_type == DeviceType.MPLS:
        return MPLSRouter(
            id=device_data.id,
            name=device_data.name,
            capacity=device_data.capacity,
            location=device_data.location
        )
    elif device_type in [DeviceType.GPON_OLT, DeviceType.GPON_ONT]:
        is_olt = device_data.is_olt if device_data.is_olt is not None else (device_type == DeviceType.GPON_OLT)
        return GPONDevice(
            id=device_data.id,
            name=device_data.name,
            capacity=device_data.capacity,
            is_olt=is_olt,
            location=device_data.location
        )
    else:
        # For other types, we'd need to create base Device instances
        # Since Device is abstract, we'll use MPLSRouter as a generic device for now
        return MPLSRouter(
            id=device_data.id,
            name=device_data.name,
            capacity=device_data.capacity,
            location=device_data.location
        )


@router.post("/device", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse)
async def create_device(
    device_data: DeviceCreate,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    metrics_repo: MetricsRepository = Depends(get_metrics_repository),
    current_user: User = Depends(require_admin)
):
    """
    Create a new network device
    
    - **id**: Unique device identifier
    - **name**: Device name
    - **type**: Device type (DWDM, OTN, SONET, MPLS, GPON_OLT, GPON_ONT, FTTH)
    - **capacity**: Device capacity in Gbps
    - **location**: Physical location (optional)
    """
    try:
        logger.info(f"Creating device: {device_data.id}")
        
        # Check if device already exists
        existing_device = neo4j_repo.get_device(device_data.id)
        if existing_device:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail={
                    "error": {
                        "code": "DEVICE_EXISTS",
                        "message": f"Device with ID {device_data.id} already exists",
                        "details": {"device_id": device_data.id}
                    }
                }
            )
        
        # Create device instance
        device = create_device_from_request(device_data)
        
        # Store in Neo4j
        success = neo4j_repo.create_device(device)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DATABASE_ERROR",
                        "message": "Failed to create device in database",
                        "details": {"device_id": device_data.id}
                    }
                }
            )
        
        # Record initial metrics
        metrics_repo.record_device_metric(
            device_id=device.id,
            utilization=device.utilization,
            status=device.status.value
        )
        
        logger.info(f"Device created successfully: {device_data.id}")
        
        return SuccessResponse(
            success=True,
            message="Device created successfully",
            data={"id": device.id, "name": device.name, "type": device.device_type.value}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)}
                }
            }
        )


@router.post("/link", status_code=status.HTTP_201_CREATED, response_model=SuccessResponse)
async def create_link(
    link_data: LinkCreate,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    metrics_repo: MetricsRepository = Depends(get_metrics_repository),
    current_user: User = Depends(require_admin)
):
    """
    Create a link between two devices
    
    - **id**: Unique link identifier
    - **source_device_id**: Source device ID
    - **target_device_id**: Target device ID
    - **bandwidth**: Link bandwidth in Gbps
    - **type**: Link type (fiber, ethernet, wireless)
    - **latency**: Link latency in milliseconds
    """
    try:
        logger.info(f"Creating link: {link_data.id} from {link_data.source_device_id} to {link_data.target_device_id}")
        
        # Verify source and target devices exist
        source_device = neo4j_repo.get_device(link_data.source_device_id)
        if not source_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Source device not found: {link_data.source_device_id}",
                        "details": {"device_id": link_data.source_device_id}
                    }
                }
            )
        
        target_device = neo4j_repo.get_device(link_data.target_device_id)
        if not target_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Target device not found: {link_data.target_device_id}",
                        "details": {"device_id": link_data.target_device_id}
                    }
                }
            )
        
        # Create link instance
        try:
            link_type = LinkType(link_data.type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_LINK_TYPE",
                        "message": f"Invalid link type: {link_data.type}",
                        "details": {
                            "valid_types": [lt.value for lt in LinkType]
                        }
                    }
                }
            )
        
        link = Link(
            id=link_data.id,
            source_device_id=link_data.source_device_id,
            target_device_id=link_data.target_device_id,
            bandwidth=link_data.bandwidth,
            link_type=link_type,
            latency=link_data.latency
        )
        
        # Store in Neo4j
        success = neo4j_repo.create_link(link)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DATABASE_ERROR",
                        "message": "Failed to create link in database",
                        "details": {"link_id": link_data.id}
                    }
                }
            )
        
        # Record initial metrics
        metrics_repo.record_link_metric(
            link_id=link.id,
            utilization=link.utilization,
            latency=link.latency
        )
        
        logger.info(f"Link created successfully: {link_data.id}")
        
        return SuccessResponse(
            success=True,
            message="Link created successfully",
            data={
                "id": link.id,
                "source": link.source_device_id,
                "target": link.target_device_id
            }
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating link: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)}
                }
            }
        )


@router.get("/debug", response_model=dict)
async def debug_topology(
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository)
):
    """
    Debug endpoint to check topology without authentication
    """
    try:
        logger.info("Debug: Fetching topology data")
        
        topology_data = neo4j_repo.get_topology_json()
        device_count = len(topology_data.get("devices", []))
        link_count = len(topology_data.get("links", []))
        
        return {
            "status": "success",
            "device_count": device_count,
            "link_count": link_count,
            "sample_device": topology_data.get("devices", [{}])[0] if device_count > 0 else None
        }
    
    except Exception as e:
        logger.error(f"Debug: Error fetching topology: {str(e)}")
        return {
            "status": "error",
            "error": str(e)
        }


@router.get("/", response_model=TopologyResponse)
async def get_topology(
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get complete network topology
    
    Returns all devices and links in the network as JSON
    """
    try:
        logger.info("Fetching complete topology")
        
        topology_data = neo4j_repo.get_topology_json()
        
        # Convert to response models
        devices = [DeviceResponse(**device) for device in topology_data.get("devices", [])]
        links = [LinkResponse(**link) for link in topology_data.get("links", [])]
        
        logger.info(f"Topology fetched: {len(devices)} devices, {len(links)} links")
        
        return TopologyResponse(devices=devices, links=links)
    
    except Exception as e:
        logger.error(f"Error fetching topology: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch topology",
                    "details": {"error": str(e)}
                }
            }
        )


@router.delete("/device/{device_id}", response_model=SuccessResponse)
async def delete_device(
    device_id: str,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_admin)
):
    """
    Delete a device and all its associated links
    
    - **device_id**: ID of the device to delete
    """
    try:
        logger.info(f"Deleting device: {device_id}")
        
        # Check if device exists
        device = neo4j_repo.get_device(device_id)
        if not device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Device not found: {device_id}",
                        "details": {"device_id": device_id}
                    }
                }
            )
        
        # Delete device (this will also delete associated relationships)
        success = neo4j_repo.delete_device(device_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": {
                        "code": "DATABASE_ERROR",
                        "message": "Failed to delete device from database",
                        "details": {"device_id": device_id}
                    }
                }
            )
        
        logger.info(f"Device deleted successfully: {device_id}")
        
        return SuccessResponse(
            success=True,
            message="Device deleted successfully",
            data={"id": device_id}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "An unexpected error occurred",
                    "details": {"error": str(e)}
                }
            }
        )


@router.get("/device/{device_id}", response_model=DeviceResponse)
async def get_device(
    device_id: str,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get a specific device by ID
    
    - **device_id**: ID of the device to retrieve
    """
    try:
        logger.info(f"Fetching device: {device_id}")
        
        device_data = neo4j_repo.get_device(device_id)
        
        if not device_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Device not found: {device_id}",
                        "details": {"device_id": device_id}
                    }
                }
            )
        
        return DeviceResponse(**device_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch device",
                    "details": {"error": str(e)}
                }
            }
        )
