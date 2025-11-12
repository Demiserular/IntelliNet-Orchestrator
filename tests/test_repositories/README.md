# Repository Integration Tests

This directory contains integration tests for the repository layer.

## Neo4j Repository Tests

The `test_neo4j_repository.py` file contains integration tests for the Neo4j repository.

### Requirements

- Docker must be running (for testcontainers)
- Python packages: `pytest`, `testcontainers`, `neo4j`

### Running the Tests

To run all Neo4j repository tests:

```bash
pytest tests/test_repositories/test_neo4j_repository.py -v
```

To run a specific test class:

```bash
pytest tests/test_repositories/test_neo4j_repository.py::TestDeviceCRUD -v
```

### Test Coverage

The tests cover:

1. **Connection Management**: Connection establishment, retry logic, and cleanup
2. **Device CRUD**: Create, read, update, and delete operations for devices
3. **Link CRUD**: Create, read, update, and delete operations for links
4. **Topology Export**: Exporting complete network topology as JSON
5. **Path Finding**: Shortest path and optimal path algorithms with constraints

### Notes

- Tests use testcontainers to spin up a real Neo4j instance
- Each test function gets a clean database (all data is deleted after each test)
- The Neo4j container is started once per test module and reused across tests
- Tests may take longer to run due to container startup time
