import React from 'react';
import { render, screen, act } from '@testing-library/react';
import { ThemeProvider, useTheme } from '@/contexts/ThemeContext';

// Test component that uses the theme context
const TestComponent = () => {
  const { theme, toggleTheme } = useTheme();
  return (
    <div>
      <div data-testid="theme-value">{theme}</div>
      <button onClick={toggleTheme}>Toggle Theme</button>
    </div>
  );
};

describe('ThemeContext', () => {
  it('provides default theme value', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
  });

  it('toggles theme when button is clicked', () => {
    render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    
    act(() => {
      button.click();
    });
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
    
    act(() => {
      button.click();
    });
    expect(screen.getByTestId('theme-value')).toHaveTextContent('light');
  });

  it('provides theme value through useTheme hook', () => {
    const TestHookComponent = () => {
      const { theme } = useTheme();
      return <div data-testid="hook-theme">{theme}</div>;
    };

    render(
      <ThemeProvider>
        <TestHookComponent />
      </ThemeProvider>
    );

    expect(screen.getByTestId('hook-theme')).toHaveTextContent('light');
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

  it('preserves theme state across re-renders', () => {
    const { rerender } = render(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    
    act(() => {
      button.click();
    });
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');

    rerender(
      <ThemeProvider>
        <TestComponent />
      </ThemeProvider>
    );
    expect(screen.getByTestId('theme-value')).toHaveTextContent('dark');
  });

  it('allows nested providers with independent state', () => {
    render(
      <ThemeProvider>
        <div data-testid="outer">
          <TestComponent />
          <ThemeProvider>
            <div data-testid="inner">
              <TestComponent />
            </div>
          </ThemeProvider>
        </div>
      </ThemeProvider>
    );

    const [outerButton, innerButton] = screen.getAllByRole('button');
    const [outerTheme, innerTheme] = screen.getAllByTestId('theme-value');

    // Initially both themes are light
    expect(outerTheme).toHaveTextContent('light');
    expect(innerTheme).toHaveTextContent('light');

    // Toggle outer theme
    act(() => {
      outerButton.click();
    });
    expect(outerTheme).toHaveTextContent('dark');
    expect(innerTheme).toHaveTextContent('light');

    // Toggle inner theme
    act(() => {
      innerButton.click();
    });
    expect(outerTheme).toHaveTextContent('dark');
    expect(innerTheme).toHaveTextContent('dark');
  });

  it('updates all consumers when theme changes', () => {
    const ConsumerOne = () => {
      const { theme } = useTheme();
      return <div data-testid="consumer-one">{theme}</div>;
    };

    const ConsumerTwo = () => {
      const { theme } = useTheme();
      return <div data-testid="consumer-two">{theme}</div>;
    };

    render(
      <ThemeProvider>
        <ConsumerOne />
        <TestComponent />
        <ConsumerTwo />
      </ThemeProvider>
    );

    const button = screen.getByRole('button');
    const consumerOne = screen.getByTestId('consumer-one');
    const consumerTwo = screen.getByTestId('consumer-two');
    const themeValue = screen.getByTestId('theme-value');

    expect(consumerOne).toHaveTextContent('light');
    expect(consumerTwo).toHaveTextContent('light');
    expect(themeValue).toHaveTextContent('light');

    act(() => {
      button.click();
    });

    expect(consumerOne).toHaveTextContent('dark');
    expect(consumerTwo).toHaveTextContent('dark');
    expect(themeValue).toHaveTextContent('dark');
  });
}); 