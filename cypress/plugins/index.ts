import { defineConfig } from 'cypress';
import { Pool } from 'pg';
import { ChatManager } from '@/websocket/chat';

// Database connection pool
const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'visual_dm_test',
  password: process.env.DB_PASSWORD || 'postgres',
  port: parseInt(process.env.DB_PORT || '5432'),
});

// Chat manager instance for e2e tests
const chatManager = new ChatManager();

export default defineConfig({
  e2e: {
    setupNodeEvents(on, config) {
      // Database tasks
      on('task', {
        async 'db:reset'() {
          const client = await pool.connect();
          try {
            // Truncate all relevant tables
            await client.query('TRUNCATE chat_rooms, chat_messages CASCADE');
            return null;
          } finally {
            client.release();
          }
        },

        async 'db:seed'({ messages }) {
          const client = await pool.connect();
          try {
            // Insert test messages
            for (const message of messages) {
              await client.query(
                'INSERT INTO chat_messages (room, user_id, content, created_at) VALUES ($1, $2, $3, NOW())',
                [message.room, message.user, message.content]
              );
            }
            return null;
          } finally {
            client.release();
          }
        },

        // Chat manager tasks
        'setRoomCapacity'({ room, capacity }) {
          chatManager.set_room_capacity(room, capacity);
          return null;
        },
      });

      return config;
    },

    baseUrl: 'http://localhost:3000',
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 30000,
    requestTimeout: 10000,
    responseTimeout: 30000,
    
    env: {
      // Environment variables for tests
      API_URL: 'http://localhost:8000',
      WS_URL: 'ws://localhost:8000',
    },
  },
}); 