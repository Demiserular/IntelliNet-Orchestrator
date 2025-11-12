# Repository Layer

This directory contains the repository layer for data persistence in the IntelliNet Orchestrator.

## Neo4j Repository

The `neo4j_repository.py` module provides the `Neo4jRepository` class for managing network topology data in Neo4j graph database.

### Features

#### Connection Management
- Automatic connection with exponential backoff retry logic
- Configurable retry attempts and delays
- Proper connection cleanup with `close()` method
- Automatic index creation for query optimization

#### Device Operations
- `create_device(device)` - Create a device node
- `get_device(device_id)` - Retrieve device by ID
- `update_device(device_id, properties)` - Update device properties
- `delete_device(device_id)` - Delete device and all relationships

#### Link Operations
- `create_link(link)` - Create a link relationship between devices
- `get_links_for_device(device_id)` - Get all links for a device
- `update_link(link_id, properties)` - Update link properties
- `delete_link(link_id)` - Delete a link relationship

#### Topology Export
- `get_topology_json()` - Export complete topology as JSON with devices and links

#### Path Finding
- `find_shortest_path(source_id, target_id)` - Find shortest path using Neo4j algorithms
- `find_optimal_path(source_id, target_id, max_utilization, max_latency)` - Find optimal path considering utilization and latency constraints

### Usage Example

```python
from src.repositories.neo4j_repository import Neo4jRepository
from src.models.device import Device, DeviceType
from src.models.link import Link, LinkType
from src.models.specialized_devices import MPLSRouter

# Initialize repository
repo = Neo4jRepository(
    uri="bolt://localhost:7687",
    user="neo4j",
    password="password"
)

# Create devices
router1 = MPLSRouter("R1", "CoreRouter1", capacity=100.0)
router2 = MPLSRouter("R2", "CoreRouter2", capacity=100.0)
repo.create_device(router1)
repo.create_device(router2)

# Create link
link = Link("L1", "R1", "R2", bandwidth=10.0, link_type=LinkType.FIBER)
repo.create_link(link)

# Find path
path = repo.find_shortest_path("R1", "R2")
print(f"Path: {path}")

# Export topology
topology = repo.get_topology_json()
print(f"Devices: {len(topology['devices'])}, Links: {len(topology['links'])}")

# Clean up
repo.close()
```

### Configuration

The repository requires Neo4j connection parameters:
- `uri`: Neo4j connection URI (e.g., `bolt://localhost:7687`)
- `user`: Neo4j username
- `password`: Neo4j password
- `max_retry_attempts`: Maximum connection retry attempts (default: 3)
- `retry_delay`: Initial retry delay in seconds (default: 1.0)

### Indexes

The repository automatically creates the following indexes for query optimization:
- `device_id_index` on `Device.id`
- `device_type_index` on `Device.type`
- `service_id_index` on `Service.id`

### Error Handling

All methods include comprehensive error handling and logging:
- Connection failures trigger retry logic with exponential backoff
- Database operation errors are logged and return appropriate failure indicators
- Methods return `None`, `False`, or empty collections on failure

### Testing

Integration tests are available in `tests/test_repositories/test_neo4j_repository.py`.

See the test README for more information on running the tests.
