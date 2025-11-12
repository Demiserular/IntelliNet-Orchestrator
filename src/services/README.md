# Services Layer

This directory contains the business logic and orchestration services for the IntelliNet Orchestrator.

## Components

### RuleEngine (`rule_engine.py`)
A rule-based validation engine for service provisioning requests.

**Key Classes:**
- `RuleCondition`: Dataclass representing a validation rule with condition, action, and priority
- `RuleEngine`: Engine that evaluates services against configured rules

**Features:**
- Dynamic rule registration with priority-based ordering
- Default rules for bandwidth capacity and latency requirements
- Support for custom rules via callable conditions
- Rule enable/disable functionality
- Comprehensive error handling and logging

**Default Rules:**
- BW001: Bandwidth Capacity Check - Validates service bandwidth against device capacity
- LAT001: Latency Requirement Check - Validates link latency against service requirements

**Usage Example:**
```python
from src.services.rule_engine import RuleEngine, RuleCondition
from src.models.service import Service

# Initialize rule engine with default rules
engine = RuleEngine()

# Add custom rule
engine.add_rule(RuleCondition(
    rule_id="CUSTOM001",
    name="Custom Validation",
    condition=lambda service, device, link: service.bandwidth > 1000,
    action="reject",
    priority=3
))

# Evaluate service
is_valid, violations = engine.evaluate(service, device, link)
```

### ServiceOrchestrator (`service_orchestrator.py`)
Orchestrates end-to-end service provisioning and decommissioning workflows.

**Key Classes:**
- `ServiceOrchestrator`: Main orchestration class coordinating repositories and rule engine

**Features:**
- Dependency injection pattern for loose coupling
- End-to-end service provisioning workflow
- Path finding using Neo4j shortest path algorithm
- Rule-based validation integration
- Service node and relationship creation in Neo4j
- Device and link utilization metrics recording
- Service decommissioning with cleanup
- Comprehensive error handling and logging

**Provisioning Workflow:**
1. Find path between source and target devices
2. Validate service against all enabled rules
3. Create service nodes and relationships in Neo4j
4. Update device and link utilization metrics
5. Log provisioning event

**Decommissioning Workflow:**
1. Retrieve service from Neo4j
2. Remove service node and relationships
3. Update device utilization metrics
4. Log decommissioning event

**Usage Example:**
```python
from src.services.service_orchestrator import ServiceOrchestrator
from src.repositories.neo4j_repository import Neo4jRepository
from src.repositories.metrics_repository import MetricsRepository
from src.services.rule_engine import RuleEngine
from src.models.service import Service, ServiceType

# Initialize dependencies
neo4j_repo = Neo4jRepository("bolt://localhost:7687", "neo4j", "password")
metrics_repo = MetricsRepository("metrics.db")
rule_engine = RuleEngine()

# Create orchestrator
orchestrator = ServiceOrchestrator(neo4j_repo, metrics_repo, rule_engine)

# Provision service
service = Service(
    id="S001",
    service_type=ServiceType.MPLS_VPN,
    source_device_id="R1",
    target_device_id="R3",
    bandwidth=50.0,
    latency_requirement=10.0
)

success, message = orchestrator.provision_service(service)
if success:
    print(f"Service provisioned: {message}")
else:
    print(f"Provisioning failed: {message}")

# Decommission service
success, message = orchestrator.decommission_service("S001")
```

## Architecture

The services layer follows these design principles:

1. **Dependency Injection**: All dependencies are injected via constructor for testability
2. **Single Responsibility**: Each service has a clear, focused purpose
3. **Separation of Concerns**: Business logic is separated from data access
4. **Error Handling**: Comprehensive error handling with descriptive messages
5. **Logging**: Detailed logging for debugging and monitoring

## Dependencies

- `src.repositories.neo4j_repository`: Neo4j topology management
- `src.repositories.metrics_repository`: SQLite metrics storage
- `src.models`: Domain models (Device, Link, Service)

## Testing

See `tests/test_services/` for comprehensive unit and integration tests.

Run tests:
```bash
pytest tests/test_services/ -v
```
