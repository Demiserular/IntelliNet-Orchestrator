"""
Integration tests for Neo4j Repository

These tests use testcontainers to spin up a real Neo4j instance
for integration testing of the repository layer.
"""

import pytest
from testcontainers.neo4j import Neo4jContainer

from src.repositories.neo4j_repository import Neo4jRepository
from src.models.device import Device, DeviceType, DeviceStatus
from src.models.link import Link, LinkType
from src.models.specialized_devices import MPLSRouter, DWDMDevice, GPONDevice


@pytest.fixture(scope="module")
def neo4j_container():
    """
    Fixture to start a Neo4j container for testing
    """
    container = Neo4jContainer("neo4j:5.12")
    container.start()
    yield container
    container.stop()


@pytest.fixture(scope="function")
def neo4j_repo(neo4j_container):
    """
    Fixture to create a Neo4j repository connected to the test container
    """
    uri = neo4j_container.get_connection_url()
    repo = Neo4jRepository(uri, "neo4j", neo4j_container.NEO4J_ADMIN_PASSWORD)
    yield repo
    
    # Clean up: delete all nodes and relationships after each test
    with repo.driver.session() as session:
        session.run("MATCH (n) DETACH DELETE n")
    
    repo.close()


class TestNeo4jRepositoryConnection:
    """Test connection management and initialization"""
    
    def test_connection_successful(self, neo4j_repo):
        """Test that connection to Neo4j is established"""
        assert neo4j_repo.driver is not None
    
    def test_indexes_created(self, neo4j_repo):
        """Test that indexes are created on initialization"""
        with neo4j_repo.driver.session() as session:
            result = session.run("SHOW INDEXES")
            indexes = [record["name"] for record in result]
            
            assert "device_id_index" in indexes
            assert "device_type_index" in indexes
            assert "service_id_index" in indexes
    
    def test_close_connection(self, neo4j_container):
        """Test that connection can be closed properly"""
        uri = neo4j_container.get_connection_url()
        repo = Neo4jRepository(uri, "neo4j", neo4j_container.NEO4J_ADMIN_PASSWORD)
        
        repo.close()
        assert repo.driver is None


class TestDeviceCRUD:
    """Test device CRUD operations"""
    
    def test_create_device(self, neo4j_repo):
        """Test creating a device in Neo4j"""
        device = MPLSRouter("R1", "CoreRouter1", capacity=100.0, location="DataCenter1")
        
        result = neo4j_repo.create_device(device)
        
        assert result is True
    
    def test_get_device(self, neo4j_repo):
        """Test retrieving a device by ID"""
        device = MPLSRouter("R2", "CoreRouter2", capacity=200.0, location="DataCenter2")
        neo4j_repo.create_device(device)
        
        retrieved = neo4j_repo.get_device("R2")
        
        assert retrieved is not None
        assert retrieved["id"] == "R2"
        assert retrieved["name"] == "CoreRouter2"
        assert retrieved["type"] == DeviceType.MPLS.value
        assert retrieved["capacity"] == 200.0
        assert retrieved["location"] == "DataCenter2"
    
    def test_get_nonexistent_device(self, neo4j_repo):
        """Test retrieving a device that doesn't exist"""
        retrieved = neo4j_repo.get_device("NONEXISTENT")
        
        assert retrieved is None
    
    def test_update_device(self, neo4j_repo):
        """Test updating device properties"""
        device = DWDMDevice("D1", "DWDM1", capacity=400.0, wavelengths=80)
        neo4j_repo.create_device(device)
        
        result = neo4j_repo.update_device("D1", {
            "status": DeviceStatus.MAINTENANCE.value,
            "utilization": 0.5
        })
        
        assert result is True
        
        updated = neo4j_repo.get_device("D1")
        assert updated["status"] == DeviceStatus.MAINTENANCE.value
        assert updated["utilization"] == 0.5
    
    def test_delete_device(self, neo4j_repo):
        """Test deleting a device"""
        device = GPONDevice("G1", "GPON_OLT1", capacity=10.0, is_olt=True)
        neo4j_repo.create_device(device)
        
        result = neo4j_repo.delete_device("G1")
        
        assert result is True
        
        retrieved = neo4j_repo.get_device("G1")
        assert retrieved is None
    
    def test_delete_device_with_relationships(self, neo4j_repo):
        """Test deleting a device that has link relationships"""
        device1 = MPLSRouter("R3", "Router3", capacity=100.0)
        device2 = MPLSRouter("R4", "Router4", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        
        link = Link("L1", "R3", "R4", bandwidth=10.0, link_type=LinkType.FIBER)
        neo4j_repo.create_link(link)
        
        result = neo4j_repo.delete_device("R3")
        
        assert result is True
        assert neo4j_repo.get_device("R3") is None


class TestLinkCRUD:
    """Test link CRUD operations"""
    
    def test_create_link(self, neo4j_repo):
        """Test creating a link between devices"""
        device1 = MPLSRouter("R5", "Router5", capacity=100.0)
        device2 = MPLSRouter("R6", "Router6", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        
        link = Link("L2", "R5", "R6", bandwidth=10.0, link_type=LinkType.FIBER, latency=5.0)
        result = neo4j_repo.create_link(link)
        
        assert result is True
    
    def test_get_links_for_device(self, neo4j_repo):
        """Test retrieving all links for a device"""
        device1 = MPLSRouter("R7", "Router7", capacity=100.0)
        device2 = MPLSRouter("R8", "Router8", capacity=100.0)
        device3 = MPLSRouter("R9", "Router9", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        neo4j_repo.create_device(device3)
        
        link1 = Link("L3", "R7", "R8", bandwidth=10.0, link_type=LinkType.FIBER)
        link2 = Link("L4", "R7", "R9", bandwidth=20.0, link_type=LinkType.ETHERNET)
        neo4j_repo.create_link(link1)
        neo4j_repo.create_link(link2)
        
        links = neo4j_repo.get_links_for_device("R7")
        
        assert len(links) == 2
        link_ids = [link["id"] for link in links]
        assert "L3" in link_ids
        assert "L4" in link_ids
    
    def test_update_link(self, neo4j_repo):
        """Test updating link properties"""
        device1 = MPLSRouter("R10", "Router10", capacity=100.0)
        device2 = MPLSRouter("R11", "Router11", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        
        link = Link("L5", "R10", "R11", bandwidth=10.0, link_type=LinkType.FIBER)
        neo4j_repo.create_link(link)
        
        result = neo4j_repo.update_link("L5", {
            "utilization": 0.7,
            "latency": 15.0
        })
        
        assert result is True
        
        links = neo4j_repo.get_links_for_device("R10")
        updated_link = next(l for l in links if l["id"] == "L5")
        assert updated_link["utilization"] == 0.7
        assert updated_link["latency"] == 15.0
    
    def test_delete_link(self, neo4j_repo):
        """Test deleting a link"""
        device1 = MPLSRouter("R12", "Router12", capacity=100.0)
        device2 = MPLSRouter("R13", "Router13", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        
        link = Link("L6", "R12", "R13", bandwidth=10.0, link_type=LinkType.FIBER)
        neo4j_repo.create_link(link)
        
        result = neo4j_repo.delete_link("L6")
        
        assert result is True
        
        links = neo4j_repo.get_links_for_device("R12")
        assert len(links) == 0


class TestTopologyExport:
    """Test topology export functionality"""
    
    def test_get_topology_json_empty(self, neo4j_repo):
        """Test exporting empty topology"""
        topology = neo4j_repo.get_topology_json()
        
        assert "devices" in topology
        assert "links" in topology
        assert len(topology["devices"]) == 0
        assert len(topology["links"]) == 0
    
    def test_get_topology_json_with_data(self, neo4j_repo):
        """Test exporting topology with devices and links"""
        device1 = MPLSRouter("R14", "Router14", capacity=100.0)
        device2 = MPLSRouter("R15", "Router15", capacity=100.0)
        device3 = DWDMDevice("D2", "DWDM2", capacity=400.0, wavelengths=80)
        
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        neo4j_repo.create_device(device3)
        
        link1 = Link("L7", "R14", "R15", bandwidth=10.0, link_type=LinkType.FIBER)
        link2 = Link("L8", "R15", "D2", bandwidth=40.0, link_type=LinkType.FIBER)
        neo4j_repo.create_link(link1)
        neo4j_repo.create_link(link2)
        
        topology = neo4j_repo.get_topology_json()
        
        assert len(topology["devices"]) == 3
        assert len(topology["links"]) == 2
        
        device_ids = [d["id"] for d in topology["devices"]]
        assert "R14" in device_ids
        assert "R15" in device_ids
        assert "D2" in device_ids
        
        link_ids = [l["id"] for l in topology["links"]]
        assert "L7" in link_ids
        assert "L8" in link_ids


class TestPathFinding:
    """Test path finding algorithms"""
    
    def setup_network(self, neo4j_repo):
        """Helper method to set up a test network topology"""
        # Create devices
        devices = [
            MPLSRouter("R16", "Router16", capacity=100.0),
            MPLSRouter("R17", "Router17", capacity=100.0),
            MPLSRouter("R18", "Router18", capacity=100.0),
            MPLSRouter("R19", "Router19", capacity=100.0),
            MPLSRouter("R20", "Router20", capacity=100.0)
        ]
        
        for device in devices:
            neo4j_repo.create_device(device)
        
        # Create links forming a network
        # R16 -> R17 -> R18 -> R20
        #  |            |
        #  +-> R19 -----+
        links = [
            Link("L9", "R16", "R17", bandwidth=10.0, link_type=LinkType.FIBER, latency=5.0),
            Link("L10", "R17", "R18", bandwidth=10.0, link_type=LinkType.FIBER, latency=10.0),
            Link("L11", "R18", "R20", bandwidth=10.0, link_type=LinkType.FIBER, latency=5.0),
            Link("L12", "R16", "R19", bandwidth=10.0, link_type=LinkType.FIBER, latency=8.0),
            Link("L13", "R19", "R18", bandwidth=10.0, link_type=LinkType.FIBER, latency=7.0)
        ]
        
        for link in links:
            neo4j_repo.create_link(link)
    
    def test_find_shortest_path(self, neo4j_repo):
        """Test finding shortest path between devices"""
        self.setup_network(neo4j_repo)
        
        path = neo4j_repo.find_shortest_path("R16", "R20")
        
        assert path is not None
        assert path[0] == "R16"
        assert path[-1] == "R20"
        assert len(path) >= 2
    
    def test_find_shortest_path_no_path(self, neo4j_repo):
        """Test finding path when no path exists"""
        device1 = MPLSRouter("R21", "Router21", capacity=100.0)
        device2 = MPLSRouter("R22", "Router22", capacity=100.0)
        neo4j_repo.create_device(device1)
        neo4j_repo.create_device(device2)
        
        path = neo4j_repo.find_shortest_path("R21", "R22")
        
        assert path is None
    
    def test_find_optimal_path(self, neo4j_repo):
        """Test finding optimal path with constraints"""
        self.setup_network(neo4j_repo)
        
        # Update some links with high utilization
        neo4j_repo.update_link("L10", {"utilization": 0.9})
        
        result = neo4j_repo.find_optimal_path("R16", "R20", max_utilization=0.8)
        
        assert result is not None
        assert "path" in result
        assert "total_latency" in result
        assert "max_utilization" in result
        assert result["path"][0] == "R16"
        assert result["path"][-1] == "R20"
        assert result["max_utilization"] <= 0.8
    
    def test_find_optimal_path_with_latency_constraint(self, neo4j_repo):
        """Test finding optimal path with latency constraint"""
        self.setup_network(neo4j_repo)
        
        result = neo4j_repo.find_optimal_path("R16", "R20", max_latency=25.0)
        
        assert result is not None
        assert result["total_latency"] <= 25.0
    
    def test_find_optimal_path_no_valid_path(self, neo4j_repo):
        """Test finding optimal path when no path meets constraints"""
        self.setup_network(neo4j_repo)
        
        # Set all links to high utilization
        for link_id in ["L9", "L10", "L11", "L12", "L13"]:
            neo4j_repo.update_link(link_id, {"utilization": 0.95})
        
        result = neo4j_repo.find_optimal_path("R16", "R20", max_utilization=0.5)
        
        assert result is None
