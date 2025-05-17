import { Request, Response, NextFunction } from 'express';
import {
  AppError,
  NotFoundError,
  isAppError,
  toErrorResponse,
  processErrorStack,
  ErrorResponse,
  isValidationError,
  isNotFoundError,
  isClientError,
  isServerError,
  isOperationalError,
} from '../errors';
import { logger } from '../utils/logger';
import { getRequestContext } from './requestContext';

// Extend Express Request to include user property
declare module 'express' {
  interface Request {
    user?: any;
    requestId?: string;
  }
}

/**
 * Handle 404 errors for routes that don't exist
 * @param req Express request
 * @param _res Express response
 * @param next Express next function
 */
export function notFoundHandler(req: Request, _res: Response, next: NextFunction): void {
  const error = new NotFoundError('Route', req.originalUrl, `Route not found: ${req.originalUrl}`);
  next(error);
}

/**
 * Global error handling middleware (robust, best practices)
 * @param error The error thrown
 * @param req Express request
 * @param res Express response
 * @param _next Express next function
 */
export function errorHandler(error: Error, req: Request, res: Response, _next: NextFunction): void {
  const requestContext = getRequestContext();
  const requestId = requestContext?.requestId || (req as any).requestId;
  const userId = requestContext?.userId || req.user?.id;
  const timestamp = new Date().toISOString();
  const path = req.path;
  const method = req.method;
  const headers = req.headers;
  const query = req.query;
  const body = req.body;
  const duration = requestContext?.startTime ? Date.now() - requestContext.startTime : undefined;

  // Specialized error handling
  let statusCode = 500;
  let code = 'INTERNAL_SERVER_ERROR';
  let message = 'An unexpected error occurred.';
  let details: any = undefined;
  let isOperational = false;

  if (isAppError(error)) {
    statusCode = error.statusCode;
    code = error.code;
    message = error.message;
    details = error.details;
    isOperational = error.isOperational;
  } else if (isValidationError(error)) {
    statusCode = 400;
    code = 'VALIDATION_ERROR';
    message = error.message;
    details = (error as any).errors || error.details;
    isOperational = true;
  } else if (isNotFoundError(error)) {
    statusCode = 404;
    code = 'NOT_FOUND';
    message = error.message;
    isOperational = true;
  } else if (isClientError(error)) {
    statusCode = 400;
    code = 'CLIENT_ERROR';
    message = error.message;
    isOperational = true;
  } else if (isServerError(error)) {
    statusCode = 500;
    code = 'SERVER_ERROR';
    message = error.message;
    isOperational = false;
  } else if (isOperationalError(error)) {
    statusCode = 500;
    code = 'OPERATIONAL_ERROR';
    message = error.message;
    isOperational = true;
  }

  // Add more specialized error types as needed (auth, conflict, rate limit, etc.)
  // TODO: Add hooks for critical error reporting (e.g., Sentry, email)
  // TODO: Add rate limiting for repeated errors (by IP, user, error type)

  // Log error with full context and performance metrics
  const logMeta = {
    error: {
      name: error.name,
      message: error.message,
      stack: error.stack,
      code,
      statusCode,
      details,
      isOperational,
    },
    path,
    method,
    query,
    body,
    user: userId,
    requestId,
    timestamp,
    headers,
    durationMs: duration,
  };
  if (isOperational) {
    logger.warn('Operational error', logMeta);
  } else {
    logger.error('Programming/Unhandled error', logMeta);
  }

  // Build error response (consistent format)
  const errorResponse: ErrorResponse = {
    error: {
      code,
      message: isOperational ? message : 'An internal server error occurred.',
      statusCode,
      details: isOperational || process.env.NODE_ENV === 'development' ? details : undefined,
      requestId,
      timestamp,
    },
  };

  res.status(statusCode).json(errorResponse);
}

/**
 * Error boundary HOC for async route handlers
 * @param handler The async route handler
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
 * @param schema The validation schema
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
