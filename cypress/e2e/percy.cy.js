describe('Percy Visual Test', () => { it('takes a snapshot', () => { cy.visit('/'); cy.percySnapshot('Home Page'); }); });
