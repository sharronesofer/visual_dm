import React from 'react';
import { render, screen } from '../../../test-utils';
import userEvent from '@testing-library/user-event';
import { axe } from 'jest-axe';
import { ThemeProvider, useTheme } from '../ThemeContext';

// Test component that uses the theme context
const TestComponent = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <span>Current theme: {theme}</span>
      <button onClick={toggleTheme}>Toggle theme</button>
    </div>
  );
};

describe('ThemeContext', () => {
  it('provides default theme value', () => {
    render(<TestComponent />, {
      wrapper: ThemeProvider,
    });
    
    expect(screen.getByText('Current theme: light')).toBeInTheDocument();
  });

  it('toggles theme when button is clicked', async () => {
    const user = userEvent.setup();
    render(<TestComponent />, {
      wrapper: ThemeProvider,
    });
    
    const toggleButton = screen.getByRole('button', { name: /toggle theme/i });
    
    // Initial state
    expect(screen.getByText('Current theme: light')).toBeInTheDocument();
    
    // Toggle to dark
    await user.click(toggleButton);
    expect(screen.getByText('Current theme: dark')).toBeInTheDocument();
    
    // Toggle back to light
    await user.click(toggleButton);
    expect(screen.getByText('Current theme: light')).toBeInTheDocument();
  });

  it('applies theme class to container div', () => {
    const { container } = render(<TestComponent />, {
      wrapper: ThemeProvider,
    });
    
    const themeContainer = container.querySelector('[data-theme]');
    expect(themeContainer).toHaveAttribute('data-theme', 'light');
  });

  it('throws error when useTheme is used outside provider', () => {
    // Suppress console.error for this test
    const consoleSpy = jest.spyOn(console, 'error');
    consoleSpy.mockImplementation(() => {});

    expect(() => {
      render(<TestComponent />);
    }).toThrow('useTheme must be used within a ThemeProvider');

    consoleSpy.mockRestore();
  });

  it('has no accessibility violations', async () => {
    const { container } = render(<TestComponent />, {
      wrapper: ThemeProvider,
    });
    
    const results = await axe(container);
    expect(results).toHaveNoViolations();
  });
}); 