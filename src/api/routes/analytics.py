"""Analytics and optimization API endpoints"""

from fastapi import APIRouter, Depends, HTTPException, status
import logging

from src.api.app import get_neo4j_repository, get_metrics_repository
from src.api.models import (
    AnalyticsStatusResponse, MetricsResponse, PathOptimizationResponse
)
from src.api.dependencies import require_user_or_admin
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.models.user import User

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["Analytics"])


@router.get("/analytics/status", response_model=AnalyticsStatusResponse)
async def get_analytics_status(
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get aggregated network analytics and status
    
    Returns summary statistics including:
    - Total number of devices
    - Number of active devices
    - Total number of links
    - Total number of services
    - Average network utilization
    """
    try:
        logger.info("Fetching analytics status")
        
        # Get topology data
        topology_data = neo4j_repo.get_topology_json()
        devices = topology_data.get("devices", [])
        links = topology_data.get("links", [])
        
        # Get services count
        services = neo4j_repo.get_all_services()
        
        # Calculate statistics
        total_devices = len(devices)
        active_devices = sum(1 for d in devices if d.get("status") == "active")
        total_links = len(links)
        total_services = len(services)
        
        # Calculate average utilization
        if devices:
            total_utilization = sum(d.get("utilization", 0.0) for d in devices)
            average_utilization = total_utilization / total_devices
        else:
            average_utilization = 0.0
        
        logger.info(f"Analytics: {total_devices} devices, {active_devices} active, {total_links} links, {total_services} services")
        
        return AnalyticsStatusResponse(
            total_devices=total_devices,
            active_devices=active_devices,
            total_links=total_links,
            total_services=total_services,
            average_utilization=round(average_utilization, 2)
        )
    
    except Exception as e:
        logger.error(f"Error fetching analytics status: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch analytics status",
                    "details": {"error": str(e)}
                }
            }
        )


@router.get("/optimization/path/{source}/{target}", response_model=PathOptimizationResponse)
async def find_optimal_path(
    source: str,
    target: str,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Find optimal path between two devices
    
    - **source**: Source device ID
    - **target**: Target device ID
    
    Returns the optimal path considering utilization and latency
    """
    try:
        logger.info(f"Finding optimal path from {source} to {target}")
        
        # Verify devices exist
        source_device = neo4j_repo.get_device(source)
        if not source_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Source device not found: {source}",
                        "details": {"device_id": source}
                    }
                }
            )
        
        target_device = neo4j_repo.get_device(target)
        if not target_device:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "DEVICE_NOT_FOUND",
                        "message": f"Target device not found: {target}",
                        "details": {"device_id": target}
                    }
                }
            )
        
        # Find optimal path
        path_result = neo4j_repo.find_optimal_path(source, target)
        
        if not path_result:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail={
                    "error": {
                        "code": "PATH_NOT_FOUND",
                        "message": f"No path found between {source} and {target}",
                        "details": {"source": source, "target": target}
                    }
                }
            )
        
        logger.info(f"Optimal path found: {path_result['path']}")
        
        return PathOptimizationResponse(
            source=source,
            target=target,
            path=path_result["path"],
            total_latency=path_result.get("total_latency", 0.0),
            available_bandwidth=path_result.get("available_bandwidth", 0.0)
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error finding optimal path: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to find optimal path",
                    "details": {"error": str(e)}
                }
            }
        )


@router.get("/analytics/device/{device_id}/metrics", response_model=MetricsResponse)
async def get_device_metrics(
    device_id: str,
    limit: int = 100,
    neo4j_repo: Neo4jRepository = Depends(get_neo4j_repository),
    metrics_repo: MetricsRepository = Depends(get_metrics_repository),
    current_user: User = Depends(require_user_or_admin)
):
    """
    Get historical metrics for a specific device
    
    - **device_id**: ID of the device
    - **limit**: Maximum number of metrics to return (default: 100)
    """
    try:
        logger.info(f"Fetching metrics for device: {device_id}")
        
        # Verify device exists
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
        
        # Get metrics from repository
        metrics = metrics_repo.get_device_metrics(device_id, limit=limit)
        
        logger.info(f"Retrieved {len(metrics)} metrics for device {device_id}")
        
        return MetricsResponse(
            device_id=device_id,
            metrics=metrics
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching device metrics: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": {
                    "code": "INTERNAL_ERROR",
                    "message": "Failed to fetch device metrics",
                    "details": {"error": str(e)}
                }
            }
        )
