import React from 'react';
import { render, screen, waitFor } from '../../../test-utils';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { AuthProvider, useAuth } from '../AuthContext';

// Test component that uses the auth context
const TestComponent = () => {
  const { user, isAuthenticated, login, logout } = useAuth();
  return (
    <div>
      <div>Authentication status: {isAuthenticated ? 'Logged in' : 'Logged out'}</div>
      {user && <div>User: {user.email}</div>}
      <button onClick={() => login('test@example.com', 'password123')}>Login</button>
      <button onClick={logout}>Logout</button>
    </div>
  );
};

describe('AuthContext', () => {
  it('provides initial authentication state', () => {
    render(<TestComponent />, {
      wrapper: AuthProvider,
    });
    
    expect(screen.getByText('Authentication status: Logged out')).toBeInTheDocument();
    expect(screen.queryByText(/User:/)).not.toBeInTheDocument();
  });

  it('handles login successfully', async () => {
    const user = userEvent.setup();
    render(<TestComponent />, {
      wrapper: AuthProvider,
    });
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authentication status: Logged in')).toBeInTheDocument();
      expect(screen.getByText('User: test@example.com')).toBeInTheDocument();
    });
  });

  it('handles logout successfully', async () => {
    const user = userEvent.setup();
    render(<TestComponent />, {
      wrapper: AuthProvider,
    });
    
    // First login
    const loginButton = screen.getByRole('button', { name: /login/i });
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authentication status: Logged in')).toBeInTheDocument();
    });

    // Then logout
    const logoutButton = screen.getByRole('button', { name: /logout/i });
    await user.click(logoutButton);

    expect(screen.getByText('Authentication status: Logged out')).toBeInTheDocument();
    expect(screen.queryByText(/User:/)).not.toBeInTheDocument();
  });

  it('throws error when useAuth is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error');
    consoleSpy.mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useAuth must be used within an AuthProvider');

    consoleSpy.mockRestore();
  });

  it('handles login errors', async () => {
    // Mock the Promise.resolve to reject instead
    const mockError = new Error('Login failed');
    jest.spyOn(Promise, 'resolve').mockRejectedValueOnce(mockError);

    const user = userEvent.setup();
    render(<TestComponent />, {
      wrapper: AuthProvider,
    });
    
    const loginButton = screen.getByRole('button', { name: /login/i });
    await user.click(loginButton);

    await waitFor(() => {
      expect(screen.getByText('Authentication status: Logged out')).toBeInTheDocument();
    });

    // Clean up mock
    jest.restoreAllMocks();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<TestComponent />, {
      wrapper: AuthProvider,
    });
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
}); 