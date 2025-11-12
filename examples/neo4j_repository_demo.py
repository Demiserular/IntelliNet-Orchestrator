"""
Demo script for Neo4j Repository

This script demonstrates the basic usage of the Neo4jRepository class.
Note: Requires a running Neo4j instance.

To run this demo:
1. Start Neo4j (e.g., via Docker: docker run -p 7687:7687 -e NEO4J_AUTH=neo4j/password neo4j:5.12)
2. Update the connection parameters below if needed
3. Run: python examples/neo4j_repository_demo.py
"""

from src.repositories.neo4j_repository import Neo4jRepository
from src.models.specialized_devices import MPLSRouter, DWDMDevice
from src.models.link import Link, LinkType


def main():
    print("=" * 60)
    print("Neo4j Repository Demo")
    print("=" * 60)
    
    # Initialize repository
    print("\n1. Connecting to Neo4j...")
    try:
        repo = Neo4jRepository(
            uri="bolt://localhost:7687",
            user="neo4j",
            password="password"
        )
        print("✓ Connected successfully")
    except Exception as e:
        print(f"✗ Connection failed: {e}")
        print("\nMake sure Neo4j is running on localhost:7687")
        return
    
    try:
        # Create devices
        print("\n2. Creating devices...")
        router1 = MPLSRouter("R1", "CoreRouter1", capacity=100.0, location="DataCenter1")
        router2 = MPLSRouter("R2", "CoreRouter2", capacity=200.0, location="DataCenter2")
        router3 = MPLSRouter("R3", "EdgeRouter1", capacity=50.0, location="Edge1")
        dwdm1 = DWDMDevice("D1", "DWDM1", capacity=400.0, wavelengths=80, location="DataCenter1")
        
        repo.create_device(router1)
        repo.create_device(router2)
        repo.create_device(router3)
        repo.create_device(dwdm1)
        print("✓ Created 4 devices")
        
        # Create links
        print("\n3. Creating links...")
        link1 = Link("L1", "R1", "R2", bandwidth=10.0, link_type=LinkType.FIBER, latency=5.0)
        link2 = Link("L2", "R2", "R3", bandwidth=5.0, link_type=LinkType.FIBER, latency=10.0)
        link3 = Link("L3", "R1", "D1", bandwidth=40.0, link_type=LinkType.FIBER, latency=2.0)
        
        repo.create_link(link1)
        repo.create_link(link2)
        repo.create_link(link3)
        print("✓ Created 3 links")
        
        # Retrieve device
        print("\n4. Retrieving device R1...")
        device = repo.get_device("R1")
        if device:
            print(f"✓ Found device: {device['name']} (Type: {device['type']}, Capacity: {device['capacity']} Gbps)")
        
        # Get links for device
        print("\n5. Getting links for device R1...")
        links = repo.get_links_for_device("R1")
        print(f"✓ Found {len(links)} links connected to R1")
        for link in links:
            print(f"  - Link {link['id']}: {link['source']} -> {link['target']} ({link['bandwidth']} Gbps)")
        
        # Update device
        print("\n6. Updating device R3 status...")
        repo.update_device("R3", {"status": "maintenance", "utilization": 0.3})
        updated = repo.get_device("R3")
        print(f"✓ Updated R3 status to: {updated['status']}")
        
        # Export topology
        print("\n7. Exporting topology...")
        topology = repo.get_topology_json()
        print(f"✓ Topology exported: {len(topology['devices'])} devices, {len(topology['links'])} links")
        
        # Find shortest path
        print("\n8. Finding shortest path from R1 to R3...")
        path = repo.find_shortest_path("R1", "R3")
        if path:
            print(f"✓ Shortest path: {' -> '.join(path)}")
        
        # Find optimal path
        print("\n9. Finding optimal path from R1 to R3...")
        optimal = repo.find_optimal_path("R1", "R3", max_utilization=0.8, max_latency=20.0)
        if optimal:
            print(f"✓ Optimal path: {' -> '.join(optimal['path'])}")
            print(f"  Total latency: {optimal['total_latency']} ms")
            print(f"  Max utilization: {optimal['max_utilization']}")
        
        # Clean up demo data
        print("\n10. Cleaning up demo data...")
        repo.delete_device("R1")
        repo.delete_device("R2")
        repo.delete_device("R3")
        repo.delete_device("D1")
        print("✓ Deleted all demo devices and links")
        
    except Exception as e:
        print(f"\n✗ Error during demo: {e}")
    
    finally:
        # Close connection
        print("\n11. Closing connection...")
        repo.close()
        print("✓ Connection closed")
    
    print("\n" + "=" * 60)
    print("Demo completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
