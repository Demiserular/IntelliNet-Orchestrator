# IntelliNet Orchestrator - Demo Guide

## Overview

This guide walks you through a complete demonstration of the IntelliNet Orchestrator system, showcasing its key features and capabilities.

## Prerequisites

- Docker and Docker Compose installed
- System is running (see README.md for setup instructions)
- Sample data has been populated

## Quick Start Demo

### 1. Start the System

```bash
# Start all services
docker-compose up -d

# Wait for services to be ready (about 30 seconds)
docker-compose ps

# Populate sample data
docker-compose exec backend python scripts/populate_sample_data.py
```

### 2. Access the Application

- **Frontend UI**: http://localhost
- **API Documentation**: http://localhost:8000/api/docs
- **Neo4j Browser**: http://localhost:7474

**Default Credentials**:
- Username: `admin`
- Password: `admin123`

## Demo Scenarios

### Scenario 1: Explore Network Topology

**Objective**: View and interact with the network topology visualization.

**Steps**:

1. **Login** to the application at http://localhost
   - Username: `admin`
   - Password: `admin123`

2. **Navigate** to the Topology view (should be the default page)

3. **Observe** the network graph:
   - Core routers (CORE-R1, CORE-R2, CORE-R3, CORE-R4)
   - Edge routers (EDGE-R1, EDGE-R2, EDGE-R3)
   - DWDM systems (DWDM-1, DWDM-2)
   - GPON devices (OLT-1, OLT-2, ONT-1, ONT-2, ONT-3)

4. **Interact** with the graph:
   - Zoom in/out using mouse wheel
   - Pan by dragging
   - Click on nodes to see device details
   - Click on edges to see link information

5. **Check device status**:
   - Green nodes: Active devices
   - Red nodes: Failed devices
   - Yellow nodes: Maintenance mode

**Expected Result**: Interactive network topology with 14 devices and 18 links.

---

### Scenario 2: Create a New Device

**Objective**: Add a new device to the network topology.

**Steps**:

1. **Navigate** to the Device Management section

2. **Click** "Add Device" button

3. **Fill in** device details:
   - ID: `EDGE-R4`
   - Name: `Edge Router 4`
   - Type: `MPLS`
   - Capacity: `50.0` Gbps
   - Location: `SF-POP1`

4. **Submit** the form

5. **Verify** the device appears in the topology

**Expected Result**: New device created and visible in the topology graph.

---

### Scenario 3: Create a Link

**Objective**: Connect two devices with a network link.

**Steps**:

1. **Navigate** to the Link Management section

2. **Click** "Add Link" button

3. **Fill in** link details:
   - ID: `LINK-C3-E4`
   - Source Device: `CORE-R3`
   - Target Device: `EDGE-R4`
   - Bandwidth: `10.0` Gbps
   - Type: `fiber`
   - Latency: `5.0` ms

4. **Submit** the form

5. **Verify** the link appears in the topology

**Expected Result**: New link created connecting CORE-R3 to EDGE-R4.

---

### Scenario 4: Provision a Service (Success)

**Objective**: Successfully provision an MPLS VPN service.

**Steps**:

1. **Navigate** to the Service Provisioning section

2. **Click** "Provision Service" button

3. **Fill in** service details:
   - ID: `VPN-DEMO-001`
   - Service Type: `MPLS_VPN`
   - Source Device: `EDGE-R1`
   - Target Device: `EDGE-R2`
   - Bandwidth: `2.0` Gbps
   - Latency Requirement: `100.0` ms

4. **Submit** the form

5. **Observe** the provisioning process:
   - System finds path between devices
   - Rule engine validates the request
   - Service is created and activated

6. **Check** the service details:
   - Service ID and status
   - Allocated path through the network
   - Bandwidth allocation

**Expected Result**: Service successfully provisioned with path displayed.

---

### Scenario 5: Provision a Service (Validation Failure)

**Objective**: Demonstrate rule engine validation by attempting to provision a service that exceeds capacity.

**Steps**:

1. **Navigate** to the Service Provisioning section

2. **Attempt** to provision a service with excessive bandwidth:
   - ID: `VPN-DEMO-002`
   - Service Type: `MPLS_VPN`
   - Source Device: `EDGE-R1`
   - Target Device: `EDGE-R3`
   - Bandwidth: `200.0` Gbps (exceeds capacity)
   - Latency Requirement: `100.0` ms

3. **Submit** the form

4. **Observe** the validation failure:
   - Error message indicating bandwidth constraint violation
   - Rule ID (BW001) that failed
   - Details about available vs. requested capacity

**Expected Result**: Service provisioning rejected with clear error message.

---

### Scenario 6: View Analytics Dashboard

**Objective**: Monitor network status and performance metrics.

**Steps**:

1. **Navigate** to the Analytics Dashboard

2. **Observe** the dashboard widgets:
   - Total devices and active count
   - Total links and utilization
   - Active services count
   - Average network utilization

3. **View** device utilization charts:
   - Bandwidth utilization over time
   - Device status distribution
   - Link performance metrics

4. **Select** a specific device to view detailed metrics:
   - Historical utilization data
   - Status changes over time
   - Associated services

**Expected Result**: Comprehensive view of network health and performance.

---

### Scenario 7: Find Optimal Path

**Objective**: Use path optimization to find the best route between devices.

**Steps**:

1. **Navigate** to the Path Optimization section

2. **Enter** source and target devices:
   - Source: `CORE-R1`
   - Target: `CORE-R3`

3. **Click** "Find Optimal Path"

4. **Compare** results:
   - Shortest path (fewest hops)
   - Optimal path (considering utilization and latency)
   - Total latency for each path
   - Available bandwidth

5. **Visualize** the path on the topology graph

**Expected Result**: Multiple path options with performance metrics.

---

### Scenario 8: Decommission a Service

**Objective**: Remove an active service from the network.

**Steps**:

1. **Navigate** to the Services list

2. **Select** a service to decommission (e.g., `VPN-DEMO-001`)

3. **Click** "Decommission" button

4. **Confirm** the action

5. **Observe** the decommissioning process:
   - Service status changes to "decommissioned"
   - Device utilization is updated
   - Event is logged

6. **Verify** the service is no longer active

**Expected Result**: Service successfully decommissioned and resources freed.

---

## API Demo (Using curl or Postman)

### 1. Authenticate

```bash
# Get JWT token
curl -X POST http://localhost:8000/api/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"admin123"}'

# Save the access_token from the response
export TOKEN="your_access_token_here"
```

### 2. Get Topology

```bash
curl -X GET http://localhost:8000/api/topology \
  -H "Authorization: Bearer $TOKEN"
```

### 3. Create Device

```bash
curl -X POST http://localhost:8000/api/topology/device \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "API-DEVICE-001",
    "name": "API Test Device",
    "type": "MPLS",
    "capacity": 50.0,
    "location": "API-TEST"
  }'
```

### 4. Provision Service

```bash
curl -X POST http://localhost:8000/api/service/provision \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "id": "API-SERVICE-001",
    "service_type": "MPLS_VPN",
    "source_device_id": "EDGE-R1",
    "target_device_id": "EDGE-R2",
    "bandwidth": 1.0,
    "latency_requirement": 100.0
  }'
```

### 5. Get Analytics

```bash
curl -X GET http://localhost:8000/api/analytics/status \
  -H "Authorization: Bearer $TOKEN"
```

### 6. Get Device Metrics

```bash
curl -X GET "http://localhost:8000/api/analytics/device/CORE-R1/metrics?limit=10" \
  -H "Authorization: Bearer $TOKEN"
```

---

## Automated Demo Scripts

### Run Sample Data Population

```bash
# Populate the database with sample topology
docker-compose exec backend python scripts/populate_sample_data.py
```

**What it does**:
- Creates 14 network devices (routers, DWDM, GPON)
- Creates 18 links connecting the devices
- Creates 5 sample services
- Records initial metrics

### Run Service Provisioning Demo

```bash
# Run automated service provisioning scenarios
docker-compose exec backend python scripts/demo_service_provisioning.py
```

**What it demonstrates**:
1. Successful service provisioning
2. Bandwidth validation failure
3. Latency validation failure
4. No path available scenario
5. Multiple service provisioning
6. Path optimization
7. Service decommissioning

---

## Neo4j Browser Demo

### 1. Access Neo4j Browser

Open http://localhost:7474 in your browser.

**Connect**:
- Bolt URL: `bolt://localhost:7687`
- Username: `neo4j`
- Password: (from your .env file)

### 2. Explore the Graph

**View all devices**:
```cypher
MATCH (d:Device)
RETURN d
```

**View all links**:
```cypher
MATCH (s:Device)-[l:LINK]->(t:Device)
RETURN s, l, t
```

**Find path between devices**:
```cypher
MATCH path = shortestPath(
  (source:Device {id: 'CORE-R1'})-[:LINK*]-(target:Device {id: 'CORE-R3'})
)
RETURN path
```

**View services**:
```cypher
MATCH (s:Service)
RETURN s
```

**Find devices by type**:
```cypher
MATCH (d:Device {type: 'MPLS'})
RETURN d.id, d.name, d.capacity
```

---

## Demo Tips

### Best Practices

1. **Start Fresh**: Clear the database before each demo for consistency
   ```bash
   docker-compose down -v
   docker-compose up -d
   ```

2. **Use Sample Data**: Always populate sample data first
   ```bash
   docker-compose exec backend python scripts/populate_sample_data.py
   ```

3. **Check Logs**: Monitor logs for detailed information
   ```bash
   docker-compose logs -f backend
   ```

4. **Test API First**: Verify API endpoints before UI demo
   - Visit http://localhost:8000/api/docs
   - Test endpoints interactively

### Common Issues

**Issue**: Frontend can't connect to backend
- **Solution**: Check CORS settings in config.yaml
- **Verify**: `curl http://localhost:8000/health`

**Issue**: Neo4j connection failed
- **Solution**: Ensure Neo4j is running and credentials are correct
- **Check**: `docker-compose logs neo4j`

**Issue**: Sample data script fails
- **Solution**: Ensure databases are initialized
- **Run**: `docker-compose exec backend python scripts/init_db.py`

---

## Demo Presentation Flow

### 5-Minute Quick Demo

1. Show topology visualization (1 min)
2. Create a device and link (1 min)
3. Provision a service successfully (1 min)
4. Show analytics dashboard (1 min)
5. Demonstrate API docs (1 min)

### 15-Minute Comprehensive Demo

1. System architecture overview (2 min)
2. Topology management (3 min)
3. Service provisioning (success and failure) (4 min)
4. Analytics and monitoring (3 min)
5. Path optimization (2 min)
6. API demonstration (1 min)

### 30-Minute Deep Dive

1. Architecture and design decisions (5 min)
2. Complete topology walkthrough (5 min)
3. Service provisioning scenarios (7 min)
4. Rule engine and validation (5 min)
5. Analytics and metrics (4 min)
6. API and integration (4 min)

---

## Next Steps After Demo

1. **Explore the Code**:
   - Review domain models in `src/models/`
   - Check service orchestration in `src/services/`
   - Examine API endpoints in `src/api/routes/`

2. **Extend the System**:
   - Add new device types
   - Create custom validation rules
   - Implement additional analytics

3. **Run Tests**:
   ```bash
   docker-compose exec backend pytest tests/ -v
   ```

4. **Read Documentation**:
   - [API Documentation](API_DOCUMENTATION.md)
   - [Developer Guide](DEVELOPER_GUIDE.md)
   - [Architecture](ARCHITECTURE.md)

---

## Support

For questions or issues during the demo:
- Check the logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/api/docs
- Consult the troubleshooting section in README.md
