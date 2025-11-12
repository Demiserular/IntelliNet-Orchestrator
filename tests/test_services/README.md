# Service Layer Tests

This directory contains unit and integration tests for the service layer components.

## Test Files

### test_rule_engine.py
Tests for the rule-based validation engine that validates service provisioning requests.

**Test Coverage:**
- RuleCondition dataclass creation
- RuleEngine initialization with default rules
- Rule addition and priority sorting
- Rule evaluation with passing conditions
- Bandwidth capacity violation detection
- Latency requirement violation detection
- Multiple rule violation aggregation
- Disabled rule exclusion
- Exception handling in rule conditions
- Optional parameter handling (None device/link)

**Default Rules Tested:**
- BW001: Bandwidth Capacity Check - Ensures service bandwidth doesn't exceed device capacity
- LAT001: Latency Requirement Check - Ensures link latency meets service requirements

### test_service_orchestrator.py
Integration tests for the ServiceOrchestrator that coordinates service provisioning workflows.

**Test Coverage:**
- ServiceOrchestrator initialization with dependency injection
- End-to-end service provisioning workflow
- Path finding integration with Neo4j repository
- Rule validation integration
- Service creation in Neo4j with relationships
- Device and link metrics recording
- Service decommissioning workflow
- Error handling for invalid paths
- Error handling for validation failures
- Error handling for Neo4j creation failures

**Test Classes:**
- TestServiceOrchestratorInitialization: Tests dependency injection setup
- TestServiceProvisioning: Tests service provisioning success and failure scenarios
- TestMetricsRecording: Tests metrics recording during provisioning
- TestServiceDecommissioning: Tests service decommissioning workflow
- TestRuleValidationIntegration: Tests integration with rule engine

## Running Tests

Run all service tests:
```bash
pytest tests/test_services/ -v
```

Run with coverage:
```bash
pytest tests/test_services/ --cov=src/services --cov-report=term-missing
```
