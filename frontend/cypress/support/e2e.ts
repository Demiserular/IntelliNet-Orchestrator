// Cypress E2E support file
// This file is processed and loaded automatically before test files

// Import commands
import './commands';

// Prevent TypeScript errors
declare global {
  namespace Cypress {
    interface Chainable {
      login(username: string, password: string): Chainable<void>;
      logout(): Chainable<void>;
    }
  }
}

// Global before hook
before(() => {
  // Setup code that runs once before all tests
  cy.log('Starting E2E test suite');
});

// Global after hook
after(() => {
  // Cleanup code that runs once after all tests
  cy.log('E2E test suite completed');
});

// Handle uncaught exceptions
Cypress.on('uncaught:exception', (err, runnable) => {
  // Returning false prevents Cypress from failing the test
  // You can customize this based on specific errors you want to ignore
  console.error('Uncaught exception:', err);
  return false;
});
