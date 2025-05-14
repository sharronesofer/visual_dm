import { Request, Response, NextFunction } from 'express';
import jwt from 'jsonwebtoken';

// Interface for JWT payload containing user info
interface UserPayload {
    userId: string;
    username: string;
    email: string;
    roles: string[];
    permissions?: string[];
}

// Extended Request interface to include authenticated user
export interface AuthenticatedRequest extends Request {
    user?: UserPayload;
}

/**
 * Middleware to authenticate users via JWT tokens
 * Extracts the token from the Authorization header and verifies it
 * Adds the decoded user payload to the request object
 */
export function authenticateUser(
    req: AuthenticatedRequest,
    res: Response,
    next: NextFunction
): void {
    const authHeader = req.headers.authorization;

    if (!authHeader) {
        res.status(401).json({
            status: 'error',
            message: 'Authentication required',
            code: 'AUTH_REQUIRED'
        });
        return;
    }

    // Format: "Bearer <token>"
    const token = authHeader.split(' ')[1];

    if (!token) {
        res.status(401).json({
            status: 'error',
            message: 'Invalid authorization format',
            code: 'INVALID_AUTH_FORMAT'
        });
        return;
    }

    try {
        // JWT secret should be in environment variables in production
        const JWT_SECRET = process.env.JWT_SECRET || 'development-secret-key';

        // Verify and decode the token
        const decoded = jwt.verify(token, JWT_SECRET) as UserPayload;

        // Attach user info to request
        req.user = decoded;

        next();
    } catch (error) {
        // Token verification failed
        res.status(401).json({
            status: 'error',
            message: 'Invalid or expired token',
            code: 'INVALID_TOKEN',
            details: process.env.NODE_ENV === 'development' ? error.message : undefined
        });
    }
}

/**
 * Middleware to check if the user has the required roles
 * Must be used after authenticateUser middleware
 * @param requiredRoles Array of roles that are allowed to access the route
 */
export function requireRoles(requiredRoles: string[]) {
    return (req: AuthenticatedRequest, res: Response, next: NextFunction): void => {
        // Ensure user is authenticated
        if (!req.user) {
            res.status(401).json({
                status: 'error',
                message: 'Authentication required',
                code: 'AUTH_REQUIRED'
            });
            return;
        }

        // Check if user has any of the required roles
        const hasRequiredRole = requiredRoles.some(role =>
            req.user?.roles.includes(role)
        );

        if (!hasRequiredRole) {
            res.status(403).json({
                status: 'error',
                message: 'Insufficient permissions',
                code: 'INSUFFICIENT_PERMISSIONS'
            });
            return;
        }

        next();
    };
}

export default {
    authenticateUser,
    requireRoles
}; 