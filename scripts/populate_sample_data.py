"""
Sample Data Population Script for IntelliNet Orchestrator

This script populates the system with sample network topology data
including devices, links, and services for demonstration purposes.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.config import get_config
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.models import (
    DeviceType, DeviceStatus, LinkType, ServiceType, ServiceStatus
)
from src.models.specialized_devices import DWDMDevice, MPLSRouter, GPONDevice
from src.models.link import Link
from src.models.service import Service
from src.logging_config import setup_logging, get_logger

# Setup logging
setup_logging(log_level="INFO")
logger = get_logger(__name__)


def create_sample_topology(neo4j_repo: Neo4jRepository, metrics_repo: MetricsRepository):
    """Create a sample network topology"""
    logger.info("=" * 80)
    logger.info("Creating Sample Network Topology")
    logger.info("=" * 80)
    
    # Create devices
    devices = [
        # Core MPLS Routers
        MPLSRouter("CORE-R1", "Core Router 1", 100.0, "NYC-DC1"),
        MPLSRouter("CORE-R2", "Core Router 2", 100.0, "NYC-DC2"),
        MPLSRouter("CORE-R3", "Core Router 3", 100.0, "LA-DC1"),
        MPLSRouter("CORE-R4", "Core Router 4", 100.0, "CHI-DC1"),
        
        # Edge MPLS Routers
        MPLSRouter("EDGE-R1", "Edge Router 1", 50.0, "NYC-POP1"),
        MPLSRouter("EDGE-R2", "Edge Router 2", 50.0, "LA-POP1"),
        MPLSRouter("EDGE-R3", "Edge Router 3", 50.0, "CHI-POP1"),
        
        # DWDM Devices
        DWDMDevice("DWDM-1", "DWDM System 1", 400.0, wavelengths=80, location="NYC-DC1"),
        DWDMDevice("DWDM-2", "DWDM System 2", 400.0, wavelengths=80, location="LA-DC1"),
        
        # GPON Devices
        GPONDevice("OLT-1", "OLT NYC 1", 10.0, is_olt=True, location="NYC-CO1"),
        GPONDevice("OLT-2", "OLT LA 1", 10.0, is_olt=True, location="LA-CO1"),
        GPONDevice("ONT-1", "ONT Customer 1", 1.0, is_olt=False, location="NYC-CUST1"),
        GPONDevice("ONT-2", "ONT Customer 2", 1.0, is_olt=False, location="NYC-CUST2"),
        GPONDevice("ONT-3", "ONT Customer 3", 1.0, is_olt=False, location="LA-CUST1"),
    ]
    
    logger.info(f"Creating {len(devices)} devices...")
    for device in devices:
        try:
            neo4j_repo.create_device(device)
            metrics_repo.record_device_metric(
                device_id=device.id,
                utilization=device.utilization,
                status=device.status.value
            )
            logger.info(f"  ✓ Created device: {device.id} ({device.name})")
        except Exception as e:
            logger.error(f"  ✗ Failed to create device {device.id}: {e}")
    
    # Create links
    links = [
        # Core network mesh
        Link("LINK-C1-C2", "CORE-R1", "CORE-R2", 10.0, LinkType.FIBER, latency=2.0),
        Link("LINK-C1-C3", "CORE-R1", "CORE-R3", 10.0, LinkType.FIBER, latency=50.0),
        Link("LINK-C1-C4", "CORE-R1", "CORE-R4", 10.0, LinkType.FIBER, latency=30.0),
        Link("LINK-C2-C3", "CORE-R2", "CORE-R3", 10.0, LinkType.FIBER, latency=45.0),
        Link("LINK-C2-C4", "CORE-R2", "CORE-R4", 10.0, LinkType.FIBER, latency=25.0),
        Link("LINK-C3-C4", "CORE-R3", "CORE-R4", 10.0, LinkType.FIBER, latency=35.0),
        
        # Core to Edge
        Link("LINK-C1-E1", "CORE-R1", "EDGE-R1", 10.0, LinkType.FIBER, latency=5.0),
        Link("LINK-C2-E1", "CORE-R2", "EDGE-R1", 10.0, LinkType.FIBER, latency=5.0),
        Link("LINK-C3-E2", "CORE-R3", "EDGE-R2", 10.0, LinkType.FIBER, latency=5.0),
        Link("LINK-C4-E3", "CORE-R4", "EDGE-R3", 10.0, LinkType.FIBER, latency=5.0),
        
        # DWDM connections
        Link("LINK-D1-C1", "DWDM-1", "CORE-R1", 100.0, LinkType.FIBER, latency=1.0),
        Link("LINK-D2-C3", "DWDM-2", "CORE-R3", 100.0, LinkType.FIBER, latency=1.0),
        Link("LINK-D1-D2", "DWDM-1", "DWDM-2", 400.0, LinkType.FIBER, latency=40.0),
        
        # GPON access network
        Link("LINK-E1-OLT1", "EDGE-R1", "OLT-1", 10.0, LinkType.FIBER, latency=2.0),
        Link("LINK-E2-OLT2", "EDGE-R2", "OLT-2", 10.0, LinkType.FIBER, latency=2.0),
        Link("LINK-OLT1-ONT1", "OLT-1", "ONT-1", 1.0, LinkType.FIBER, latency=1.0),
        Link("LINK-OLT1-ONT2", "OLT-1", "ONT-2", 1.0, LinkType.FIBER, latency=1.0),
        Link("LINK-OLT2-ONT3", "OLT-2", "ONT-3", 1.0, LinkType.FIBER, latency=1.0),
    ]
    
    logger.info(f"\nCreating {len(links)} links...")
    for link in links:
        try:
            neo4j_repo.create_link(link)
            metrics_repo.record_link_metric(
                link_id=link.id,
                utilization=link.utilization,
                latency=link.latency
            )
            logger.info(f"  ✓ Created link: {link.id} ({link.source_device_id} → {link.target_device_id})")
        except Exception as e:
            logger.error(f"  ✗ Failed to create link {link.id}: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Sample topology created successfully!")
    logger.info("=" * 80)


def create_sample_services(neo4j_repo: Neo4jRepository, metrics_repo: MetricsRepository):
    """Create sample services"""
    logger.info("\n" + "=" * 80)
    logger.info("Creating Sample Services")
    logger.info("=" * 80)
    
    services = [
        Service(
            id="VPN-001",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="EDGE-R1",
            target_device_id="EDGE-R2",
            bandwidth=2.0,
            latency_requirement=100.0
        ),
        Service(
            id="VPN-002",
            service_type=ServiceType.MPLS_VPN,
            source_device_id="EDGE-R1",
            target_device_id="EDGE-R3",
            bandwidth=3.0,
            latency_requirement=80.0
        ),
        Service(
            id="CIRCUIT-001",
            service_type=ServiceType.OTN_CIRCUIT,
            source_device_id="DWDM-1",
            target_device_id="DWDM-2",
            bandwidth=10.0,
            latency_requirement=50.0
        ),
        Service(
            id="GPON-001",
            service_type=ServiceType.GPON_ACCESS,
            source_device_id="OLT-1",
            target_device_id="ONT-1",
            bandwidth=0.1,
            latency_requirement=10.0
        ),
        Service(
            id="GPON-002",
            service_type=ServiceType.GPON_ACCESS,
            source_device_id="OLT-1",
            target_device_id="ONT-2",
            bandwidth=0.1,
            latency_requirement=10.0
        ),
    ]
    
    logger.info(f"Creating {len(services)} services...")
    for service in services:
        try:
            # Find path
            path = neo4j_repo.find_shortest_path(
                service.source_device_id,
                service.target_device_id
            )
            
            if path:
                service.path = path
                service.status = ServiceStatus.ACTIVE
                
                # Create service in Neo4j
                neo4j_repo.create_service(service)
                
                # Log service creation
                metrics_repo.record_service_log(
                    service_id=service.id,
                    event_type="PROVISIONED",
                    details=f"Service provisioned on path: {' → '.join(path)}"
                )
                
                logger.info(f"  ✓ Created service: {service.id} ({service.service_type.value})")
                logger.info(f"    Path: {' → '.join(path)}")
            else:
                logger.warning(f"  ⚠ No path found for service: {service.id}")
        except Exception as e:
            logger.error(f"  ✗ Failed to create service {service.id}: {e}")
    
    logger.info("\n" + "=" * 80)
    logger.info("Sample services created successfully!")
    logger.info("=" * 80)


def print_topology_summary(neo4j_repo: Neo4jRepository):
    """Print topology summary"""
    logger.info("\n" + "=" * 80)
    logger.info("Topology Summary")
    logger.info("=" * 80)
    
    try:
        topology = neo4j_repo.get_topology_json()
        
        devices = topology.get("devices", [])
        links = topology.get("links", [])
        
        logger.info(f"\nTotal Devices: {len(devices)}")
        
        # Count by type
        device_types = {}
        for device in devices:
            dtype = device.get("type", "Unknown")
            device_types[dtype] = device_types.get(dtype, 0) + 1
        
        for dtype, count in sorted(device_types.items()):
            logger.info(f"  - {dtype}: {count}")
        
        logger.info(f"\nTotal Links: {len(links)}")
        
        # Count by type
        link_types = {}
        for link in links:
            ltype = link.get("type", "Unknown")
            link_types[ltype] = link_types.get(ltype, 0) + 1
        
        for ltype, count in sorted(link_types.items()):
            logger.info(f"  - {ltype}: {count}")
        
        logger.info("\n" + "=" * 80)
    except Exception as e:
        logger.error(f"Failed to get topology summary: {e}")


def main():
    """Main function"""
    logger.info("IntelliNet Orchestrator - Sample Data Population")
    logger.info("=" * 80)
    
    # Load configuration
    config = get_config()
    
    # Initialize repositories
    logger.info("Initializing repositories...")
    neo4j_repo = Neo4jRepository(
        uri=config.neo4j.uri,
        user=config.neo4j.user,
        password=config.neo4j.password
    )
    logger.info(f"  ✓ Neo4j connected: {config.neo4j.uri}")
    
    metrics_repo = MetricsRepository(db_path=config.metrics.path)
    logger.info(f"  ✓ Metrics DB initialized: {config.metrics.path}")
    
    try:
        # Create sample data
        create_sample_topology(neo4j_repo, metrics_repo)
        create_sample_services(neo4j_repo, metrics_repo)
        
        # Print summary
        print_topology_summary(neo4j_repo)
        
        logger.info("\n✓ Sample data population completed successfully!")
        logger.info("\nYou can now:")
        logger.info("  1. View the topology at: http://localhost:4200")
        logger.info("  2. Explore the API at: http://localhost:8000/api/docs")
        logger.info("  3. Login with: admin / admin123")
        
    except Exception as e:
        logger.error(f"\n✗ Error during data population: {e}", exc_info=True)
        sys.exit(1)
    finally:
        # Cleanup
        neo4j_repo.close()
        metrics_repo.close()
        logger.info("\nRepositories closed.")


if __name__ == "__main__":
    main()
