import '@testing-library/jest-dom';
import { configure } from '@testing-library/react';
import { setLogger } from 'react-query';

// Increase the default timeout for async tests
jest.setTimeout(10000);

// Configure React Testing Library
configure({
  testIdAttribute: 'data-testid',
});

// Silence React Query error logging in tests
setLogger({
  log: console.log,
  warn: console.warn,
  error: () => {},
});

// Mock IntersectionObserver
class IntersectionObserver {
  observe = jest.fn();
  disconnect = jest.fn();
  unobserve = jest.fn();
}

Object.defineProperty(window, 'IntersectionObserver', {
  writable: true,
  configurable: true,
  value: IntersectionObserver,
});

// Mock matchMedia
Object.defineProperty(window, 'matchMedia', {
  writable: true,
  value: jest.fn().mockImplementation(query => ({
    matches: false,
    media: query,
    onchange: null,
    addListener: jest.fn(),
    removeListener: jest.fn(),
    addEventListener: jest.fn(),
    removeEventListener: jest.fn(),
    dispatchEvent: jest.fn(),
  })),
});
