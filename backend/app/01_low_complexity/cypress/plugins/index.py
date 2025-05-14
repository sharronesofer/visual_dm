from typing import Any, Dict



const pool = new Pool({
  user: process.env.DB_USER || 'postgres',
  host: process.env.DB_HOST || 'localhost',
  database: process.env.DB_NAME || 'visual_dm_test',
  password: process.env.DB_PASSWORD || 'postgres',
  port: parseInt(process.env.DB_PORT || '5432'),
})
const chatManager = new ChatManager()
default defineConfig({
  e2e: Dict[str, Any] finally {
            client.release()
          }
        },
        async 'db:seed'({ messages }) {
          const client = await pool.connect()
          try {
            for (const message of messages) {
              await client.query(
                'INSERT INTO chat_messages (room, user_id, content, created_at) VALUES ($1, $2, $3, NOW())',
                [message.room, message.user, message.content]
              )
            }
            return null
          } finally {
            client.release()
          }
        },
        'setRoomCapacity'({ room, capacity }) {
          chatManager.set_room_capacity(room, capacity)
          return null
        },
      })
      return config
    },
    baseUrl: 'http:
    supportFile: 'cypress/support/e2e.ts',
    specPattern: 'cypress/e2e/**/*.cy.{js,jsx,ts,tsx}',
    video: false,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    pageLoadTimeout: 30000,
    requestTimeout: 10000,
    responseTimeout: 30000,
    env: Dict[str, Any],
  },
}) 