/// <reference types="cypress" />

describe('Search and Filter Functionality', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/media');
  });

  describe('Search Functionality', () => {
    it('should perform basic text search', () => {
      const searchTerm = 'test image';
      cy.get('.search-form input').type(searchTerm);
      cy.get('.search-form').submit();

      // Verify search results
      cy.get('.media-card').should('exist');
      cy.get('.media-card .filename').should('contain', searchTerm);
      cy.get('.highlight').should('contain', searchTerm);
    });

    it('should handle search with no results', () => {
      cy.get('.search-form input').type('nonexistent123456');
      cy.get('.search-form').submit();

      cy.get('.no-results').should('be.visible');
      cy.get('.no-results').should('contain', 'No results found');
    });

    it('should update results as user types with debounce', () => {
      cy.get('.search-form input').type('test');
      cy.get('.loading-indicator').should('be.visible');
      cy.get('.media-card').should('exist');

      // Type more and verify debounce
      cy.get('.search-form input').type(' image');
      cy.get('.loading-indicator').should('be.visible');
      cy.get('.media-card').should('exist');
    });
  });

  describe('Filter Functionality', () => {
    it('should filter by file type', () => {
      cy.get('select[name="mimeType"]').select('image');
      cy.get('.media-card').each(($card) => {
        cy.wrap($card).should('contain', 'image');
      });

      cy.get('select[name="mimeType"]').select('video');
      cy.get('.media-card').each(($card) => {
        cy.wrap($card).should('contain', 'video');
      });
    });

    it('should filter by date range', () => {
      const today = new Date().toISOString().split('T')[0];
      cy.get('input[name="dateFrom"]').type(today);
      cy.get('input[name="dateTo"]').type(today);

      cy.get('.media-card').should('have.length.gte', 0);
      cy.get('.date-filter-active').should('be.visible');
    });

    it('should filter by file size', () => {
      cy.get('input[name="minSize"]').type('100');
      cy.get('input[name="maxSize"]').type('1000');

      cy.get('.media-card').should('have.length.gte', 0);
      cy.get('.size-filter-active').should('be.visible');
    });

    it('should combine multiple filters', () => {
      // Apply multiple filters
      cy.get('select[name="mimeType"]').select('image');
      cy.get('input[name="minSize"]').type('100');
      cy.get('.search-form input').type('test');
      cy.get('.search-form').submit();

      // Verify filtered results
      cy.get('.media-card').should('have.length.gte', 0);
      cy.get('.active-filters').should('contain', 'image');
      cy.get('.active-filters').should('contain', 'size');
      cy.get('.active-filters').should('contain', 'test');
    });
  });

  describe('Filter Management', () => {
    it('should clear individual filters', () => {
      // Apply filters
      cy.get('select[name="mimeType"]').select('image');
      cy.get('input[name="minSize"]').type('100');

      // Clear file type filter
      cy.get('[data-testid="clear-filter-mimeType"]').click();
      cy.get('select[name="mimeType"]').should('have.value', '');
      cy.get('.active-filters').should('not.contain', 'image');

      // Size filter should still be active
      cy.get('.active-filters').should('contain', 'size');
    });

    it('should clear all filters', () => {
      // Apply multiple filters
      cy.get('select[name="mimeType"]').select('image');
      cy.get('input[name="minSize"]').type('100');
      cy.get('.search-form input').type('test');
      cy.get('.search-form').submit();

      // Clear all filters
      cy.get('[data-testid="clear-all-filters"]').click();

      // Verify all filters are cleared
      cy.get('select[name="mimeType"]').should('have.value', '');
      cy.get('input[name="minSize"]').should('have.value', '');
      cy.get('.search-form input').should('have.value', '');
      cy.get('.active-filters').should('not.exist');
    });

    it('should save and load filter presets', () => {
      // Set up filters
      cy.get('select[name="mimeType"]').select('image');
      cy.get('input[name="minSize"]').type('100');

      // Save preset
      cy.get('[data-testid="save-preset"]').click();
      cy.get('input[name="preset-name"]').type('My Images');
      cy.get('[data-testid="confirm-save-preset"]').click();

      // Clear filters
      cy.get('[data-testid="clear-all-filters"]').click();

      // Load preset
      cy.get('[data-testid="load-preset"]').click();
      cy.get('[data-testid="preset-My Images"]').click();

      // Verify filters are restored
      cy.get('select[name="mimeType"]').should('have.value', 'image');
      cy.get('input[name="minSize"]').should('have.value', '100');
    });
  });
}); 