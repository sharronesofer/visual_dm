// k6 Load Testing Configuration
import { SharedArray } from 'k6/data';
import { check } from 'k6';
import http from 'k6/http';

export const CONFIG = {
  // Base URL for the API
  baseUrl: __ENV.API_BASE_URL || 'http://localhost:5050/api',
  
  // Default headers
  defaultHeaders: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },

  // Load test scenarios
  scenarios: {
    // Smoke test - minimal load to verify functionality
    smoke: {
      executor: 'constant-vus',
      vus: 1,
      duration: '1m',
    },
    
    // Load test - normal expected load
    load: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '2m', target: 50 },  // Ramp up to 50 users
        { duration: '5m', target: 50 },  // Stay at 50 users
        { duration: '2m', target: 0 },   // Ramp down to 0
      ],
    },
    
    // Stress test - find the breaking point
    stress: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '3m', target: 100 },  // Ramp up to 100 users
        { duration: '5m', target: 100 },  // Stay at 100
        { duration: '3m', target: 200 },  // Ramp up to 200
        { duration: '5m', target: 200 },  // Stay at 200
        { duration: '3m', target: 0 },    // Ramp down
      ],
    },
    
    // Spike test - sudden surge in users
    spike: {
      executor: 'ramping-vus',
      startVUs: 0,
      stages: [
        { duration: '1m', target: 0 },    // Baseline
        { duration: '1m', target: 300 },  // Sudden spike
        { duration: '1m', target: 300 },  // Hold spike
        { duration: '1m', target: 0 },    // Return to baseline
      ],
    },
  },
  
  // Performance thresholds
  thresholds: {
    http_req_duration: ['p(95)<2000'], // 95% of requests should be below 2s
    http_req_failed: ['rate<0.1'],     // Error rate should be below 10%
  },
};

// Helper function to get auth token
export function getAuthToken(username, password) {
  const loginRes = http.post(
    `${CONFIG.baseUrl}/auth/login`,
    JSON.stringify({ username, password }),
    { headers: CONFIG.defaultHeaders }
  );
  
  if (loginRes.status === 200) {
    return loginRes.json('token');
  }
  return null;
}

// Helper function to check response
export function checkResponse(res, expectedStatus = 200) {
  const result = check(res, {
    'status is ok': (r) => r.status === expectedStatus,
    'response time < 2s': (r) => r.timings.duration < 2000,
  });
  
  if (!result) {
    console.warn(`Response check failed: Status ${res.status}, Duration ${res.timings.duration}ms`);
  }
  
  return result;
}

// Generate test data
export function generateTestData() {
  return {
    username: `testuser_${Date.now()}`,
    password: 'TestPass123!',
    email: `test_${Date.now()}@example.com`,
  };
}

// Get current scenario
export function getCurrentScenario() {
  return __ENV.SCENARIO || 'smoke';
}

// Export options based on selected scenario
export function getOptions() {
  const scenario = getCurrentScenario();
  return {
    scenarios: {
      [scenario]: CONFIG.scenarios[scenario]
    },
    thresholds: CONFIG.thresholds,
  };
} 