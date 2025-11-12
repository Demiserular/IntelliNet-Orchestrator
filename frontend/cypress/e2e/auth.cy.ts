/// <reference types="cypress" />

describe('Authentication Flow', () => {
  beforeEach(() => {
    cy.visit('/login');
  });

  it('should display login form', () => {
    cy.get('input[name="username"]').should('be.visible');
    cy.get('input[name="password"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should login with valid credentials', () => {
    cy.get('input[name="username"]').type('admin');
    cy.get('input[name="password"]').type('admin123');
    cy.get('button[type="submit"]').click();
    
    cy.url().should('not.include', '/login');
    cy.window().its('localStorage.auth_token').should('exist');
  });

  it('should show error with invalid credentials', () => {
    cy.get('input[name="username"]').type('invalid');
    cy.get('input[name="password"]').type('wrong');
    cy.get('button[type="submit"]').click();
    
    cy.contains('Invalid credentials').should('be.visible');
  });

  it('should logout successfully', () => {
    cy.login('admin', 'admin123');
    cy.visit('/');
    
    cy.get('[data-cy="logout-button"]').click();
    cy.url().should('include', '/login');
    cy.window().its('localStorage.auth_token').should('not.exist');
  });
});
