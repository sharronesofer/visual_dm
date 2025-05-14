import React from 'react';
import { render, screen, fireEvent } from '@testing-library/react';
import {
  ErrorBoundary,
  useErrorBoundary,
  useErrorRecovery,
  withErrorBoundary,
} from '../ErrorBoundary';
import { logger } from '../../utils/logger';

// Mock logger to prevent actual logging during tests
jest.mock('../../utils/logger', () => ({
  logger: {
    error: jest.fn(),
  },
}));

// Component that throws an error
const ErrorComponent: React.FC<{ shouldThrow?: boolean }> = ({
  shouldThrow = true,
}) => {
  if (shouldThrow) {
    throw new Error('Test error');
  }
  return <div>No error</div>;
};

// Component that uses error boundary hooks
const HookTestComponent: React.FC = () => {
  const { hasError, error, retry, reset } = useErrorRecovery();

  return (
    <div>
      {hasError ? (
        <>
          <div>Error: {error?.message}</div>
          <button onClick={retry}>Retry</button>
          <button onClick={reset}>Reset</button>
        </>
      ) : (
        <div>No error</div>
      )}
    </div>
  );
};

describe('ErrorBoundary', () => {
  // Clear mocks before each test
  beforeEach(() => {
    jest.clearAllMocks();
    jest.spyOn(console, 'error').mockImplementation(() => {});
  });

  afterEach(() => {
    jest.restoreAllMocks();
  });

  it('should render children when there is no error', () => {
    const { container } = render(
      <ErrorBoundary>
        <div>Test content</div>
      </ErrorBoundary>
    );

    expect(container).toHaveTextContent('Test content');
  });

  it('should render default fallback when error occurs', () => {
    const { container } = render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(container).toHaveTextContent('Something went wrong');
    expect(container).toHaveTextContent('Test error');
    expect(screen.getByText('Retry')).toBeInTheDocument();
    expect(screen.getByText('Reset')).toBeInTheDocument();
  });

  it('should render custom fallback component when error occurs', () => {
    const CustomFallback = () => <div>Custom error view</div>;

    const { container } = render(
      <ErrorBoundary fallback={<CustomFallback />}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(container).toHaveTextContent('Custom error view');
  });

  it('should render custom fallback function when error occurs', () => {
    const customFallback = (error: Error) => <div>Error: {error.message}</div>;

    const { container } = render(
      <ErrorBoundary fallback={customFallback}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(container).toHaveTextContent('Error: Test error');
  });

  it('should call onError when error occurs', () => {
    const onError = jest.fn();

    render(
      <ErrorBoundary onError={onError}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(onError).toHaveBeenCalledWith(
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('should log error with logger', () => {
    render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(logger.error).toHaveBeenCalledWith(
      'UI Error Boundary caught error',
      expect.any(Error),
      expect.objectContaining({
        componentStack: expect.any(String),
      })
    );
  });

  it('should deduplicate errors within 5 minutes', () => {
    const { rerender } = render(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(logger.error).toHaveBeenCalledTimes(1);

    // Rerender with same error
    rerender(
      <ErrorBoundary>
        <ErrorComponent />
      </ErrorBoundary>
    );

    expect(logger.error).toHaveBeenCalledTimes(1);
  });

  it('should reset error state when retry is clicked', () => {
    const onRetry = jest.fn();

    const { container } = render(
      <ErrorBoundary onRetry={onRetry}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Retry'));

    expect(onRetry).toHaveBeenCalled();
    expect(container).toHaveTextContent('Something went wrong');
  });

  it('should reset error state when reset is clicked', () => {
    const onReset = jest.fn();

    const { container } = render(
      <ErrorBoundary onReset={onReset}>
        <ErrorComponent />
      </ErrorBoundary>
    );

    fireEvent.click(screen.getByText('Reset'));

    expect(onReset).toHaveBeenCalled();
    expect(container).toHaveTextContent('Something went wrong');
  });
});

describe('useErrorBoundary hook', () => {
  it('should throw error when used outside ErrorBoundary', () => {
    const spy = jest.spyOn(console, 'error').mockImplementation(() => {});

    expect(() => {
      render(<HookTestComponent />);
    }).toThrow('useErrorBoundary must be used within an ErrorBoundary');

    spy.mockRestore();
  });

  it('should provide error context when used inside ErrorBoundary', () => {
    const { container } = render(
      <ErrorBoundary>
        <HookTestComponent />
      </ErrorBoundary>
    );

    expect(container).toHaveTextContent('No error');
  });
});

describe('withErrorBoundary HOC', () => {
  it('should wrap component with error boundary', () => {
    const WrappedComponent = withErrorBoundary(ErrorComponent, {
      fallback: <div>HOC fallback</div>,
    });

    const { container } = render(<WrappedComponent />);

    expect(container).toHaveTextContent('HOC fallback');
  });

  it('should pass through props to wrapped component', () => {
    const WrappedComponent = withErrorBoundary(ErrorComponent);

    const { container } = render(<WrappedComponent shouldThrow={false} />);

    expect(container).toHaveTextContent('No error');
  });
});
