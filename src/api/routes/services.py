"""Service provisioning API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
import logging

from src.api.app import get_service_orchestrator, get_neo4j_repository
from src.api.models import (
    ServiceProvisionRequest, ServiceResponse, SuccessResponse
)
from src.api.dependencies import require_admin, require_user_or_admin
from src.services.service_orchestrator import ServiceOrchestrator
from src.repositories.neo4j_repository import Neo4jRepository
from src.models import Service, ServiceType, ServiceStatus
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/service", tags=["Services"])


@router.post("/provision", status_code=status.HTTP_201_CREATED, response_model=ServiceResponse)
async def provision_service(
    request: ServiceProvisionRequest,
    orchestrator: ServiceOrchestrator = Depends(get_service_orchestrator),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Provision a new network service
    
    - **id**: Unique service identifier
    - **service_type**: Service type (MPLS_VPN, OTN_CIRCUIT, GPON_ACCESS, FTTH_SERVICE)
    - **source_device_id**: Source device ID
    - **target_device_id**: Target device ID
    - **bandwidth**: Required bandwidth in Gbps
    - **latency_requirement**: Maximum acceptable latency in milliseconds (optional)
    """
    try:
        logger.info(f"Provisioning service: {request.id}")
        
        # Validate service type
        try:
            service_type = ServiceType(request.service_type)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "INVALID_SERVICE_TYPE",
                        "message": f"Invalid service type: {request.service_type}",
                        "details": {
                            "valid_types": [st.value for st in ServiceType]
                        }
                    }
                }
            )
        
        # Create service instance
        service = Service(
            id=request.id,
            service_type=service_type,
            source_device_id=request.source_device_id,
            target_device_id=request.target_device_id,
            bandwidth=request.bandwidth,
            latency_requirement=request.latency_requirement
        )
        
        # Provision service through orchestrator
        success, message = orchestrator.provision_service(service)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "error": {
                        "code": "PROVISIONING_FAILED",
                        "message": message,
                        "details": {"service_id": request.id}
                    }
                }
            )
        
        logger.info(f"Service provisioned successfully: {request.id}")
        
        # Return service response
        return ServiceResponse(
            id=service.id,
            service_type=service.service_type.value,
            source_device_id=service.source_device_id,
            target_device_id=service.target_device_id,
            bandwidth=service.bandwidth,
            latency_requirement=service.latency_requirement,
            status=service.status.value,
            path=service.path,
            created_at=service.created_at,
            activated_at=service.activated_at
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error provisioning service: {str(e)}")
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


@router.get("", response_model=list[dict])
async def get_all_services(
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get all services
    
    Returns a list of all provisioned services in the network
    """
    try:
        logger.info("Fetching all services")
        
        services = neo4j_repo.get_all_services()
        
        if not services:
            return []
        
        return services
        
    except Exception as e:
        logger.error(f"Error fetching all services: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "GET_SERVICES_ERROR",
                    "message": "Failed to fetch services",
                    "details": {"exception": str(e)}
                }
            }
        )


@router.get("/{service_id}", response_model=ServiceResponse)
async def get_service(
    service_id: str,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get a specific service by ID
    
    - **service_id**: ID of the service to retrieve
    """
    try:
        logger.info(f"Fetching service: {service_id}")
        
        service_data = neo4j_repo.get_service(service_id)
        
        if not service_data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "SERVICE_NOT_FOUND",
                        "message": f"Service not found: {service_id}",
                        "details": {"service_id": service_id}
                    }
                }
            )
        
        return ServiceResponse(**service_data)
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching service: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch service",
                    "details": {"error": str(e)}
                }
            }
        )


@router.delete("/{service_id}", response_model=SuccessResponse)
async def decommission_service(
    service_id: str,
    orchestrator: ServiceOrchestrator = Depends(get_service_orchestrator),
    current_user: User = Depends(require_admin)
):
    """
    Decommission a service
    
    - **service_id**: ID of the service to decommission
    """
    try:
        logger.info(f"Decommissioning service: {service_id}")
        
        # Decommission service through orchestrator
        success, message = orchestrator.decommission_service(service_id)
        
        if not success:
            if "not found" in message.lower():
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail={
                        "error": {
                            "code": "SERVICE_NOT_FOUND",
                            "message": message,
                            "details": {"service_id": service_id}
                        }
                    }
                )
            else:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail={
                        "error": {
                            "code": "DECOMMISSION_FAILED",
                            "message": message,
                            "details": {"service_id": service_id}
                        }
                    }
                )
        
        logger.info(f"Service decommissioned successfully: {service_id}")
        
        return SuccessResponse(
            success=True,
            message=message,
            data={"id": service_id}
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error decommissioning service: {str(e)}")
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
