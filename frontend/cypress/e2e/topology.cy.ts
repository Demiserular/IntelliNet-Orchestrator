/// <reference types="cypress" />

describe('Topology Management', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    cy.visit('/topology');
  });

  afterEach(() => {
    cy.cleanupTestData();
  });

  it('should display topology visualizer', () => {
    cy.get('[data-cy="topology-canvas"]').should('be.visible');
  });

  it('should create a new device', () => {
    cy.get('[data-cy="add-device-button"]').click();
    
    cy.get('input[name="deviceId"]').type('TEST-DEVICE-001');
    cy.get('input[name="deviceName"]').type('Test Router');
    cy.get('select[name="deviceType"]').select('MPLS');
    cy.get('input[name="capacity"]').type('100');
    
    cy.get('button[type="submit"]').click();
    
    cy.contains('Device created successfully').should('be.visible');
  });

  it('should display device list', () => {
    cy.get('[data-cy="device-list"]').should('be.visible');
    cy.get('[data-cy="device-item"]').should('have.length.at.least', 0);
  });

  it('should search for devices', () => {
    cy.get('[data-cy="device-search"]').type('router');
    cy.get('[data-cy="device-item"]').each(($el) => {
      cy.wrap($el).should('contain.text', 'router');
    });
  });
});
