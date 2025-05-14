import { Request, Response, NextFunction } from 'express';
import { verifyToken, requiresMfaVerification } from '../utils/auth';

/**
 * Middleware to check if MFA verification is required
 * This should be used after the authentication middleware
 */
export const requireMfa = (req: Request, res: Response, next: NextFunction) => {
    try {
        // Get token from request (assuming auth middleware has already set req.user)
        const token = req.headers.authorization?.split(' ')[1];

        if (!token) {
            return res.status(401).json({ message: 'Authentication required' });
        }

        // Verify the token and check if MFA verification is required
        const decoded = verifyToken(token);

        // If user is payment-enabled and MFA is not verified, block access
        if (requiresMfaVerification(decoded)) {
            return res.status(403).json({
                message: 'MFA verification required',
                requiresMfa: true
            });
        }

        // MFA is not required or already verified, proceed
        next();
    } catch (error) {
        return res.status(401).json({ message: 'Invalid or expired token' });
    }
};

/**
 * Middleware to require MFA for payment-enabled users
 * Can be used on routes related to payments
 */
export const requirePaymentMfa = (req: Request, res: Response, next: NextFunction) => {
    try {
        // Get token from request (assuming auth middleware has already set req.user)
        const token = req.headers.authorization?.split(' ')[1];

        if (!token) {
            return res.status(401).json({ message: 'Authentication required' });
        }

        // Verify the token
        const decoded = verifyToken(token);

        // If user has payment enabled, require MFA verification
        if (decoded.paymentEnabled && !decoded.mfaVerified) {
            return res.status(403).json({
                message: 'MFA verification required for payment operations',
                requiresMfa: true
            });
        }

        // MFA is verified or not required, proceed
        next();
    } catch (error) {
        return res.status(401).json({ message: 'Invalid or expired token' });
    }
}; 