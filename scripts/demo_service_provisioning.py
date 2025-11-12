"""
Service Provisioning Demo Script

This script demonstrates various service provisioning scenarios
including successful provisioning, validation failures, and path optimization.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.rule_engine import RuleEngine
from src.services.service_orchestrator import ServiceOrchestrator
from src.models import ServiceType
from src.models.service import Service
from src.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


def demo_successful_provisioning(orchestrator: ServiceOrchestrator):
    """Demo: Successful service provisioning"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 1: Successful Service Provisioning")
    logger.info("=" * 80)
    
    service = Service(
        id="DEMO-VPN-001",
        service_type=ServiceType.MPLS_VPN,
        source_device_id="EDGE-R1",
        target_device_id="EDGE-R2",
        bandwidth=1.0,
        latency_requirement=100.0
    )
    
    logger.info(f"\nProvisioning service: {service.id}")
    logger.info(f"  Type: {service.service_type.value}")
    logger.info(f"  Source: {service.source_device_id}")
    logger.info(f"  Target: {service.target_device_id}")
    logger.info(f"  Bandwidth: {service.bandwidth} Gbps")
    logger.info(f"  Latency Requirement: {service.latency_requirement} ms")
    
    success, message = orchestrator.provision_service(service)
    
    if success:
        logger.info(f"\n✓ SUCCESS: {message}")
        logger.info(f"  Service Path: {' → '.join(service.path)}")
    else:
        logger.error(f"\n✗ FAILED: {message}")
    
    time.sleep(1)


def demo_bandwidth_validation_failure(orchestrator: ServiceOrchestrator):
    """Demo: Service provisioning fails due to bandwidth constraint"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 2: Bandwidth Validation Failure")
    logger.info("=" * 80)
    
    service = Service(
        id="DEMO-VPN-002",
        service_type=ServiceType.MPLS_VPN,
        source_device_id="EDGE-R1",
        target_device_id="EDGE-R3",
        bandwidth=200.0,  # Exceeds available capacity
        latency_requirement=100.0
    )
    
    logger.info(f"\nProvisioning service with excessive bandwidth: {service.id}")
    logger.info(f"  Requested Bandwidth: {service.bandwidth} Gbps (exceeds capacity)")
    
    success, message = orchestrator.provision_service(service)
    
    if success:
        logger.info(f"\n✓ SUCCESS: {message}")
    else:
        logger.warning(f"\n⚠ EXPECTED FAILURE: {message}")
        logger.info("  This demonstrates the rule engine rejecting invalid requests")
    
    time.sleep(1)


def demo_latency_validation_failure(orchestrator: ServiceOrchestrator):
    """Demo: Service provisioning fails due to latency constraint"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 3: Latency Validation Failure")
    logger.info("=" * 80)
    
    service = Service(
        id="DEMO-VPN-003",
        service_type=ServiceType.MPLS_VPN,
        source_device_id="EDGE-R1",
        target_device_id="EDGE-R2",
        bandwidth=1.0,
        latency_requirement=1.0  # Very strict latency requirement
    )
    
    logger.info(f"\nProvisioning service with strict latency: {service.id}")
    logger.info(f"  Latency Requirement: {service.latency_requirement} ms (very strict)")
    
    success, message = orchestrator.provision_service(service)
    
    if success:
        logger.info(f"\n✓ SUCCESS: {message}")
    else:
        logger.warning(f"\n⚠ EXPECTED FAILURE: {message}")
        logger.info("  This demonstrates latency constraint validation")
    
    time.sleep(1)


def demo_no_path_available(orchestrator: ServiceOrchestrator):
    """Demo: Service provisioning fails due to no available path"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 4: No Path Available")
    logger.info("=" * 80)
    
    service = Service(
        id="DEMO-VPN-004",
        service_type=ServiceType.MPLS_VPN,
        source_device_id="EDGE-R1",
        target_device_id="NONEXISTENT-DEVICE",
        bandwidth=1.0,
        latency_requirement=100.0
    )
    
    logger.info(f"\nProvisioning service to non-existent device: {service.id}")
    logger.info(f"  Target: {service.target_device_id} (does not exist)")
    
    success, message = orchestrator.provision_service(service)
    
    if success:
        logger.info(f"\n✓ SUCCESS: {message}")
    else:
        logger.warning(f"\n⚠ EXPECTED FAILURE: {message}")
        logger.info("  This demonstrates path validation")
    
    time.sleep(1)


def demo_multiple_services(orchestrator: ServiceOrchestrator):
    """Demo: Provision multiple services"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 5: Multiple Service Provisioning")
    logger.info("=" * 80)
    
    services = [
        Service("DEMO-VPN-005", ServiceType.MPLS_VPN, "EDGE-R1", "EDGE-R2", 0.5, 100.0),
        Service("DEMO-VPN-006", ServiceType.MPLS_VPN, "EDGE-R2", "EDGE-R3", 0.5, 100.0),
        Service("DEMO-VPN-007", ServiceType.MPLS_VPN, "EDGE-R1", "EDGE-R3", 0.5, 100.0),
    ]
    
    logger.info(f"\nProvisioning {len(services)} services...")
    
    successful = 0
    failed = 0
    
    for service in services:
        logger.info(f"\n  Provisioning: {service.id}")
        logger.info(f"    {service.source_device_id} → {service.target_device_id}")
        
        success, message = orchestrator.provision_service(service)
        
        if success:
            logger.info(f"    ✓ Success: {' → '.join(service.path)}")
            successful += 1
        else:
            logger.error(f"    ✗ Failed: {message}")
            failed += 1
        
        time.sleep(0.5)
    
    logger.info(f"\n  Summary: {successful} successful, {failed} failed")
    time.sleep(1)


def demo_path_optimization(neo4j_repo: Neo4jRepository):
    """Demo: Path optimization"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 6: Path Optimization")
    logger.info("=" * 80)
    
    source = "CORE-R1"
    target = "CORE-R3"
    
    logger.info(f"\nFinding optimal path from {source} to {target}...")
    
    # Find shortest path
    shortest_path = neo4j_repo.find_shortest_path(source, target)
    
    if shortest_path:
        logger.info(f"\n  Shortest Path: {' → '.join(shortest_path)}")
        logger.info(f"  Hops: {len(shortest_path) - 1}")
    else:
        logger.warning(f"  No path found")
    
    # Find optimal path (considering utilization)
    optimal_path = neo4j_repo.find_optimal_path(source, target)
    
    if optimal_path:
        logger.info(f"\n  Optimal Path (low utilization): {' → '.join(optimal_path['path'])}")
        logger.info(f"  Total Latency: {optimal_path.get('total_latency', 0):.2f} ms")
        logger.info(f"  Average Utilization: {optimal_path.get('avg_utilization', 0):.2%}")
    
    time.sleep(1)


def demo_service_decommissioning(orchestrator: ServiceOrchestrator):
    """Demo: Service decommissioning"""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO 7: Service Decommissioning")
    logger.info("=" * 80)
    
    service_id = "DEMO-VPN-001"
    
    logger.info(f"\nDecommissioning service: {service_id}")
    
    success, message = orchestrator.decommission_service(service_id)
    
    if success:
        logger.info(f"✓ SUCCESS: {message}")
    else:
        logger.error(f"✗ FAILED: {message}")
    
    time.sleep(1)


def print_demo_summary(metrics_repo: MetricsRepository):
    """Print demo summary"""
    logger.info("\n" + "=" * 80)
    logger.info("Demo Summary")
    logger.info("=" * 80)
    
    try:
        # Get service logs
        logs = metrics_repo.get_service_logs(limit=20)
        
        logger.info(f"\nRecent Service Events: {len(logs)}")
        for log in logs[:10]:  # Show last 10
            logger.info(f"  [{log['timestamp']}] {log['event_type']}: {log['service_id']}")
        
        logger.info("\n" + "=" * 80)
    except Exception as e:
        logger.error(f"Failed to get demo summary: {e}")


def main():
    """Main function"""
    logger.info("IntelliNet Orchestrator - Service Provisioning Demo")
    logger.info("=" * 80)
    
    # Load configuration
    config = get_config()
    
    # Initialize repositories
    logger.info("Initializing components...")
    neo4j_repo = Neo4jRepository(
        uri=config.neo4j.uri,
        user=config.neo4j.user,
        password=config.neo4j.password
    )
    logger.info(f"  ✓ Neo4j connected")
    
    metrics_repo = MetricsRepository(db_path=config.metrics.path)
    logger.info(f"  ✓ Metrics DB initialized")
    
    rule_engine = RuleEngine()
    logger.info(f"  ✓ Rule engine initialized")
    
    orchestrator = ServiceOrchestrator(
        neo4j_repo=neo4j_repo,
        metrics_repo=metrics_repo,
        rule_engine=rule_engine
    )
    logger.info(f"  ✓ Service orchestrator initialized")
    
    try:
        # Run demos
        demo_successful_provisioning(orchestrator)
        demo_bandwidth_validation_failure(orchestrator)
        demo_latency_validation_failure(orchestrator)
        demo_no_path_available(orchestrator)
        demo_multiple_services(orchestrator)
        demo_path_optimization(neo4j_repo)
        demo_service_decommissioning(orchestrator)
        
        # Print summary
        print_demo_summary(metrics_repo)
        
        logger.info("\n✓ Demo completed successfully!")
        logger.info("\nKey Takeaways:")
        logger.info("  1. Rule engine validates service requests")
        logger.info("  2. Path finding ensures connectivity")
        logger.info("  3. Metrics are recorded for all operations")
        logger.info("  4. Services can be provisioned and decommissioned")
        logger.info("  5. Path optimization considers multiple factors")
        
    except Exception as e:
        logger.error(f"\n✗ Error during demo: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        neo4j_repo.close()
        metrics_repo.close()
        logger.info("\nRepositories closed.")


if __name__ == "__main__":
    main()
