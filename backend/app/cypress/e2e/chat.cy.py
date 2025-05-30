from typing import Any, Dict


describe('Chat Feature', () => {
  beforeEach(() => {
    cy.task('db:reset')
    cy.intercept('GET', '/ws/chat/**', (req) => {
      req.reply({
        statusCode: 101,
        headers: Dict[str, Any]
      })
    })
  })
  it('allows users to join chat rooms and send messages', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="chat-status"]').should('contain', 'Connected')
    cy.get('[data-testid="room-name"]').should('contain', 'test-room')
    cy.get('[data-testid="user-list"]').should('contain', 'user1')
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user2')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="user-list"]').should('contain', 'user1')
    cy.get('[data-testid="user-list"]').should('contain', 'user2')
    cy.get('[data-testid="message-input"]').type('Hello from user1{enter}')
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Hello from user1')
    cy.get('[data-testid="message-input"]').type('Hi user1!{enter}')
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').should('have.length', 2)
      cy.get('[data-testid="chat-message"]').first().should('contain', 'user1: Hello from user1')
      cy.get('[data-testid="chat-message"]').last().should('contain', 'user2: Hi user1!')
    })
  })
  it('shows chat history when joining room', () => {
    cy.task('db:seed', {
      messages: [
        { room: 'test-room', user: 'previous-user', content: 'Previous message 1' },
        { room: 'test-room', user: 'previous-user', content: 'Previous message 2' }
      ]
    })
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('new-user')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').should('have.length', 2)
      cy.get('[data-testid="chat-message"]').first().should('contain', 'Previous message 1')
      cy.get('[data-testid="chat-message"]').last().should('contain', 'Previous message 2')
    })
  })
  it('handles disconnections and reconnections', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.window().then((win) => {
      win.dispatchEvent(new Event('offline'))
    })
    cy.get('[data-testid="chat-status"]').should('contain', 'Disconnected')
    cy.get('[data-testid="reconnect-button"]').should('be.visible')
    cy.window().then((win) => {
      win.dispatchEvent(new Event('online'))
    })
    cy.get('[data-testid="chat-status"]').should('contain', 'Connected')
    cy.get('[data-testid="reconnect-button"]').should('not.exist')
    cy.get('[data-testid="message-input"]').type('Back online!{enter}')
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Back online!')
  })
  it('enforces rate limiting', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    for (let i = 0; i < 10; i++) {
      cy.get('[data-testid="message-input"]').type(`Message ${i}{enter}`)
    }
    cy.get('[data-testid="error-message"]').should('contain', 'Rate limit exceeded')
    cy.wait(60000) 
    cy.get('[data-testid="message-input"]').type('Rate limit reset{enter}')
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Rate limit reset')
  })
  it('handles room capacity limits', () => {
    cy.task('setRoomCapacity', { room: 'test-room', capacity: 2 })
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user2')
    cy.get('[data-testid="join-button"]').click()
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user3')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="error-message"]').should('contain', 'Room is full')
  })
  it('supports emoji and special characters in messages', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    const message = '👋 Hello! Special chars: ñ áéíóú &<>"'
    cy.get('[data-testid="message-input"]').type(`${message}{enter}`)
    cy.get('[data-testid="chat-messages"]').should('contain', `user1: ${message}`)
  })
  it('persists messages across page reloads', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="message-input"]').type('Test message{enter}')
    cy.reload()
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Test message')
  })
  it('supports message formatting', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    cy.get('[data-testid="message-input"]').type('*bold text*{enter}')
    cy.get('[data-testid="message-input"]').type('_italic text_{enter}')
    cy.get('[data-testid="message-input"]').type('`code text`{enter}')
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').first().find('strong').should('contain', 'bold text')
      cy.get('[data-testid="chat-message"]').eq(1).find('em').should('contain', 'italic text')
      cy.get('[data-testid="chat-message"]').last().find('code').should('contain', 'code text')
    })
  })
  it('handles long messages and auto-scrolling', () => {
    cy.visit('/chat/test-room')
    cy.get('[data-testid="username-input"]').type('user1')
    cy.get('[data-testid="join-button"]').click()
    for (let i = 0; i < 50; i++) {
      cy.get('[data-testid="message-input"]').type(`Message ${i}{enter}`)
    }
    cy.get('[data-testid="chat-messages"]').then(($messages) => {
      const scrollTop = $messages[0].scrollTop
      const scrollHeight = $messages[0].scrollHeight
      const clientHeight = $messages[0].clientHeight
      expect(scrollTop + clientHeight).to.equal(scrollHeight)
    })
    cy.get('[data-testid="message-input"]').type('New message{enter}')
    cy.get('[data-testid="chat-messages"]').then(($messages) => {
      const scrollTop = $messages[0].scrollTop
      const scrollHeight = $messages[0].scrollHeight
      const clientHeight = $messages[0].clientHeight
      expect(scrollTop + clientHeight).to.equal(scrollHeight)
    })
  })
}) 