/// <reference types="cypress" />

declare namespace Cypress {
  interface Chainable<Subject = any> {
    task(event: string, arg?: any): Chainable<any>;
    intercept(method: string, url: string | RegExp, routeHandler?: any): Chainable<any>;
    // Add other custom commands here if needed
  }
} 