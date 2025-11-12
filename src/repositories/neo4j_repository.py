"""
Neo4j Repository for topology management

This module provides the Neo4jRepository class for managing network topology
data in Neo4j graph database, including devices, links, and services.
"""

import time
import logging
from typing import Optional, List, Dict, Any
from neo4j import GraphDatabase, Driver, Session
from neo4j.exceptions import ServiceUnavailable, SessionExpired

from src.models.device import Device, DeviceType, DeviceStatus
from src.models.link import Link, LinkType
from src.models.service import Service

logger = logging.getLogger(__name__)


class Neo4jRepository:
    """Repository for topology data in Neo4j"""
    
    def __init__(self, uri: str, user: str, password: str, 
                 max_retry_attempts: int = 3, retry_delay: float = 1.0):
        """
        Initialize Neo4j repository with connection management
        
        Args:
            uri: Neo4j connection URI (e.g., bolt://localhost:7687)
            user: Neo4j username
            password: Neo4j password
            max_retry_attempts: Maximum number of connection retry attempts
            retry_delay: Initial delay between retries in seconds (exponential backoff)
        """
        self.uri = uri
        self.user = user
        self.password = password
        self.max_retry_attempts = max_retry_attempts
        self.retry_delay = retry_delay
        self.driver: Optional[Driver] = None
        
        self._connect_with_retry()
        self._initialize_indexes()
    
    def _connect_with_retry(self) -> None:
        """
        Establish connection to Neo4j with exponential backoff retry logic
        
        Raises:
            ServiceUnavailable: If connection fails after all retry attempts
        """
        attempt = 0
        last_exception = None
        
        while attempt < self.max_retry_attempts:
            try:
                logger.info(f"Attempting to connect to Neo4j at {self.uri} (attempt {attempt + 1}/{self.max_retry_attempts})")
                self.driver = GraphDatabase.driver(self.uri, auth=(self.user, self.password))
                
                # Verify connectivity
                with self.driver.session() as session:
                    session.run("RETURN 1")
                
                logger.info("Successfully connected to Neo4j")
                return
                
            except ServiceUnavailable as e:
                last_exception = e
                attempt += 1
                
                if attempt < self.max_retry_attempts:
                    delay = self.retry_delay * (2 ** (attempt - 1))  # Exponential backoff
                    logger.warning(f"Connection failed, retrying in {delay} seconds...")
                    time.sleep(delay)
                else:
                    logger.error(f"Failed to connect to Neo4j after {self.max_retry_attempts} attempts")
        
        raise ServiceUnavailable(f"Could not connect to Neo4j: {last_exception}")
    
    def _initialize_indexes(self) -> None:
        """
        Create indexes for query optimization
        
        Creates indexes on:
        - Device.id
        - Device.type
        - Service.id
        """
        if not self.driver:
            return
        
        try:
            with self.driver.session() as session:
                # Create index on Device.id
                session.run("""
                    CREATE INDEX device_id_index IF NOT EXISTS
                    FOR (d:Device) ON (d.id)
                """)
                
                # Create index on Device.type
                session.run("""
                    CREATE INDEX device_type_index IF NOT EXISTS
                    FOR (d:Device) ON (d.type)
                """)
                
                # Create index on Service.id
                session.run("""
                    CREATE INDEX service_id_index IF NOT EXISTS
                    FOR (s:Service) ON (s.id)
                """)
                
                logger.info("Neo4j indexes created successfully")
                
        except Exception as e:
            logger.error(f"Error creating indexes: {e}")
            # Don't raise - indexes are optimization, not critical
    
    def close(self) -> None:
        """
        Close the Neo4j driver connection
        
        Should be called when the repository is no longer needed
        to properly release resources.
        """
        if self.driver:
            logger.info("Closing Neo4j connection")
            self.driver.close()
            self.driver = None

    # Device CRUD Operations
    
    def create_device(self, device: Device) -> bool:
        """
        Create a device node in Neo4j
        
        Args:
            device: Device object to create
            
        Returns:
            bool: True if device was created successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                CREATE (d:Device {
                    id: $id,
                    name: $name,
                    type: $type,
                    capacity: $capacity,
                    location: $location,
                    status: $status,
                    utilization: $utilization
                })
                RETURN d
                """
                
                device_dict = device.to_dict()
                result = session.run(query, **device_dict)
                
                created = result.single() is not None
                if created:
                    logger.info(f"Created device: {device.id}")
                return created
                
        except Exception as e:
            logger.error(f"Error creating device {device.id}: {e}")
            return False
    
    def get_device(self, device_id: str) -> Optional[Dict[str, Any]]:
        """
        Retrieve a device by ID
        
        Args:
            device_id: Unique identifier of the device
            
        Returns:
            Optional[Dict[str, Any]]: Device properties as dictionary, or None if not found
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return None
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (d:Device {id: $device_id})
                RETURN d
                """
                
                result = session.run(query, device_id=device_id)
                record = result.single()
                
                if record:
                    device_node = record["d"]
                    return dict(device_node)
                
                return None
                
        except Exception as e:
            logger.error(f"Error retrieving device {device_id}: {e}")
            return None
    
    def update_device(self, device_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update device properties
        
        Args:
            device_id: Unique identifier of the device
            properties: Dictionary of properties to update
            
        Returns:
            bool: True if device was updated successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                # Build SET clause dynamically
                set_clauses = [f"d.{key} = ${key}" for key in properties.keys()]
                set_clause = ", ".join(set_clauses)
                
                query = f"""
                MATCH (d:Device {{id: $device_id}})
                SET {set_clause}
                RETURN d
                """
                
                params = {"device_id": device_id, **properties}
                result = session.run(query, **params)
                
                updated = result.single() is not None
                if updated:
                    logger.info(f"Updated device: {device_id}")
                return updated
                
        except Exception as e:
            logger.error(f"Error updating device {device_id}: {e}")
            return False
    
    def delete_device(self, device_id: str) -> bool:
        """
        Delete a device and all its relationships
        
        Args:
            device_id: Unique identifier of the device
            
        Returns:
            bool: True if device was deleted successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (d:Device {id: $device_id})
                DETACH DELETE d
                RETURN count(d) as deleted_count
                """
                
                result = session.run(query, device_id=device_id)
                record = result.single()
                
                deleted = record and record["deleted_count"] > 0
                if deleted:
                    logger.info(f"Deleted device: {device_id}")
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting device {device_id}: {e}")
            return False

    # Link CRUD Operations
    
    def create_link(self, link: Link) -> bool:
        """
        Create a link relationship between two devices in Neo4j
        
        Args:
            link: Link object to create
            
        Returns:
            bool: True if link was created successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (source:Device {id: $source_id})
                MATCH (target:Device {id: $target_id})
                CREATE (source)-[l:LINK {
                    id: $id,
                    bandwidth: $bandwidth,
                    type: $type,
                    latency: $latency,
                    utilization: $utilization,
                    status: $status
                }]->(target)
                RETURN l
                """
                
                link_dict = link.to_dict()
                params = {
                    "source_id": link.source_device_id,
                    "target_id": link.target_device_id,
                    "id": link_dict["id"],
                    "bandwidth": link_dict["bandwidth"],
                    "type": link_dict["type"],
                    "latency": link_dict["latency"],
                    "utilization": link_dict["utilization"],
                    "status": link_dict["status"]
                }
                
                result = session.run(query, **params)
                created = result.single() is not None
                
                if created:
                    logger.info(f"Created link: {link.id} from {link.source_device_id} to {link.target_device_id}")
                return created
                
        except Exception as e:
            logger.error(f"Error creating link {link.id}: {e}")
            return False
    
    def get_links_for_device(self, device_id: str) -> List[Dict[str, Any]]:
        """
        Query all links connected to a device
        
        Args:
            device_id: Unique identifier of the device
            
        Returns:
            List[Dict[str, Any]]: List of link properties with source and target device IDs
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return []
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (d:Device {id: $device_id})
                MATCH (d)-[l:LINK]-(other:Device)
                RETURN l, startNode(l).id as source, endNode(l).id as target
                """
                
                result = session.run(query, device_id=device_id)
                
                links = []
                for record in result:
                    link_props = dict(record["l"])
                    link_props["source"] = record["source"]
                    link_props["target"] = record["target"]
                    links.append(link_props)
                
                return links
                
        except Exception as e:
            logger.error(f"Error retrieving links for device {device_id}: {e}")
            return []
    
    def update_link(self, link_id: str, properties: Dict[str, Any]) -> bool:
        """
        Update link properties
        
        Args:
            link_id: Unique identifier of the link
            properties: Dictionary of properties to update
            
        Returns:
            bool: True if link was updated successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                # Build SET clause dynamically
                set_clauses = [f"l.{key} = ${key}" for key in properties.keys()]
                set_clause = ", ".join(set_clauses)
                
                query = f"""
                MATCH ()-[l:LINK {{id: $link_id}}]-()
                SET {set_clause}
                RETURN l
                """
                
                params = {"link_id": link_id, **properties}
                result = session.run(query, **params)
                
                updated = result.single() is not None
                if updated:
                    logger.info(f"Updated link: {link_id}")
                return updated
                
        except Exception as e:
            logger.error(f"Error updating link {link_id}: {e}")
            return False
    
    def delete_link(self, link_id: str) -> bool:
        """
        Delete a link relationship
        
        Args:
            link_id: Unique identifier of the link
            
        Returns:
            bool: True if link was deleted successfully, False otherwise
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return False
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH ()-[l:LINK {id: $link_id}]-()
                DELETE l
                RETURN count(l) as deleted_count
                """
                
                result = session.run(query, link_id=link_id)
                record = result.single()
                
                deleted = record and record["deleted_count"] > 0
                if deleted:
                    logger.info(f"Deleted link: {link_id}")
                return deleted
                
        except Exception as e:
            logger.error(f"Error deleting link {link_id}: {e}")
            return False

    # Topology Export and Path Finding
    
    def get_topology_json(self) -> Dict[str, Any]:
        """
        Export complete network topology as JSON
        
        Returns:
            Dict[str, Any]: Dictionary containing 'devices' and 'links' lists
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return {"devices": [], "links": []}
        
        try:
            with self.driver.session() as session:
                # Get all devices
                devices_query = "MATCH (d:Device) RETURN d"
                devices_result = session.run(devices_query)
                devices = [dict(record["d"]) for record in devices_result]
                
                # Get all links
                links_query = """
                MATCH (source:Device)-[l:LINK]->(target:Device)
                RETURN source.id as source, target.id as target, properties(l) as link
                """
                links_result = session.run(links_query)
                
                links = []
                for record in links_result:
                    link_data = dict(record["link"])
                    link_data["source"] = record["source"]
                    link_data["target"] = record["target"]
                    links.append(link_data)
                
                logger.info(f"Exported topology: {len(devices)} devices, {len(links)} links")
                return {"devices": devices, "links": links}
                
        except Exception as e:
            logger.error(f"Error exporting topology: {e}")
            return {"devices": [], "links": []}
    
    def find_shortest_path(self, source_id: str, target_id: str) -> Optional[List[str]]:
        """
        Find shortest path between two devices using Neo4j shortestPath algorithm
        
        Args:
            source_id: Source device ID
            target_id: Target device ID
            
        Returns:
            Optional[List[str]]: List of device IDs in the path, or None if no path exists
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return None
        
        try:
            with self.driver.session() as session:
                query = """
                MATCH (source:Device {id: $source_id}),
                      (target:Device {id: $target_id}),
                      path = shortestPath((source)-[:LINK*]-(target))
                RETURN [node in nodes(path) | node.id] as device_path
                """
                
                result = session.run(query, source_id=source_id, target_id=target_id)
                record = result.single()
                
                if record:
                    path = record["device_path"]
                    logger.info(f"Found shortest path from {source_id} to {target_id}: {path}")
                    return path
                
                logger.warning(f"No path found from {source_id} to {target_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error finding shortest path: {e}")
            return None
    
    def find_optimal_path(self, source_id: str, target_id: str, 
                         max_utilization: float = 0.8,
                         max_latency: Optional[float] = None) -> Optional[Dict[str, Any]]:
        """
        Find optimal path considering utilization and latency constraints
        
        Args:
            source_id: Source device ID
            target_id: Target device ID
            max_utilization: Maximum acceptable link utilization (0.0 to 1.0)
            max_latency: Maximum acceptable total latency in ms (optional)
            
        Returns:
            Optional[Dict[str, Any]]: Dictionary with 'path' (list of device IDs),
                                     'total_latency' (float), and 'max_utilization' (float),
                                     or None if no valid path exists
        """
        if not self.driver:
            logger.error("Neo4j driver not initialized")
            return None
        
        try:
            with self.driver.session() as session:
                # Find all paths and filter by constraints
                query = """
                MATCH (source:Device {id: $source_id}),
                      (target:Device {id: $target_id}),
                      path = (source)-[:LINK*]-(target)
                WHERE ALL(rel in relationships(path) WHERE rel.utilization <= $max_utilization)
                WITH path, 
                     [node in nodes(path) | node.id] as device_path,
                     reduce(total = 0, rel in relationships(path) | total + rel.latency) as total_latency,
                     reduce(max_util = 0, rel in relationships(path) | 
                            CASE WHEN rel.utilization > max_util THEN rel.utilization ELSE max_util END) as max_link_utilization
                """
                
                # Add latency constraint if specified
                if max_latency is not None:
                    query += " WHERE total_latency <= $max_latency"
                
                query += """
                RETURN device_path, total_latency, max_link_utilization
                ORDER BY length(path), total_latency, max_link_utilization
                LIMIT 1
                """
                
                params = {
                    "source_id": source_id,
                    "target_id": target_id,
                    "max_utilization": max_utilization
                }
                
                if max_latency is not None:
                    params["max_latency"] = max_latency
                
                result = session.run(query, **params)
                record = result.single()
                
                if record:
                    optimal_path = {
                        "path": record["device_path"],
                        "total_latency": record["total_latency"],
                        "max_utilization": record["max_link_utilization"]
                    }
                    logger.info(f"Found optimal path from {source_id} to {target_id}: {optimal_path}")
                    return optimal_path
                
                logger.warning(f"No optimal path found from {source_id} to {target_id} with given constraints")
                return None
                
        except Exception as e:
            logger.error(f"Error finding optimal path: {e}")
            return None

    def get_all_services(self) -> List[Dict[str, Any]]:
        """
        Get all services from the database
        
        Returns:
            List of service dictionaries with their properties
        """
        try:
            with self.driver.session() as session:
                query = """
                MATCH (s:Service)
                RETURN s.id as id,
                       s.service_type as service_type,
                       s.source_device_id as source_device_id,
                       s.target_device_id as target_device_id,
                       s.bandwidth as bandwidth,
                       s.latency_requirement as latency_requirement,
                       s.status as status,
                       s.path as path,
                       s.created_at as created_at,
                       s.activated_at as activated_at
                ORDER BY s.created_at DESC
                """
                
                result = session.run(query)
                services = []
                
                for record in result:
                    service = {
                        "id": record["id"],
                        "service_type": record["service_type"],
                        "source_device_id": record["source_device_id"],
                        "target_device_id": record["target_device_id"],
                        "bandwidth": record["bandwidth"],
                        "latency_requirement": record["latency_requirement"],
                        "status": record["status"],
                        "path": record["path"] if record["path"] else [],
                        "created_at": record["created_at"],
                        "activated_at": record["activated_at"]
                    }
                    services.append(service)
                
                logger.info(f"Retrieved {len(services)} services from database")
                return services
                
        except Exception as e:
            logger.error(f"Error getting all services: {e}")
            return []
