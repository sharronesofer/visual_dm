import { POIException, POIValidationException, POIIntegrationException, POIPersistenceException, POIConcurrencyException, POIAuthorizationException, POIUnknownException } from './index';
import { AppError } from './index';
// If a logging system exists, import it here. Otherwise, use console as fallback.
// import { logger } from '../logging';

/**
 * Factory for POI exception handlers for different application layers.
 */
export class POIExceptionHandlerFactory {
    /**
     * Returns an Express-style error-handling middleware for POI exceptions.
     * Usage: app.use(POIExceptionHandlerFactory.controllerHandler())
     */
    static controllerHandler() {
        // (err, req, res, next) signature for Express
        return function (err: unknown, req: any, res: any, next: any) {
            if (err instanceof POIException) {
                // Log error context
                // logger?.error?.(err) ||
                console.error('[POIException]', err.toJSON?.() || err);
                res.status(err.statusCode || 500).json(err.toJSON());
            } else if (err instanceof AppError) {
                // Fallback for other AppErrors
                // logger?.error?.(err) ||
                console.error('[AppError]', err.toJSON?.() || err);
                res.status(err.statusCode || 500).json(err.toJSON());
            } else {
                // logger?.error?.(err) ||
                console.error('[UnknownError]', err);
                res.status(500).json({
                    name: 'InternalServerError',
                    message: 'An unexpected error occurred',
                });
            }
        };
    }

    /**
     * Returns a service-layer handler for POI exceptions.
     * Usage: wrap business logic in try/catch and call this handler in catch.
     */
    static serviceHandler(onError?: (err: POIException) => void) {
        return function (err: unknown) {
            if (err instanceof POIException) {
                // logger?.error?.(err) ||
                console.error('[POIException]', err.toJSON?.() || err);
                if (onError) onError(err);
                // Optionally, implement fallback/recovery logic here
                throw err; // propagate if not handled
            } else if (err instanceof AppError) {
                // logger?.error?.(err) ||
                console.error('[AppError]', err.toJSON?.() || err);
                throw err;
            } else {
                // logger?.error?.(err) ||
                console.error('[UnknownError]', err);
                throw err;
            }
        };
    }

    /**
     * Returns a data access layer handler for POI persistence/concurrency exceptions.
     * Usage: wrap DB logic in try/catch and call this handler in catch.
     */
    static dataAccessHandler(onError?: (err: POIException) => void) {
        return function (err: unknown) {
            if (err instanceof POIPersistenceException || err instanceof POIConcurrencyException) {
                // logger?.error?.(err) ||
                console.error('[POIDataAccessException]', err.toJSON?.() || err);
                if (onError) onError(err);
                throw err;
            } else if (err instanceof POIException) {
                // logger?.error?.(err) ||
                console.error('[POIException]', err.toJSON?.() || err);
                throw err;
            } else if (err instanceof AppError) {
                // logger?.error?.(err) ||
                console.error('[AppError]', err.toJSON?.() || err);
                throw err;
            } else {
                // logger?.error?.(err) ||
                console.error('[UnknownError]', err);
                throw err;
            }
        };
    }
} 