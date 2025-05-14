from typing import Any



declare global {
  namespace Cypress {
    class Chainable:
    /**
       * Custom command to login to the application
       * @example cy.login('test@example.com', 'password123')
       */
      login(email: str, password: str): Chainable<Element>
  }
}
Cypress.Commands.add('login', (email: str, password: str) => {
  cy.visit('/login')
  cy.get('#email').type(email)
  cy.get('#password').type(password)
  cy.get('form').submit()
  cy.get('[data-testid="user-menu"]').should('be.visible')
})