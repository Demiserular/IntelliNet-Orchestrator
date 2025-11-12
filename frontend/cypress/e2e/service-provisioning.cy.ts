/// <reference types="cypress" />

describe('Service Provisioning', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    
    // Create test devices
    cy.createDevice({
      id: 'TEST-R1',
      name: 'Test Router 1',
      type: 'MPLS',
      capacity: 100
    });
    
    cy.createDevice({
      id: 'TEST-R2',
      name: 'Test Router 2',
      type: 'MPLS',
      capacity: 100
    });
    
    // Create test link
    cy.createLink({
      id: 'TEST-LINK-1',
      source_device_id: 'TEST-R1',
      target_device_id: 'TEST-R2',
      bandwidth: 10,
      type: 'fiber',
      latency: 5
    });
    
    cy.visit('/services/provision');
  });

  afterEach(() => {
    cy.cleanupTestData();
  });

  it('should display service provision form', () => {
    cy.get('select[name="serviceType"]').should('be.visible');
    cy.get('input[name="bandwidth"]').should('be.visible');
    cy.get('button[type="submit"]').should('be.visible');
  });

  it('should provision a service successfully', () => {
    cy.get('select[name="serviceType"]').select('MPLS_VPN');
    cy.get('input[name="source"]').type('TEST-R1');
    cy.get('input[name="destination"]').type('TEST-R2');
    cy.get('input[name="bandwidth"]').type('5');
    
    cy.get('button[type="submit"]').click();
    
    cy.contains('Service provisioned successfully').should('be.visible');
  });
});
