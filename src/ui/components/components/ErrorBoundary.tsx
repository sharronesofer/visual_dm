import React, {
  Component,
  ReactNode,
  createContext,
  useContext,
  useCallback,
} from 'react';
import { formatError, sanitizeErrorForClient } from '../utils/error-utils';
import { logger } from '../utils/logger';
import './ErrorBoundary.css';

/**
 * Error recovery context interface
 */
interface ErrorRecoveryContextType {
  reset: () => void;
  retry: () => void;
  hasError: boolean;
  error: Error | null;
}

/**
 * Error boundary props interface
 */
interface ErrorBoundaryProps {
  children: ReactNode;
  fallback?:
    | ReactNode
    | ((error: Error, retry: () => void, reset: () => void) => ReactNode);
  onError?: (error: Error, errorInfo: React.ErrorInfo) => void;
  onReset?: () => void;
  onRetry?: () => void;
  errorGroup?: string;
}

/**
 * Error boundary state interface
 */
interface ErrorBoundaryState {
  error: Error | null;
  hasError: boolean;
}

// Create error recovery context
const ErrorRecoveryContext = createContext<ErrorRecoveryContextType>({
  reset: () => {},
  retry: () => {},
  hasError: false,
  error: null,
});

/**
 * Default fallback component for error states
 */
const DefaultFallback: React.FC<{
  error: Error;
  retry: () => void;
  reset: () => void;
}> = ({ error, retry, reset }) => (
  <div className="error-boundary-fallback">
    <h2>Something went wrong</h2>
    <pre>{error.message}</pre>
    <div className="error-boundary-actions">
      <button onClick={retry}>Retry</button>
      <button onClick={reset}>Reset</button>
    </div>
  </div>
);

/**
 * Error boundary component for catching and handling React errors
 */
export class ErrorBoundary extends Component<
  ErrorBoundaryProps,
  ErrorBoundaryState
> {
  // Track mounted state to prevent setState after unmount
  private mounted: boolean = false;

  // Store original children for reset functionality
  private readonly originalChildren: ReactNode;

  // Error deduplication cache
  private static errorCache = new Map<string, number>();

  constructor(props: ErrorBoundaryProps) {
    super(props);
    this.state = { error: null, hasError: false };
    this.originalChildren = props.children;
  }

  /**
   * Reset error state and restore original children
   */
  reset = () => {
    if (this.mounted) {
      this.setState({ error: null, hasError: false });
      this.props.onReset?.();
    }
  };

  /**
   * Retry the operation that caused the error
   */
  retry = () => {
    if (this.mounted) {
      this.setState({ error: null, hasError: false });
      this.props.onRetry?.();
    }
  };

  componentDidMount() {
    this.mounted = true;
  }

  componentWillUnmount() {
    this.mounted = false;
  }

  /**
   * Handle errors during rendering
   */
  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { error, hasError: true };
  }

  /**
   * Handle errors caught during lifecycle methods
   */
  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    // Format and sanitize error for logging
    const formattedError = formatError(error);
    const sanitizedError = sanitizeErrorForClient(formattedError);

    // Deduplicate errors
    const errorKey = `${error.name}:${error.message}`;
    const lastOccurrence = ErrorBoundary.errorCache.get(errorKey) || 0;
    const now = Date.now();

    // Only log if error hasn't occurred in the last 5 minutes
    if (now - lastOccurrence > 5 * 60 * 1000) {
      ErrorBoundary.errorCache.set(errorKey, now);

      // Log error with context
      logger.error('UI Error Boundary caught error', error, {
        sanitizedError,
        componentStack: errorInfo.componentStack,
        errorGroup: this.props.errorGroup,
      });
    }

    // Call onError callback if provided
    this.props.onError?.(error, errorInfo);
  }

  render() {
    const { hasError, error } = this.state;
    const { children, fallback } = this.props;

    if (hasError && error) {
      // Render custom fallback if provided
      if (fallback) {
        if (typeof fallback === 'function') {
          return fallback(error, this.retry, this.reset);
        }
        return fallback;
      }

      // Render default fallback
      return (
        <DefaultFallback error={error} retry={this.retry} reset={this.reset} />
      );
    }

    // Provide error recovery context to children
    return (
      <ErrorRecoveryContext.Provider
        value={{
          reset: this.reset,
          retry: this.retry,
          hasError,
          error,
        }}
      >
        {children}
      </ErrorRecoveryContext.Provider>
    );
  }
}

/**
 * Hook for accessing error boundary context
 */
export function useErrorBoundary() {
  const context = useContext(ErrorRecoveryContext);

  if (!context) {
    throw new Error('useErrorBoundary must be used within an ErrorBoundary');
  }

  return context;
}

/**
 * Hook for error recovery functionality
 */
export function useErrorRecovery() {
  const { reset, retry, hasError, error } = useErrorBoundary();

  const handleReset = useCallback(() => {
    reset();
  }, [reset]);

  const handleRetry = useCallback(() => {
    retry();
  }, [retry]);

  return {
    reset: handleReset,
    retry: handleRetry,
    hasError,
    error,
  };
}

/**
 * Higher-order component for wrapping components with error boundary
 */
export function withErrorBoundary<P extends object>(
  WrappedComponent: React.ComponentType<P>,
  boundaryProps?: Omit<ErrorBoundaryProps, 'children'>
) {
  return function WithErrorBoundary(props: P) {
    return (
      <ErrorBoundary {...boundaryProps}>
        <WrappedComponent {...props} />
      </ErrorBoundary>
    );
  };
}
