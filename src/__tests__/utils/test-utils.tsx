import React, { ReactElement } from 'react';
import { render as rtlRender, RenderOptions, RenderResult } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { BrowserRouter } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';

// Create a custom render function that includes providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  route?: string;
  initialEntries?: string[];
  queryClient?: QueryClient;
}

function render(
  ui: ReactElement,
  {
    route = '/',
    initialEntries = [route],
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          gcTime: 0,
          staleTime: 0,
        },
      },
    }),
    ...renderOptions
  }: CustomRenderOptions = {}
): RenderResult & { user: ReturnType<typeof userEvent.setup> } {
  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <BrowserRouter>{children}</BrowserRouter>
      </QueryClientProvider>
    );
  }

  return {
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions }),
    user: userEvent.setup(),
  };
}

// Mock API response helper
interface MockApiResponse<T = any> {
  data?: T;
  error?: Error;
  status?: number;
}

function createMockApiResponse<T>({
  data,
  error,
  status = 200,
}: MockApiResponse<T>) {
  if (error) {
    return Promise.reject(error);
  }
  return Promise.resolve({
    data,
    status,
    ok: status >= 200 && status < 300,
    headers: new Headers(),
    json: () => Promise.resolve(data),
  });
}

// Mock local storage
const mockLocalStorage = {
  store: {} as Record<string, string>,
  getItem(key: string) {
    return this.store[key] || null;
  },
  setItem(key: string, value: string) {
    this.store[key] = value;
  },
  removeItem(key: string) {
    delete this.store[key];
  },
  clear() {
    this.store = {};
  },
};

// Mock intersection observer
function mockIntersectionObserver() {
  class MockIntersectionObserver {
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
  }

  Object.defineProperty(window, 'IntersectionObserver', {
    writable: true,
    configurable: true,
    value: MockIntersectionObserver,
  });
}

// Mock resize observer
function mockResizeObserver() {
  class MockResizeObserver {
    observe = jest.fn();
    unobserve = jest.fn();
    disconnect = jest.fn();
  }

  Object.defineProperty(window, 'ResizeObserver', {
    writable: true,
    configurable: true,
    value: MockResizeObserver,
  });
}

// Wait for element to be removed helper
async function waitForElementToBeRemoved(element: Element | null) {
  if (!element) return;
  
  await new Promise<void>((resolve) => {
    const observer = new MutationObserver(() => {
      if (!document.contains(element)) {
        observer.disconnect();
        resolve();
      }
    });

    observer.observe(document.body, {
      childList: true,
      subtree: true,
    });
  });
}

// Generate test IDs helper
function generateTestId(...parts: string[]): string {
  return parts.join('-');
}

// Mock date helper
function mockDate(isoDate: string) {
  const RealDate = Date;
  const mockDate = new RealDate(isoDate);

  jest.spyOn(global, 'Date').mockImplementation(function(this: DateConstructor, ...args: Parameters<DateConstructor>) {
    if (args.length) {
      return new RealDate(...args);
    }
    return mockDate;
  });
}

// Reset all mocks helper
function resetAllMocks() {
  jest.resetAllMocks();
  mockLocalStorage.clear();
}

export {
  render,
  createMockApiResponse,
  mockLocalStorage,
  mockIntersectionObserver,
  mockResizeObserver,
  waitForElementToBeRemoved,
  generateTestId,
  mockDate,
  resetAllMocks,
}; 