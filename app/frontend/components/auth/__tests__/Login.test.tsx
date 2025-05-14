import React from 'react';
import { render, screen, waitFor } from '../../../test-utils';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import Login from '../Login';

// Mock the AuthContext
jest.mock('../AuthContext', () => ({
  useAuth: () => ({
    login: jest.fn().mockImplementation(async (email, password) => {
      if (email === 'invalid@example.com' || password === 'wrongpassword') {
        throw new Error('Invalid email or password');
      }
      if (email === 'network@error.com') {
        throw new Error('Network error');
      }
      return Promise.resolve();
    }),
  }),
}));

describe('Login Component', () => {
  it('renders login form', () => {
    render(<Login />);
    
    expect(screen.getByLabelText(/email/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument();
    expect(screen.getByRole('button', { name: /login/i })).toBeInTheDocument();
  });

  it('handles successful login', async () => {
    const user = userEvent.setup();
    render(<Login />);
    
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);
    
    expect(submitButton).toHaveTextContent(/logging in/i);
    await waitFor(() => {
      expect(submitButton).toHaveTextContent(/login/i);
    });
  });

  it('displays error message on invalid credentials', async () => {
    const user = userEvent.setup();
    render(<Login />);
    
    await user.type(screen.getByLabelText(/email/i), 'invalid@example.com');
    await user.type(screen.getByLabelText(/password/i), 'wrongpassword');
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText(/invalid email or password/i)).toBeInTheDocument();
    });
  });

  it('handles form validation', async () => {
    const user = userEvent.setup();
    render(<Login />);
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);
    
    // HTML5 validation will prevent form submission
    expect(screen.getByLabelText(/email/i)).toBeInvalid();
    expect(screen.getByLabelText(/password/i)).toBeInvalid();
  });

  it('disables submit button while loading', async () => {
    const user = userEvent.setup();
    render(<Login />);
    
    await user.type(screen.getByLabelText(/email/i), 'test@example.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);
    
    expect(submitButton).toBeDisabled();
    expect(submitButton).toHaveTextContent(/logging in/i);
  });

  it('handles network errors gracefully', async () => {
    const user = userEvent.setup();
    render(<Login />);
    
    await user.type(screen.getByLabelText(/email/i), 'network@error.com');
    await user.type(screen.getByLabelText(/password/i), 'password123');
    
    const submitButton = screen.getByRole('button', { name: /login/i });
    await user.click(submitButton);

    await waitFor(() => {
      expect(screen.getByText('Network error')).toBeInTheDocument();
    });
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<Login />);
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
}); 