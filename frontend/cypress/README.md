# Cypress E2E Tests

This directory contains end-to-end tests for the IntelliNet Orchestrator frontend.

## Structure

```
cypress/
├── e2e/                    # Test specifications
│   ├── auth.cy.ts         # Authentication tests
│   ├── topology.cy.ts     # Topology management tests
│   ├── service-provisioning.cy.ts  # Service provisioning tests
│   └── analytics.cy.ts    # Analytics dashboard tests
├── fixtures/              # Test data
│   └── test-data.json    # Sample test data
├── support/              # Support files
│   ├── commands.ts       # Custom commands
│   └── e2e.ts           # Global configuration
└── README.md            # This file
```

## Running Tests

### Interactive Mode (Development)

```bash
npm run e2e
```

This opens the Cypress Test Runner where you can select and run tests interactively.

### Headless Mode (CI)

```bash
npm run e2e:headless
```

This runs all tests in headless mode, suitable for CI/CD pipelines.

### With Server Start

```bash
npm run e2e:ci
```

This starts the Angular dev server and runs tests, then stops the server.

## Prerequisites

Before running E2E tests, ensure:

1. Backend API is running on `http://localhost:8000`
2. Neo4j database is running and accessible
3. Test user accounts exist (admin/admin123, user/user123)

## Custom Commands

The tests use custom Cypress commands defined in `support/commands.ts`:

- `cy.login(username, password)` - Login with credentials
- `cy.logout()` - Logout current user
- `cy.createDevice(deviceData)` - Create a test device
- `cy.createLink(linkData)` - Create a test link
- `cy.cleanupTestData()` - Clean up test data

## Test Data

Test fixtures are located in `fixtures/test-data.json` and include:
- Test user credentials
- Sample device configurations
- Sample link configurations
- Sample service requests

## Writing New Tests

When writing new E2E tests:

1. Use data-cy attributes for element selection
2. Clean up test data in afterEach hooks
3. Use fixtures for consistent test data
4. Handle async operations properly
5. Add meaningful assertions

Example:

```typescript
describe('My Feature', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    cy.visit('/my-feature');
  });

  afterEach(() => {
    cy.cleanupTestData();
  });

  it('should do something', () => {
    cy.get('[data-cy="my-element"]').click();
    cy.contains('Expected text').should('be.visible');
  });
});
```

## CI/CD Integration

E2E tests run automatically in GitHub Actions after backend and frontend tests pass.
See `.github/workflows/ci.yml` for the complete CI configuration.
