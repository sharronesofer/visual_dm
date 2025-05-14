import { check, sleep } from 'k6';
import ws from 'k6/ws';
import http from 'k6/http';
import { Rate } from 'k6/metrics';

// Custom metrics
const messageRate = new Rate('message_send_rate');
const connectionRate = new Rate('connection_success_rate');
const disconnectionRate = new Rate('clean_disconnection_rate');

// Test configuration
export const options = {
  // Test scenarios
  scenarios: {
    // Constant load test
    constant_load: {
      executor: 'constant-vus',
      vus: 50,
      duration: '5m',
    },
    // Ramp-up test
    ramp_up: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100 users
        { duration: '2m', target: 0 },    // Ramp down to 0
      ],
    },
    // Stress test
    stress_test: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '3m', target: 200 },  // Ramp up to 200 users
        { duration: '5m', target: 200 },  // Stay at 200 users
        { duration: '2m', target: 0 },    // Ramp down to 0
      ],
    },
  },
  // Test thresholds
  thresholds: {
    'message_send_rate': ['rate>0.95'],  // 95% of messages should be sent successfully
    'connection_success_rate': ['rate>0.98'],  // 98% of connections should be successful
    'clean_disconnection_rate': ['rate>0.95'],  // 95% of disconnections should be clean
    'http_req_duration': ['p(95)<500'],  // 95% of requests should complete within 500ms
    'ws_connecting_duration': ['p(95)<1000'],  // 95% of WS connections should establish within 1s
    'ws_session_duration': ['p(95)>30000'],  // 95% of WS sessions should last at least 30s
  },
};

// Helper function to generate random room names
function getRandomRoom() {
  return `room-${Math.floor(Math.random() * 10)}`;  // 10 different rooms
}

// Helper function to generate random user names
function getRandomUser() {
  return `user-${Math.floor(Math.random() * 1000000)}`;
}

// Helper function to generate random messages
function getRandomMessage() {
  const messages = [
    'Hello everyone!',
    'How are you doing?',
    'Nice to meet you all!',
    'This is a test message',
    'Having a great time here',
    'Anyone want to chat?',
    'Testing the chat system',
    'Hope this works well',
    'Performance testing in progress',
    'Load testing the chat'
  ];
  return messages[Math.floor(Math.random() * messages.length)];
}

export default function () {
  const room = getRandomRoom();
  const user = getRandomUser();
  const url = `ws://localhost:8000/ws/chat/${room}/${user}`;

  // WebSocket connection
  const response = ws.connect(url, {}, function (socket) {
    connectionRate.add(1);  // Record successful connection

    // Handle connection established message
    socket.on('open', () => {
      console.log(`VU ${__VU}: Connected to chat`);
    });

    // Handle incoming messages
    socket.on('message', (data) => {
      const message = JSON.parse(data);
      check(message, {
        'message has correct type': (msg) => msg.type !== undefined,
        'message has content': (msg) => msg.type === 'chat_message' ? msg.content !== undefined : true,
      });
    });

    // Send messages periodically
    const interval = setInterval(() => {
      try {
        socket.send(JSON.stringify({
          type: 'message',
          content: getRandomMessage()
        }));
        messageRate.add(1);  // Record successful message send
      } catch (e) {
        messageRate.add(0);  // Record failed message send
        console.error(`VU ${__VU}: Failed to send message:`, e);
      }
    }, 5000);  // Send message every 5 seconds

    // Cleanup on test end
    socket.on('close', () => {
      clearInterval(interval);
      disconnectionRate.add(1);  // Record clean disconnection
    });
  });

  check(response, {
    'status is 101': (r) => r && r.status === 101,
  });

  // Keep connection alive for test duration
  sleep(60);  // Each VU stays connected for 1 minute
}

// Test setup
export function setup() {
  // Create test rooms if needed
  for (let i = 0; i < 10; i++) {
    http.post(`http://localhost:8000/api/rooms`, JSON.stringify({
      name: `room-${i}`,
      capacity: 100  // Allow up to 100 users per room
    }), {
      headers: { 'Content-Type': 'application/json' },
    });
  }
}

// Test teardown
export function teardown(data) {
  // Cleanup test rooms if needed
  for (let i = 0; i < 10; i++) {
    http.del(`http://localhost:8000/api/rooms/room-${i}`);
  }
} 