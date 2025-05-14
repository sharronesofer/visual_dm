// Add custom matchers from jest-dom
import '@testing-library/jest-dom';

// Set up global test timeout
jest.setTimeout(10000);

// Mock global objects if needed
// Example: global.fetch = jest.fn();

// Clean up after each test
afterEach(() => {
  jest.clearAllMocks();
  jest.restoreAllMocks();
});

// Extend expect matchers
expect.extend({}); 