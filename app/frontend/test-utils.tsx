import React from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import userEvent from '@testing-library/user-event';
import { axe, toHaveNoViolations } from 'jest-axe';
import { ThemeProvider } from './components/theme/ThemeContext';
import { AuthProvider } from './components/auth/AuthContext';
import rootReducer from './store/rootReducer';

// Add jest-axe matchers
expect.extend(toHaveNoViolations);

interface ExtendedRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  preloadedState?: Record<string, unknown>;
  store?: ReturnType<typeof configureStore>;
  wrapper?: React.ComponentType<{ children: React.ReactNode }>;
}

// Create a custom render function that includes providers
function render(
  ui: React.ReactElement,
  {
    preloadedState = {},
    store = configureStore({ reducer: rootReducer, preloadedState }),
    wrapper: CustomWrapper,
    ...renderOptions
  }: ExtendedRenderOptions = {}
) {
  function DefaultWrapper({ children }: { children: React.ReactNode }) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          <ThemeProvider>
            <AuthProvider>
              {children}
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      </Provider>
    );
  }

  const Wrapper = CustomWrapper || DefaultWrapper;

  return {
    store,
    user: userEvent.setup(),
    ...rtlRender(ui, { wrapper: Wrapper, ...renderOptions }),
  };
}

// Mock file factory for upload tests
function createMockFile(name = 'test.png', type = 'image/png', size = 1024) {
  const file = new File(['test'], name, { type });
  Object.defineProperty(file, 'size', { value: size });
  return file;
}

// Mock response factory for API tests
function createMockResponse<T>(data: T, status = 200, statusText = 'OK') {
  return {
    data,
    status,
    statusText,
    headers: {},
    config: {},
  };
}

// Mock error factory for API tests
function createMockError(status = 500, message = 'Internal Server Error') {
  const error = new Error(message);
  Object.defineProperty(error, 'response', {
    value: {
      status,
      data: { message },
    },
  });
  return error;
}

// Helper to wait for loading states
async function waitForLoadingToFinish() {
  const { queryByTestId } = render(<div data-testid="loading" />);
  if (queryByTestId('loading')) {
    await waitForLoadingToFinish();
  }
}

// Helper to resize viewport for responsive tests
function setViewport(width: number, height = 768) {
  Object.defineProperty(window, 'innerWidth', { value: width });
  Object.defineProperty(window, 'innerHeight', { value: height });
  window.dispatchEvent(new Event('resize'));
}

// Re-export everything
export * from '@testing-library/react';
export {
  render,
  axe,
  createMockFile,
  createMockResponse,
  createMockError,
  waitForLoadingToFinish,
  setViewport,
}; 