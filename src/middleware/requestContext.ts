/**
 * Request context handling middleware and utilities
 * This module provides functionality to track request context throughout the request lifecycle
 */

import { AsyncLocalStorage } from 'async_hooks';
import { Request, Response, NextFunction } from 'express';
import { v4 as uuidv4 } from 'uuid';

// Define the shape of the request context
export interface RequestContext {
    /** Unique ID for the current request */
    requestId: string;
    /** Start time of the request (for performance tracking) */
    startTime: number;
    /** User ID if authenticated */
    userId?: string | number;
    /** Additional custom context properties */
    [key: string]: unknown;
}

// Create storage for the request context using AsyncLocalStorage
const asyncLocalStorage = new AsyncLocalStorage<RequestContext>();

// List of headers that may contain request IDs
const REQUEST_ID_HEADERS = [
    'x-request-id',
    'x-correlation-id',
    'request-id',
    'correlation-id',
];

/**
 * Middleware to initialize request context
 * This middleware should be added early in the middleware chain
 */
export function requestContextMiddleware(req: Request, res: Response, next: NextFunction) {
    // Check for existing request ID in headers
    let requestId: string | undefined;

    for (const header of REQUEST_ID_HEADERS) {
        const headerValue = req.headers[header];
        if (headerValue && typeof headerValue === 'string') {
            requestId = headerValue;
            break;
        }
    }

    // Generate a new request ID if none exists
    if (!requestId) {
        requestId = uuidv4();
    }

    // Add request ID to response headers
    res.setHeader('X-Request-ID', requestId);

    // Create the initial request context
    const requestContext: RequestContext = {
        requestId,
        startTime: Date.now(),
        // Add more properties as needed
    };

    // If user is authenticated, add user information
    if (req.user) {
        requestContext.userId = (req.user as any).id;
    }

    // Run the rest of the request with this context
    asyncLocalStorage.run(requestContext, () => {
        next();
    });
}

/**
 * Get the current request context
 * Returns undefined if called outside a request context
 */
export function getRequestContext(): RequestContext | undefined {
    return asyncLocalStorage.getStore();
}

/**
 * Add data to the current request context
 * @param key The key to add/update
 * @param value The value to set
 * @returns Whether the update was successful
 */
export function addToRequestContext(key: string, value: unknown): boolean {
    const store = asyncLocalStorage.getStore();
    if (!store) {
        return false;
    }

    store[key] = value;
    return true;
}

/**
 * Get a specific value from the request context
 * @param key The key to retrieve
 * @returns The value or undefined if not found or outside a request context
 */
export function getFromRequestContext(key: string): unknown | undefined {
    const store = asyncLocalStorage.getStore();
    if (!store) {
        return undefined;
    }

    return store[key];
}

/**
 * Get the current request ID
 * @returns The request ID or undefined if not available
 */
export function getRequestId(): string | undefined {
    const store = asyncLocalStorage.getStore();
    return store?.requestId;
}

/**
 * Utility to create headers with the current request ID
 * Useful for propagating request ID to downstream services
 */
export function createTraceHeaders(): Record<string, string> {
    const requestId = getRequestId();
    if (!requestId) {
        return {};
    }

    return {
        'X-Request-ID': requestId,
    };
}

// Extend Express Request type to include the requestContext property
declare global {
    namespace Express {
        interface Request {
            user?: any; // This should match your user type
        }
    }
} 