"""
Service Orchestrator for network service provisioning

This module provides the ServiceOrchestrator class that coordinates
service provisioning workflows by integrating Neo4j topology management,
metrics recording, and rule-based validation.
"""

import logging
from typing import Tuple, Optional
from datetime import datetime

from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.rule_engine import RuleEngine
from src.models.service import Service, ServiceStatus

logger = logging.getLogger(__name__)


class ServiceOrchestrator:
    """Orchestrates service provisioning workflow"""
    
    def __init__(self, neo4j_repo: Neo4jRepository, 
                 metrics_repo: MetricsRepository,
                 rule_engine: RuleEngine):
        """
        Initialize ServiceOrchestrator with dependency injection
        
        Args:
            neo4j_repo: Neo4jRepository instance for topology management
            metrics_repo: MetricsRepository instance for metrics recording
            rule_engine: RuleEngine instance for service validation
        """
        self.neo4j_repo = neo4j_repo
        self.metrics_repo = metrics_repo
        self.rule_engine = rule_engine
        
        logger.info("ServiceOrchestrator initialized with dependencies")

    def provision_service(self, service: Service) -> Tuple[bool, str]:
        """
        Provision a network service with complete workflow
        
        This method:
        1. Finds a path between source and target devices
        2. Validates the service against all enabled rules
        3. Creates service nodes and relationships in Neo4j
        4. Updates device and link utilization metrics
        5. Logs the provisioning event
        
        Args:
            service: Service object to provision
            
        Returns:
            Tuple[bool, str]: (success, message)
                - success: True if provisioning succeeded, False otherwise
                - message: Descriptive message about the result
        """
        logger.info(f"Starting provisioning workflow for service {service.id}")
        
        # Step 1: Find path between source and target
        path = self.neo4j_repo.find_shortest_path(
            service.source_device_id,
            service.target_device_id
        )
        
        if not path:
            error_msg = f"No path found between {service.source_device_id} and {service.target_device_id}"
            logger.error(f"Service {service.id}: {error_msg}")
            service.status = ServiceStatus.FAILED
            self.metrics_repo.record_service_log(
                service.id,
                "provisioning_failed",
                error_msg
            )
            return False, error_msg
        
        service.path = path
        logger.info(f"Service {service.id}: Found path with {len(path)} devices")
        
        # Step 2: Validate service against rules for each device in path
        violations = []
        for device_id in path:
            device_data = self.neo4j_repo.get_device(device_id)
            if not device_data:
                error_msg = f"Device {device_id} not found in topology"
                logger.error(f"Service {service.id}: {error_msg}")
                violations.append(error_msg)
                continue
            
            # Validate against rule engine (simplified - passing None for link)
            is_valid, device_violations = self.rule_engine.evaluate(service, None, None)
            if not is_valid:
                violations.extend(device_violations)
        
        if violations:
            error_msg = f"Validation failed: {'; '.join(violations)}"
            logger.error(f"Service {service.id}: {error_msg}")
            service.status = ServiceStatus.FAILED
            self.metrics_repo.record_service_log(
                service.id,
                "validation_failed",
                error_msg
            )
            return False, error_msg
        
        logger.info(f"Service {service.id}: Validation passed")
        
        # Step 3: Create service in Neo4j
        success = self._create_service_in_neo4j(service)
        if not success:
            error_msg = "Failed to create service in Neo4j"
            logger.error(f"Service {service.id}: {error_msg}")
            service.status = ServiceStatus.FAILED
            self.metrics_repo.record_service_log(
                service.id,
                "creation_failed",
                error_msg
            )
            return False, error_msg
        
        # Step 4: Update device and link utilization metrics
        self._update_utilization_metrics(service)
        
        # Step 5: Update service status and log success
        service.status = ServiceStatus.ACTIVE
        service.activated_at = datetime.now().isoformat()
        
        success_msg = f"Service {service.id} provisioned successfully on path: {' -> '.join(path)}"
        logger.info(success_msg)
        
        self.metrics_repo.record_service_log(
            service.id,
            "provisioned",
            success_msg
        )
        
        return True, success_msg
    
    def _create_service_in_neo4j(self, service: Service) -> bool:
        """
        Create service node and relationships in Neo4j
        
        Args:
            service: Service object to create
            
        Returns:
            bool: True if creation succeeded, False otherwise
        """
        if not self.neo4j_repo.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.neo4j_repo.driver.session() as session:
                # Create service node
                create_service_query = """
                CREATE (s:Service {
                    id: $id,
                    service_type: $service_type,
                    source: $source,
                    target: $target,
                    bandwidth: $bandwidth,
                    latency_requirement: $latency_requirement,
                    status: $status,
                    path: $path,
                    activated_at: $activated_at
                })
                RETURN s
                """
                
                service_params = {
                    "id": service.id,
                    "service_type": service.service_type.value,
                    "source": service.source_device_id,
                    "target": service.target_device_id,
                    "bandwidth": service.bandwidth,
                    "latency_requirement": service.latency_requirement,
                    "status": service.status.value,
                    "path": service.path,
                    "activated_at": service.activated_at
                }
                
                result = session.run(create_service_query, **service_params)
                if not result.single():
                    return False
                
                # Create USES relationships between service and devices in path
                for device_id in service.path:
                    uses_query = """
                    MATCH (s:Service {id: $service_id})
                    MATCH (d:Device {id: $device_id})
                    CREATE (s)-[:USES]->(d)
                    """
                    session.run(uses_query, service_id=service.id, device_id=device_id)
                
                logger.info(f"Created service {service.id} in Neo4j with {len(service.path)} device relationships")
                return True
                
        except Exception as e:
            logger.error(f"Error creating service in Neo4j: {e}", exc_info=True)
            return False
    
    def _update_utilization_metrics(self, service: Service) -> None:
        """
        Update device and link utilization metrics after service provisioning
        
        Args:
            service: Provisioned service
        """
        # Record metrics for each device in the path
        for device_id in service.path:
            device_data = self.neo4j_repo.get_device(device_id)
            if device_data:
                # Calculate new utilization (simplified - would need actual calculation)
                current_utilization = device_data.get("utilization", 0.0)
                
                self.metrics_repo.record_device_metric(
                    device_id,
                    current_utilization,
                    device_data.get("status", "active")
                )
                
                logger.debug(f"Recorded metric for device {device_id}")
        
        # Record metrics for links in the path
        for i in range(len(service.path) - 1):
            source_id = service.path[i]
            target_id = service.path[i + 1]
            
            # Get links between consecutive devices
            links = self.neo4j_repo.get_links_for_device(source_id)
            for link in links:
                if link.get("target") == target_id or link.get("source") == target_id:
                    self.metrics_repo.record_link_metric(
                        link.get("id", f"{source_id}-{target_id}"),
                        link.get("utilization", 0.0),
                        link.get("latency", 0.0)
                    )
                    logger.debug(f"Recorded metric for link {link.get('id')}")

    def decommission_service(self, service_id: str) -> Tuple[bool, str]:
        """
        Decommission a network service
        
        This method:
        1. Retrieves the service from Neo4j
        2. Removes service node and relationships from Neo4j
        3. Updates device utilization metrics
        4. Logs the decommissioning event
        
        Args:
            service_id: Unique identifier of the service to decommission
            
        Returns:
            Tuple[bool, str]: (success, message)
                - success: True if decommissioning succeeded, False otherwise
                - message: Descriptive message about the result
        """
        logger.info(f"Starting decommissioning workflow for service {service_id}")
        
        # Step 1: Retrieve service from Neo4j
        service_data = self._get_service_from_neo4j(service_id)
        if not service_data:
            error_msg = f"Service {service_id} not found"
            logger.error(error_msg)
            return False, error_msg
        
        # Extract path for metrics update
        path = service_data.get("path", [])
        
        # Step 2: Remove service from Neo4j
        success = self._delete_service_from_neo4j(service_id)
        if not success:
            error_msg = f"Failed to delete service {service_id} from Neo4j"
            logger.error(error_msg)
            return False, error_msg
        
        logger.info(f"Service {service_id}: Removed from Neo4j")
        
        # Step 3: Update device utilization metrics
        for device_id in path:
            device_data = self.neo4j_repo.get_device(device_id)
            if device_data:
                self.metrics_repo.record_device_metric(
                    device_id,
                    device_data.get("utilization", 0.0),
                    device_data.get("status", "active")
                )
                logger.debug(f"Updated metrics for device {device_id} after decommissioning")
        
        # Step 4: Log service decommissioning event
        success_msg = f"Service {service_id} decommissioned successfully"
        logger.info(success_msg)
        
        self.metrics_repo.record_service_log(
            service_id,
            "decommissioned",
            success_msg
        )
        
        return True, success_msg
    
    def _get_service_from_neo4j(self, service_id: str) -> Optional[dict]:
        """
        Retrieve service data from Neo4j
        
        Args:
            service_id: Unique identifier of the service
            
        Returns:
            Optional[dict]: Service properties as dictionary, or None if not found
        """
        if not self.neo4j_repo.driver:
            logger.error("Neo4j driver not initialized")
            return None
        
        try:
            with self.neo4j_repo.driver.session() as session:
                query = """
                MATCH (s:Service {id: $service_id})
                RETURN s
                """
                
                result = session.run(query, service_id=service_id)
                record = result.single()
                
                if record:
                    return dict(record["s"])
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving service {service_id}: {e}", exc_info=True)
            return None
    
    def _delete_service_from_neo4j(self, service_id: str) -> bool:
        """
        Delete service node and all its relationships from Neo4j
        
        Args:
            service_id: Unique identifier of the service
            
        Returns:
            bool: True if deletion succeeded, False otherwise
        """
        if not self.neo4j_repo.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.neo4j_repo.driver.session() as session:
                query = """
                MATCH (s:Service {id: $service_id})
                DETACH DELETE s
                RETURN count(s) as deleted_count
                """
                
                result = session.run(query, service_id=service_id)
                record = result.single()
                
                deleted = record and record["deleted_count"] > 0
                if deleted:
                    logger.info(f"Deleted service {service_id} from Neo4j")
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting service {service_id}: {e}", exc_info=True)
            return False
