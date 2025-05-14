import React from 'react';
import { render as rtlRender, RenderOptions } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { QueryClient, QueryClientProvider } from 'react-query';
import { responsiveTheme } from '../theme/responsiveTheme';
import '@testing-library/jest-dom';

// Create a custom render function that includes providers
interface CustomRenderOptions extends Omit<RenderOptions, 'wrapper'> {
  queryClient?: QueryClient;
}

function render(
  ui: React.ReactElement,
  {
    queryClient = new QueryClient({
      defaultOptions: {
        queries: {
          retry: false,
          cacheTime: 0,
        },
      },
    }),
    ...renderOptions
  }: CustomRenderOptions = {}
): ReturnType<typeof rtlRender> & { rerender: (ui: React.ReactElement) => ReturnType<typeof rtlRender>; unmount: () => void } {
  // Create a new div for the render
  const container = document.createElement('div');
  document.body.appendChild(container);

  function Wrapper({ children }: { children: React.ReactNode }) {
    return (
      <QueryClientProvider client={queryClient}>
        <ThemeProvider theme={responsiveTheme}>{children}</ThemeProvider>
      </QueryClientProvider>
    );
  }

  const result = rtlRender(ui, {
    wrapper: Wrapper,
    container,
    ...renderOptions,
  });

  return {
    ...result,
    rerender: (ui: React.ReactElement) =>
      render(ui, { container, ...renderOptions }),
    unmount: () => {
      result.unmount();
      document.body.removeChild(container);
    },
  };
}

// Mock response for character data
export const mockCharacterData = {
  race: 'Human',
  class: 'Fighter',
  background: 'Soldier',
  attributes: {
    strength: 15,
    dexterity: 14,
    constitution: 13,
    intelligence: 12,
    wisdom: 10,
    charisma: 8,
  },
  skills: ['Athletics', 'Intimidation'],
  equipment: ['Longsword', 'Chain Mail', 'Shield'],
};

// Mock API response
export const mockApiResponse = (data: any, delay = 0) => {
  return new Promise(resolve => {
    setTimeout(() => {
      resolve({
        ok: true,
        json: async () => data,
      });
    }, delay);
  });
};

// Mock error response
export const mockApiError = (status = 500, message = 'Server Error') => {
  return Promise.reject({
    status,
    message,
  });
};

// Create a mock resize observer
export class MockResizeObserver {
  observe = jest.fn();
  unobserve = jest.fn();
  disconnect = jest.fn();
}

// Re-export everything
export * from '@testing-library/react';
export { render };
