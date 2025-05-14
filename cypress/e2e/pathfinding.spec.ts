/// <reference types="cypress" />

describe('Media Navigation Pathfinding', () => {
  beforeEach(() => {
    cy.login('test@example.com', 'password123');
    cy.visit('/media');
  });

  it('should navigate through media grid using keyboard shortcuts', () => {
    // Start from first item
    cy.get('.media-card').first().click();
    cy.get('.media-preview-modal').should('be.visible');

    // Navigate right
    cy.get('body').type('{rightarrow}');
    cy.get('.media-preview-modal').should('contain', 'Item 2');

    // Navigate left
    cy.get('body').type('{leftarrow}');
    cy.get('.media-preview-modal').should('contain', 'Item 1');

    // Close preview
    cy.get('body').type('Escape');
    cy.get('.media-preview-modal').should('not.exist');
  });

  it('should maintain navigation history', () => {
    // Navigate through several items
    cy.get('.media-card').eq(0).click();
    cy.get('.media-preview-modal').should('be.visible');
    cy.get('body').type('{rightarrow}');
    cy.get('body').type('{rightarrow}');

    // Go back in history
    cy.get('[data-testid="nav-back"]').click();
    cy.get('.media-preview-modal').should('contain', 'Item 2');

    // Go forward in history
    cy.get('[data-testid="nav-forward"]').click();
    cy.get('.media-preview-modal').should('contain', 'Item 3');
  });

  it('should handle grid navigation with filters applied', () => {
    // Apply a filter
    cy.get('select[name="mimeType"]').select('image');

    // Navigate through filtered results
    cy.get('.media-card').first().click();
    cy.get('.media-preview-modal').should('be.visible');

    // Verify navigation only includes filtered items
    cy.get('body').type('{rightarrow}');
    cy.get('.media-preview-modal').should('contain', 'image');
  });

  it('should maintain position after closing and reopening preview', () => {
    // Navigate to third item
    cy.get('.media-card').eq(2).click();
    cy.get('.media-preview-modal').should('contain', 'Item 3');

    // Close preview
    cy.get('body').type('Escape');
    cy.get('.media-preview-modal').should('not.exist');

    // Reopen preview from grid
    cy.get('.media-card').eq(2).click();
    cy.get('.media-preview-modal').should('contain', 'Item 3');
  });

  it('should handle edge cases in navigation', () => {
    // Navigate to first item
    cy.get('.media-card').first().click();
    
    // Try to navigate left (should stay on first item)
    cy.get('body').type('{leftarrow}');
    cy.get('.media-preview-modal').should('contain', 'Item 1');

    // Navigate to last item
    cy.get('.media-card').last().click();
    
    // Try to navigate right (should stay on last item)
    cy.get('body').type('{rightarrow}');
    cy.get('.media-preview-modal').should('contain', 'Last Item');
  });

  it('should support touch swipe navigation', () => {
    // Open preview
    cy.get('.media-card').first().click();
    cy.get('.media-preview-modal').should('be.visible');

    // Swipe left to next item
    cy.get('.media-preview-modal')
      .trigger('touchstart', { touches: [{ clientX: 500, clientY: 300 }] })
      .trigger('touchmove', { touches: [{ clientX: 100, clientY: 300 }] })
      .trigger('touchend');

    cy.get('.media-preview-modal').should('contain', 'Item 2');

    // Swipe right to previous item
    cy.get('.media-preview-modal')
      .trigger('touchstart', { touches: [{ clientX: 100, clientY: 300 }] })
      .trigger('touchmove', { touches: [{ clientX: 500, clientY: 300 }] })
      .trigger('touchend');

    cy.get('.media-preview-modal').should('contain', 'Item 1');
  });
}); 