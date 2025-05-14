// Shared test utilities, mocks, and fixtures will go here.

import React from 'react';
import { render as rtlRender } from '@testing-library/react';
import { configureStore } from '@reduxjs/toolkit';
import { Provider } from 'react-redux';
import { BrowserRouter } from 'react-router-dom';
import { ThemeProvider } from '@mui/material/styles';
import { MediaAsset, User } from '../types';
import { rootReducer } from '../store/rootReducer';
import { lightTheme } from '../theme';
import { AuthProvider } from '../contexts/AuthContext';

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 B';
  const k = 1024;
  const sizes = ['B', 'KB', 'MB', 'GB', 'TB'];
  const i = Math.floor(Math.log(bytes) / Math.log(k));
  return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
}

export function createMockMediaAsset(overrides?: Partial<MediaAsset>): MediaAsset {
  return {
    id: 'test-asset-id',
    filename: 'test-file.jpg',
    size: 1024,
    type: 'image',
    mimeType: 'image/jpeg',
    thumbnailUrl: 'http://example.com/thumbnail.jpg',
    url: 'http://example.com/file.jpg',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

export function createMockUser(overrides?: Partial<User>): User {
  return {
    id: 'test-user-id',
    email: 'test@example.com',
    name: 'Test User',
    role: 'user',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString(),
    ...overrides,
  };
}

interface WrapperProps {
  children: React.ReactNode;
  initialState?: any;
}

function render(
  ui: React.ReactElement,
  {
    initialState = {},
    store = configureStore({
      reducer: rootReducer,
      preloadedState: initialState,
    }),
    ...renderOptions
  } = {}
): ReturnType<typeof rtlRender> {
  function Wrapper({ children }: WrapperProps) {
    return (
      <Provider store={store}>
        <BrowserRouter>
          <ThemeProvider theme={lightTheme}>
            <AuthProvider>
              {children}
            </AuthProvider>
          </ThemeProvider>
        </BrowserRouter>
      </Provider>
    );
  }
  return rtlRender(ui, { wrapper: Wrapper, ...renderOptions });
}

// re-export everything
export * from '@testing-library/react';
export { render };
