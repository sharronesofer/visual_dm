import http from 'k6/http';
import { check, group, sleep } from 'k6';
import { CONFIG, getAuthToken, checkResponse, generateTestData, getOptions } from './config.js';

// Initialize test data
const testData = generateTestData();
let authToken = null;

// Export options based on selected scenario
export const options = getOptions();

// Setup function - runs once per VU
export function setup() {
  // Create a test user and get auth token
  const registerRes = http.post(
    `${CONFIG.baseUrl}/auth/register`,
    JSON.stringify(testData),
    { headers: CONFIG.defaultHeaders }
  );
  
  checkResponse(registerRes, 200);
  
  // Get auth token
  authToken = getAuthToken(testData.username, testData.password);
  if (!authToken) {
    console.error('Failed to get auth token');
  }
  
  return { authToken };
}

// Main test function
export default function(data) {
  const headers = {
    ...CONFIG.defaultHeaders,
    'Authorization': `Bearer ${data.authToken}`,
  };

  group('Public Endpoints', function() {
    // Test public endpoints that don't require auth
    const healthRes = http.get(`${CONFIG.baseUrl}/health`);
    checkResponse(healthRes);
    
    sleep(1);
  });

  group('Authentication', function() {
    // Test login endpoint
    const loginRes = http.post(
      `${CONFIG.baseUrl}/auth/login`,
      JSON.stringify({
        username: testData.username,
        password: testData.password,
      }),
      { headers: CONFIG.defaultHeaders }
    );
    checkResponse(loginRes);
    
    sleep(1);
  });

  group('Protected Endpoints', function() {
    // Test protected endpoints that require auth
    const profileRes = http.get(
      `${CONFIG.baseUrl}/users/profile`,
      { headers }
    );
    checkResponse(profileRes);

    // Test campaign creation
    const campaignData = {
      name: `Test Campaign ${Date.now()}`,
      description: 'Load test campaign',
      settings: {
        theme: 'fantasy',
        visibility: 'private',
      },
    };
    
    const createCampaignRes = http.post(
      `${CONFIG.baseUrl}/campaigns`,
      JSON.stringify(campaignData),
      { headers }
    );
    checkResponse(createCampaignRes);

    // Get campaigns list
    const campaignsRes = http.get(
      `${CONFIG.baseUrl}/campaigns`,
      { headers }
    );
    checkResponse(campaignsRes);
    
    sleep(1);
  });

  group('Character Operations', function() {
    // Create character
    const characterData = {
      name: `Test Character ${Date.now()}`,
      race: 'Human',
      class: 'Fighter',
      level: 1,
      attributes: {
        strength: 15,
        dexterity: 14,
        constitution: 13,
        intelligence: 12,
        wisdom: 10,
        charisma: 8,
      },
    };
    
    const createCharRes = http.post(
      `${CONFIG.baseUrl}/characters`,
      JSON.stringify(characterData),
      { headers }
    );
    checkResponse(createCharRes);

    // Get character list
    const charactersRes = http.get(
      `${CONFIG.baseUrl}/characters`,
      { headers }
    );
    checkResponse(charactersRes);
    
    sleep(1);
  });

  // Add random sleep between requests to simulate real user behavior
  sleep(Math.random() * 3);
}

// Teardown function - runs once after all VUs complete
export function teardown(data) {
  // Cleanup test data if needed
  if (data.authToken) {
    const headers = {
      ...CONFIG.defaultHeaders,
      'Authorization': `Bearer ${data.authToken}`,
    };
    
    // Delete test user
    const deleteRes = http.del(
      `${CONFIG.baseUrl}/users/${testData.username}`,
      null,
      { headers }
    );
    checkResponse(deleteRes);
  }
} 