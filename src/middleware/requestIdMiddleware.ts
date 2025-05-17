import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';
import { addToRequestContext, getRequestContext } from './requestContext';

/**
 * Express middleware to ensure every request has a unique request ID for correlation
 * - Checks for X-Request-ID or X-Correlation-ID in headers
 * - Generates a new UUID if not present
 * - Attaches requestId to req, request context, and response header
 *
 * NOTE: This middleware should be used after requestContextMiddleware
 */
export function requestIdMiddleware(req: Request, res: Response, next: NextFunction) {
    const headerId = req.headers['x-request-id'] || req.headers['x-correlation-id'];
    const requestId = typeof headerId === 'string' ? headerId : Array.isArray(headerId) ? headerId[0] : uuidv4();

    // Attach to request object for convenience
    (req as any).requestId = requestId;

    // Add to request context if available
    addToRequestContext('requestId', requestId);

    // Set response header for client visibility
    res.setHeader('X-Request-ID', requestId);

    next();
}

/**
 * Utility to get the current request ID from context
 */
export function getCurrentRequestId(): string | undefined {
    return getRequestContext()?.requestId;
} 