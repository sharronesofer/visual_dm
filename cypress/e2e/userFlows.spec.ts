import { faker } from '@faker-js/faker';

describe('User Flows', () => {
  beforeEach(() => {
    // Reset application state and visit the home page
    cy.visit('/');
  });

  describe('Authentication Flow', () => {
    it('should allow user to login and logout', () => {
      // Test login
      cy.get('[data-testid="login-button"]').click();
      cy.get('#email').type('test@example.com');
      cy.get('#password').type('password123');
      cy.get('form').submit();
      
      // Verify successful login
      cy.get('[data-testid="user-menu"]').should('be.visible');
      
      // Test logout
      cy.get('[data-testid="user-menu"]').click();
      cy.get('[data-testid="logout-button"]').click();
      
      // Verify successful logout
      cy.get('[data-testid="login-button"]').should('be.visible');
    });

    it('should show validation errors for invalid login', () => {
      cy.get('[data-testid="login-button"]').click();
      cy.get('#email').type('invalid@email');
      cy.get('#password').type('short');
      cy.get('form').submit();
      
      cy.get('.error-message').should('be.visible');
    });
  });

  describe('Media Browsing Flow', () => {
    beforeEach(() => {
      // Login before each test
      cy.login('test@example.com', 'password123');
    });

    it('should display media grid and allow switching to list view', () => {
      // Check initial grid view
      cy.get('.media-grid').should('be.visible');
      cy.get('.media-card').should('have.length.gt', 0);
      
      // Switch to list view
      cy.get('[data-testid="view-toggle"]').click();
      cy.get('.media-list').should('be.visible');
    });

    it('should allow opening and closing media preview', () => {
      // Click first media item
      cy.get('.media-card').first().click();
      
      // Verify preview modal
      cy.get('.media-preview-modal').should('be.visible');
      
      // Close preview
      cy.get('[data-testid="close-preview"]').click();
      cy.get('.media-preview-modal').should('not.exist');
    });
  });

  describe('Upload Flow', () => {
    beforeEach(() => {
      cy.login('test@example.com', 'password123');
    });

    it('should allow file upload via drag and drop', () => {
      // Create a test file
      const fileName = 'test-image.png';
      
      // Trigger file drop
      cy.get('.dropzone').attachFile(fileName, { subjectType: 'drag-n-drop' });
      
      // Verify upload progress
      cy.get('.progress-bar').should('be.visible');
      cy.get('.progress-bar').should('have.attr', 'style').and('include', 'width: 100%');
      
      // Verify successful upload
      cy.get('.media-card').should('contain', fileName);
    });

    it('should handle upload errors gracefully', () => {
      // Try uploading an invalid file
      cy.get('.dropzone').attachFile('invalid.xyz', { subjectType: 'drag-n-drop' });
      
      // Verify error message
      cy.get('.error-message').should('be.visible');
    });
  });

  describe('Search and Filter Flow', () => {
    beforeEach(() => {
      cy.login('test@example.com', 'password123');
    });

    it('should filter media by type and date range', () => {
      // Select image type filter
      cy.get('select[name="mimeType"]').select('image');
      
      // Set date range
      const today = new Date().toISOString().split('T')[0];
      cy.get('input[name="dateFrom"]').type(today);
      cy.get('input[name="dateTo"]').type(today);
      
      // Verify filtered results
      cy.get('.media-card').should('have.length.gte', 0);
    });

    it('should perform text search with highlighting', () => {
      // Type search query
      const searchQuery = 'test';
      cy.get('.search-form input').type(searchQuery);
      cy.get('.search-form').submit();
      
      // Verify search results and highlighting
      cy.get('.media-card').should('exist');
      cy.get('.highlight').should('contain', searchQuery);
    });
  });
}); 