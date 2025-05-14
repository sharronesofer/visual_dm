describe('Chat Feature', () => {
  beforeEach(() => {
    // Reset database state
    cy.task('db:reset');
    
    // Intercept WebSocket connection
    cy.intercept('GET', '/ws/chat/**', (req) => {
      req.reply({
        statusCode: 101,
        headers: {
          'Upgrade': 'websocket',
          'Connection': 'Upgrade'
        }
      });
    });
  });

  it('allows users to join chat rooms and send messages', () => {
    // First user joins
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Verify connection success
    cy.get('[data-testid="chat-status"]').should('contain', 'Connected');
    cy.get('[data-testid="room-name"]').should('contain', 'test-room');
    cy.get('[data-testid="user-list"]').should('contain', 'user1');

    // Open new tab for second user
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user2');
    cy.get('[data-testid="join-button"]').click();

    // Verify both users are listed
    cy.get('[data-testid="user-list"]').should('contain', 'user1');
    cy.get('[data-testid="user-list"]').should('contain', 'user2');

    // Send message from first user
    cy.get('[data-testid="message-input"]').type('Hello from user1{enter}');

    // Verify message appears in chat
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Hello from user1');

    // Send message from second user
    cy.get('[data-testid="message-input"]').type('Hi user1!{enter}');

    // Verify both messages appear in correct order
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').should('have.length', 2);
      cy.get('[data-testid="chat-message"]').first().should('contain', 'user1: Hello from user1');
      cy.get('[data-testid="chat-message"]').last().should('contain', 'user2: Hi user1!');
    });
  });

  it('shows chat history when joining room', () => {
    // Setup test data
    cy.task('db:seed', {
      messages: [
        { room: 'test-room', user: 'previous-user', content: 'Previous message 1' },
        { room: 'test-room', user: 'previous-user', content: 'Previous message 2' }
      ]
    });

    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('new-user');
    cy.get('[data-testid="join-button"]').click();

    // Verify history is loaded
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').should('have.length', 2);
      cy.get('[data-testid="chat-message"]').first().should('contain', 'Previous message 1');
      cy.get('[data-testid="chat-message"]').last().should('contain', 'Previous message 2');
    });
  });

  it('handles disconnections and reconnections', () => {
    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Simulate connection loss
    cy.window().then((win) => {
      win.dispatchEvent(new Event('offline'));
    });

    // Verify disconnection state
    cy.get('[data-testid="chat-status"]').should('contain', 'Disconnected');
    cy.get('[data-testid="reconnect-button"]').should('be.visible');

    // Simulate connection restore
    cy.window().then((win) => {
      win.dispatchEvent(new Event('online'));
    });

    // Verify automatic reconnection
    cy.get('[data-testid="chat-status"]').should('contain', 'Connected');
    cy.get('[data-testid="reconnect-button"]').should('not.exist');

    // Verify can still send messages
    cy.get('[data-testid="message-input"]').type('Back online!{enter}');
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Back online!');
  });

  it('enforces rate limiting', () => {
    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Send messages rapidly
    for (let i = 0; i < 10; i++) {
      cy.get('[data-testid="message-input"]').type(`Message ${i}{enter}`);
    }

    // Verify rate limit error
    cy.get('[data-testid="error-message"]').should('contain', 'Rate limit exceeded');

    // Wait for rate limit to reset
    cy.wait(60000); // 1 minute

    // Verify can send messages again
    cy.get('[data-testid="message-input"]').type('Rate limit reset{enter}');
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Rate limit reset');
  });

  it('handles room capacity limits', () => {
    // Set room capacity to 2 users
    cy.task('setRoomCapacity', { room: 'test-room', capacity: 2 });

    // First user joins
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Second user joins
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user2');
    cy.get('[data-testid="join-button"]').click();

    // Third user attempts to join
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user3');
    cy.get('[data-testid="join-button"]').click();

    // Verify capacity error
    cy.get('[data-testid="error-message"]').should('contain', 'Room is full');
  });

  it('supports emoji and special characters in messages', () => {
    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Send message with emojis and special characters
    const message = '👋 Hello! Special chars: ñ áéíóú &<>"';
    cy.get('[data-testid="message-input"]').type(`${message}{enter}`);

    // Verify message appears correctly
    cy.get('[data-testid="chat-messages"]').should('contain', `user1: ${message}`);
  });

  it('persists messages across page reloads', () => {
    // Join room and send message
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();
    cy.get('[data-testid="message-input"]').type('Test message{enter}');

    // Reload page
    cy.reload();

    // Rejoin room
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Verify message history includes previous message
    cy.get('[data-testid="chat-messages"]').should('contain', 'user1: Test message');
  });

  it('supports message formatting', () => {
    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Send formatted messages
    cy.get('[data-testid="message-input"]').type('*bold text*{enter}');
    cy.get('[data-testid="message-input"]').type('_italic text_{enter}');
    cy.get('[data-testid="message-input"]').type('`code text`{enter}');

    // Verify formatting
    cy.get('[data-testid="chat-messages"]').within(() => {
      cy.get('[data-testid="chat-message"]').first().find('strong').should('contain', 'bold text');
      cy.get('[data-testid="chat-message"]').eq(1).find('em').should('contain', 'italic text');
      cy.get('[data-testid="chat-message"]').last().find('code').should('contain', 'code text');
    });
  });

  it('handles long messages and auto-scrolling', () => {
    // Join room
    cy.visit('/chat/test-room');
    cy.get('[data-testid="username-input"]').type('user1');
    cy.get('[data-testid="join-button"]').click();

    // Send many messages to fill the chat
    for (let i = 0; i < 50; i++) {
      cy.get('[data-testid="message-input"]').type(`Message ${i}{enter}`);
    }

    // Verify auto-scroll to bottom
    cy.get('[data-testid="chat-messages"]').then(($messages) => {
      const scrollTop = $messages[0].scrollTop;
      const scrollHeight = $messages[0].scrollHeight;
      const clientHeight = $messages[0].clientHeight;
      expect(scrollTop + clientHeight).to.equal(scrollHeight);
    });

    // Send another message
    cy.get('[data-testid="message-input"]').type('New message{enter}');

    // Verify still scrolled to bottom
    cy.get('[data-testid="chat-messages"]').then(($messages) => {
      const scrollTop = $messages[0].scrollTop;
      const scrollHeight = $messages[0].scrollHeight;
      const clientHeight = $messages[0].clientHeight;
      expect(scrollTop + clientHeight).to.equal(scrollHeight);
    });
  });
}); 