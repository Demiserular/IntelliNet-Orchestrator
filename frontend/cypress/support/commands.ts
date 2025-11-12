// Custom Cypress commands for IntelliNet Orchestrator

/**
 * Login command
 * Usage: cy.login('admin', 'password')
 */
Cypress.Commands.add('login', (username: string, password: string) => {
  cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/auth/login`,
    body: {
      username,
      password
    }
  }).then((response) => {
    expect(response.status).to.eq(200);
    expect(response.body).to.have.property('access_token');
    
    // Store token in localStorage
    window.localStorage.setItem('auth_token', response.body.access_token);
    window.localStorage.setItem('user', JSON.stringify(response.body.user));
  });
});

/**
 * Logout command
 * Usage: cy.logout()
 */
Cypress.Commands.add('logout', () => {
  window.localStorage.removeItem('auth_token');
  window.localStorage.removeItem('user');
  cy.visit('/login');
});

/**
 * Create a test device
 */
Cypress.Commands.add('createDevice', (deviceData: any) => {
  const token = window.localStorage.getItem('auth_token');
  
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/topology/device`,
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: deviceData
  });
});

/**
 * Create a test link
 */
Cypress.Commands.add('createLink', (linkData: any) => {
  const token = window.localStorage.getItem('auth_token');
  
  return cy.request({
    method: 'POST',
    url: `${Cypress.env('apiUrl')}/topology/link`,
    headers: {
      Authorization: `Bearer ${token}`
    },
    body: linkData
  });
});

/**
 * Clean up test data
 */
Cypress.Commands.add('cleanupTestData', () => {
  // This would call cleanup endpoints if they exist
  cy.log('Cleaning up test data');
});

// Extend Cypress namespace for TypeScript
declare global {
  namespace Cypress {
    interface Chainable {
      createDevice(deviceData: any): Chainable<Response<any>>;
      createLink(linkData: any): Chainable<Response<any>>;
      cleanupTestData(): Chainable<void>;
    }
  }
}

export {};
