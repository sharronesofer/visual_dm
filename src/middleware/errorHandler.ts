import { Request, Response, NextFunction } from 'express';
import {
  AppError,
  NotFoundError,
  isAppError,
  toErrorResponse,
  processErrorStack,
  ErrorResponse,
} from '../errors';
import { logger } from '../utils/logger';

// Extend Express Request to include user property
declare module 'express' {
  interface Request {
    user?: any;
  }
}

/**
 * Handle 404 errors for routes that don't exist
 */
export function notFoundHandler(req: Request, _res: Response, next: NextFunction): void {
  const error = new NotFoundError('Route', req.originalUrl, `Route not found: ${req.originalUrl}`);
  next(error);
}

/**
 * Global error handling middleware
 */
export function errorHandler(error: Error, req: Request, res: Response, _next: NextFunction): void {
  // Process error stack for logging
  const stackInfo = processErrorStack(error);

  // Log error with appropriate level
  if (!stackInfo.isOperational) {
    logger.error('Unhandled error:', {
      error: stackInfo,
      path: req.path,
      method: req.method,
      query: req.query,
      body: req.body,
      user: req.user,
    });
  } else {
    logger.warn('Operational error:', {
      error: stackInfo,
      path: req.path,
      method: req.method,
    });
  }

  // Convert error to standardized response format
  const errorResponse = toErrorResponse(error);

  // Add stack trace in development
  if (process.env.NODE_ENV === 'development' && error.stack) {
    const details = (errorResponse.details as Record<string, unknown>) || {};
    errorResponse.details = {
      ...details,
      stack: error.stack,
    };
  }

  // Send error response
  res.status(errorResponse.statusCode).json({
    status: 'error',
    ...errorResponse,
  });
}

/**
 * Error boundary HOC for async route handlers
 */
export function asyncErrorBoundary(handler: Function) {
  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    try {
      await handler(req, res, next);
    } catch (error) {
      next(error);
    }
  };
}

/**
 * Validate request against schema and handle validation errors
 */
export function validateRequest(schema: any) {
  return (req: Request, _res: Response, next: NextFunction): void => {
    try {
      const { error } = schema.validate(req.body, {
        abortEarly: false,
        stripUnknown: true,
      });

      if (error) {
        const validationErrors: Record<string, string[]> = {};

        error.details.forEach((detail: any) => {
          const path = detail.path.join('.');
          if (!validationErrors[path]) {
            validationErrors[path] = [];
          }
          validationErrors[path].push(detail.message);
        });

        throw new AppError('Validation failed', 'VALIDATION_ERROR', 400, validationErrors);
      }

      next();
    } catch (error) {
      next(error);
    }
  };
}
