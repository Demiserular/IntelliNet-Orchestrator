# Domain Model Unit Tests

This directory contains comprehensive unit tests for the IntelliNet Orchestrator domain models.

## Test Coverage

### Test Files
- `test_device.py` - Tests for Device base class and specialized device implementations
- `test_link.py` - Tests for Link model
- `test_service.py` - Tests for Service model

### Coverage Summary
- **Total Tests**: 86
- **Code Coverage**: 98%
- **All Tests**: PASSING ✓

## Test Categories

### Device Tests (test_device.py)
1. **Device Inheritance and Polymorphism** (6 tests)
   - Abstract base class behavior
   - Inheritance verification for all device types
   - Polymorphic method behavior

2. **DWDM Device Tests** (8 tests)
   - Initialization and configuration
   - Wavelength allocation and provisioning
   - Capacity calculations (full, partial, empty)

3. **MPLS Router Tests** (8 tests)
   - Initialization and configuration
   - Service provisioning with capacity checks
   - VPN instance management
   - Capacity calculations

4. **GPON Device Tests** (9 tests)
   - OLT and ONT initialization
   - Split ratio management
   - Provisioning behavior for OLT/ONT
   - Capacity calculations

5. **Device Serialization Tests** (5 tests)
   - to_dict() method for all device types
   - JSON serialization correctness

### Link Tests (test_link.py)
1. **Link Creation Tests** (5 tests)
   - Initialization with all parameters
   - Default values
   - Different link types (FIBER, ETHERNET, WIRELESS)

2. **Bandwidth Calculation Tests** (6 tests)
   - Available bandwidth with various utilization levels
   - Edge cases (0%, 100% utilization)

3. **Link Serialization Tests** (6 tests)
   - to_dict() method correctness
   - Different link types and statuses

4. **LinkType Enum Tests** (2 tests)
   - Enum values and members

### Service Tests (test_service.py)
1. **Service Creation Tests** (8 tests)
   - Initialization with all parameters
   - Different service types
   - Default values

2. **Service Status Management Tests** (3 tests)
   - Status transitions (PENDING, ACTIVE, FAILED, DECOMMISSIONED)

3. **Service Path Management Tests** (3 tests)
   - Path setting and modification
   - Empty path handling

4. **Service Serialization Tests** (7 tests)
   - to_dict() method for all service types
   - Different statuses and configurations

5. **Service Enum Tests** (4 tests)
   - ServiceType and ServiceStatus enum values

6. **Service Requirements Tests** (6 tests)
   - Bandwidth requirements
   - Latency requirements

## Running Tests

### Run all model tests:
```bash
pytest tests/test_models/ -v
```

### Run with coverage:
```bash
pytest tests/test_models/ --cov=src/models --cov-report=term-missing
```

### Run specific test file:
```bash
pytest tests/test_models/test_device.py -v
```

### Run specific test class:
```bash
pytest tests/test_models/test_device.py::TestDWDMDevice -v
```

## Requirements Coverage

These tests satisfy the following requirements from the specification:

- **Requirement 2.1**: Device type support and OOP hierarchy
- **Requirement 2.2**: DWDM device wavelength management
- **Requirement 2.3**: GPON device OLT/ONT support
- **Requirement 2.4**: MPLS router label-switched paths
- **Requirement 2.5**: Device capacity calculations and serialization

## Test Design Principles

1. **Comprehensive Coverage**: Tests cover normal cases, edge cases, and error conditions
2. **Clear Naming**: Test names clearly describe what is being tested
3. **Isolation**: Each test is independent and can run in any order
4. **Assertions**: Multiple assertions verify different aspects of behavior
5. **Documentation**: Docstrings explain the purpose of each test
