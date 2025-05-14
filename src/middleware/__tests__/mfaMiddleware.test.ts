import { Request, Response, NextFunction } from 'express';
import { requireMfa, requirePaymentMfa } from '../mfaMiddleware';
import { verifyToken, requiresMfaVerification } from '../../utils/auth';

// Mock dependencies
jest.mock('../../utils/auth', () => ({
    verifyToken: jest.fn(),
    requiresMfaVerification: jest.fn(),
}));

describe('MFA Middleware', () => {
    let mockRequest: Partial<Request>;
    let mockResponse: Partial<Response>;
    let nextFunction: NextFunction;

    beforeEach(() => {
        mockRequest = {
            headers: {
                authorization: 'Bearer test_token',
            },
        };

        mockResponse = {
            status: jest.fn().mockReturnThis(),
            json: jest.fn(),
        };

        nextFunction = jest.fn();

        // Reset mocks
        jest.clearAllMocks();
    });

    describe('requireMfa middleware', () => {
        it('should call next() if MFA verification is not required', () => {
            // Mock token verification
            (verifyToken as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                mfaVerified: true,
            });

            // Mock MFA verification check
            (requiresMfaVerification as jest.Mock).mockReturnValue(false);

            requireMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).toHaveBeenCalled();
            expect(mockResponse.status).not.toHaveBeenCalled();
        });

        it('should return 403 if MFA verification is required', () => {
            // Mock token verification
            (verifyToken as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: false,
            });

            // Mock MFA verification check
            (requiresMfaVerification as jest.Mock).mockReturnValue(true);

            requireMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(403);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'MFA verification required',
                requiresMfa: true,
            });
        });

        it('should return 401 if no token is provided', () => {
            mockRequest.headers = {};

            requireMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(401);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'Authentication required',
            });
        });

        it('should return 401 if the token is invalid', () => {
            // Mock token verification to throw an error
            (verifyToken as jest.Mock).mockImplementation(() => {
                throw new Error('Invalid token');
            });

            requireMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(401);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'Invalid or expired token',
            });
        });
    });

    describe('requirePaymentMfa middleware', () => {
        it('should call next() if user does not have payment enabled', () => {
            // Mock token verification
            (verifyToken as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: false,
            });

            requirePaymentMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).toHaveBeenCalled();
            expect(mockResponse.status).not.toHaveBeenCalled();
        });

        it('should call next() if user has payment enabled and MFA is verified', () => {
            // Mock token verification
            (verifyToken as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: true,
            });

            requirePaymentMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).toHaveBeenCalled();
            expect(mockResponse.status).not.toHaveBeenCalled();
        });

        it('should return 403 if user has payment enabled but MFA is not verified', () => {
            // Mock token verification
            (verifyToken as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: false,
            });

            requirePaymentMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(403);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'MFA verification required for payment operations',
                requiresMfa: true,
            });
        });

        it('should return 401 if no token is provided', () => {
            mockRequest.headers = {};

            requirePaymentMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(401);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'Authentication required',
            });
        });

        it('should return 401 if the token is invalid', () => {
            // Mock token verification to throw an error
            (verifyToken as jest.Mock).mockImplementation(() => {
                throw new Error('Invalid token');
            });

            requirePaymentMfa(mockRequest as Request, mockResponse as Response, nextFunction);

            expect(nextFunction).not.toHaveBeenCalled();
            expect(mockResponse.status).toHaveBeenCalledWith(401);
            expect(mockResponse.json).toHaveBeenCalledWith({
                message: 'Invalid or expired token',
            });
        });
    });
}); 