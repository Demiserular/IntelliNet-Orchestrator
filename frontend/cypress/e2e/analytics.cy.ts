/// <reference types="cypress" />

describe('Analytics Dashboard', () => {
  beforeEach(() => {
    cy.login('admin', 'admin123');
    cy.visit('/analytics');
  });

  it('should display analytics dashboard', () => {
    cy.get('[data-cy="analytics-dashboard"]').should('be.visible');
  });

  it('should display network status summary', () => {
    cy.get('[data-cy="status-summary"]').should('be.visible');
    cy.get('[data-cy="total-devices"]').should('exist');
    cy.get('[data-cy="total-services"]').should('exist');
  });

  it('should display bandwidth utilization chart', () => {
    cy.get('[data-cy="bandwidth-chart"]').should('be.visible');
  });

  it('should refresh data on button click', () => {
    cy.get('[data-cy="refresh-button"]').click();
    cy.contains('Data refreshed').should('be.visible');
  });

  it('should filter metrics by time range', () => {
    cy.get('[data-cy="time-range-select"]').select('24h');
    cy.get('[data-cy="bandwidth-chart"]').should('be.visible');
  });
});
