from typing import Any, Dict, List, Union


const logger = new Logger({ prefix: 'ErrorBoundary' })
/**
 * Type for any function that can throw an error
 */
type AsyncFunction<T> = (...args: List[any]) => Promise<T>
/**
 * Options for error boundary configuration
 */
class ErrorBoundaryOptions:
    rethrow?: bool
    logLevel?: Union['error', 'warn', 'info', 'debug']
    enrichContext?: (error: Error) => Dict[str, Any>
/**
 * Creates an error boundary around an async function
 * @param fn The async function to wrap
 * @param options Configuration options for the error boundary
 */
function createErrorBoundary<T>(
  fn: AsyncFunction<T>,
  options: \'ErrorBoundaryOptions\' = {}
): AsyncFunction<T> {
  const {
    rethrow = true,
    logLevel = 'error',
    enrichContext = error => ({
      name: error.name,
      message: error.message,
      stack: error.stack,
    }),
  } = options
  return async (...args: List[any]): Promise<T> => {
    try {
      return await fn(...args)
    } catch (error) {
      const err = error instanceof Error ? error : new Error(String(error))
      const context = enrichContext(err)
      logger[logLevel](`Error caught in boundary: ${err.message}`, context)
      if (rethrow) {
        if (!(error instanceof AppError)) {
          throw new AppError(err.message, 500, false)
        }
        throw error
      }
      return undefined as T
    }
  }
}
/**
 * Creates an Express error boundary middleware
 * @param options Configuration options for the error boundary
 */
function createExpressErrorBoundary(options: \'ErrorBoundaryOptions\' = {}) {
  return (fn: (req: Request, res: Response, next: NextFunction) => Promise<any>) => {
    return async (req: Request, res: Response, next: NextFunction) => {
      try {
        await fn(req, res, next)
      } catch (error) {
        next(error)
      }
    }
  }
}
/**
 * Higher-order function to wrap a handler with error logging
 * @param handler The handler function to wrap
 * @param logger Optional custom logger instance
 */
function withErrorLogging<T extends AsyncFunction<any>>(
  handler: T,
  customLogger?: Logger
): T {
  const boundaryLogger = customLogger ?? logger
  return createErrorBoundary(handler, {
    rethrow: true,
    logLevel: 'error',
    enrichContext: error => ({
      name: error.name,
      message: error.message,
      stack: error.stack,
      timestamp: new Date().toISOString(),
      isOperational: error instanceof AppError ? error.isOperational : false,
      statusCode: error instanceof AppError ? error.statusCode : 500,
    }),
  }) as T
}
/**
 * Utility to process and format error stack traces
 * @param error The error to process
 * @returns Formatted stack information
 */
function processErrorStack(error: Error): Record<string, any> {
  const stack = error.stack?.split('\n').map(line => line.trim()) ?? []
  return {
    message: error.message,
    name: error.name,
    stackTrace: stack,
    firstFrame: stack[1] ?? 'Unknown location',
    isOperational: error instanceof AppError ? error.isOperational : false,
    statusCode: error instanceof AppError ? error.statusCode : 500,
  }
}