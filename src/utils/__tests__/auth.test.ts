import * as jwt from 'jsonwebtoken';
import { generateToken, verifyToken, requiresMfaVerification } from '../auth';

// Mock dependencies
jest.mock('jsonwebtoken');

describe('Authentication Utilities', () => {
    beforeEach(() => {
        jest.clearAllMocks();
    });

    describe('generateToken', () => {
        it('should include MFA verification status in token payload', () => {
            // Mock jwt.sign
            (jwt.sign as jest.Mock).mockReturnValue('test_token');

            const user = {
                id: 'user1',
                email: 'test@example.com',
                role: 'user',
                mfaVerified: true,
                paymentEnabled: true,
            };

            generateToken(user);

            // Check token payload includes MFA fields
            expect(jwt.sign).toHaveBeenCalledWith(
                expect.objectContaining({
                    mfaVerified: true,
                    paymentEnabled: true,
                }),
                expect.any(String),
                expect.any(Object)
            );
        });

        it('should default MFA verified to false if not provided', () => {
            // Mock jwt.sign
            (jwt.sign as jest.Mock).mockReturnValue('test_token');

            const user = {
                id: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
            };

            generateToken(user);

            // Check token payload has mfaVerified as false
            expect(jwt.sign).toHaveBeenCalledWith(
                expect.objectContaining({
                    mfaVerified: false,
                    paymentEnabled: true,
                }),
                expect.any(String),
                expect.any(Object)
            );
        });
    });

    describe('verifyToken', () => {
        it('should return decoded token payload', () => {
            const payload = {
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                mfaVerified: true,
                paymentEnabled: false,
            };

            // Mock jwt.verify
            (jwt.verify as jest.Mock).mockReturnValue(payload);

            const result = verifyToken('test_token');

            expect(result).toEqual(payload);
            expect(jwt.verify).toHaveBeenCalledWith('test_token', expect.any(String));
        });

        it('should throw error for invalid token', () => {
            // Mock jwt.verify to throw
            (jwt.verify as jest.Mock).mockImplementation(() => {
                throw new Error('Invalid token');
            });

            expect(() => {
                verifyToken('invalid_token');
            }).toThrow('Invalid token');
        });
    });

    describe('requiresMfaVerification', () => {
        it('should require MFA verification for payment-enabled user', () => {
            // Verify token when provided as string
            (jwt.verify as jest.Mock).mockReturnValue({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: false,
            });

            const result1 = requiresMfaVerification('test_token');
            expect(result1).toBe(true);

            // Direct payload object
            const result2 = requiresMfaVerification({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: false,
            });
            expect(result2).toBe(true);
        });

        it('should not require MFA verification for payment-enabled user with verified MFA', () => {
            // Direct payload object
            const result = requiresMfaVerification({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: true,
                mfaVerified: true,
            });

            expect(result).toBe(false);
        });

        it('should not require MFA verification for standard user', () => {
            // Direct payload object
            const result = requiresMfaVerification({
                userId: 'user1',
                email: 'test@example.com',
                role: 'user',
                paymentEnabled: false,
                mfaVerified: false,
            });

            expect(result).toBe(false);
        });
    });
}); 