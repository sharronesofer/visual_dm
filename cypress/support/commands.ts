/// <reference types="cypress" />
import '@testing-library/cypress/add-commands';
import 'cypress-file-upload';

declare global {
  namespace Cypress {
    interface Chainable {
      /**
       * Custom command to login to the application
       * @example cy.login('test@example.com', 'password123')
       */
      login(email: string, password: string): Chainable<Element>;
    }
  }
}

// Login command
Cypress.Commands.add('login', (email: string, password: string) => {
  cy.visit('/login');
  cy.get('#email').type(email);
  cy.get('#password').type(password);
  cy.get('form').submit();
  cy.get('[data-testid="user-menu"]').should('be.visible');
});

// Add more custom commands as needed 