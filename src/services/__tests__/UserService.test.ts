import { UserService } from '../UserService';
import { NotFoundError } from '../../errors/NotFoundError';
import { ValidationError } from '../../errors/ValidationError';
import * as mfaUtils from '../../utils/mfa';
import * as authUtils from '../../utils/auth';

// Mock dependencies
jest.mock('../../utils/mfa');
jest.mock('../../utils/auth');
jest.mock('../../utils/password', () => ({
    hashPassword: jest.fn().mockResolvedValue('hashed_password'),
    comparePassword: jest.fn().mockResolvedValue(true),
}));

describe('UserService', () => {
    let userService: UserService;
    const mockUser = {
        id: 'user1',
        email: 'test@example.com',
        password: 'hashed_password',
        username: 'testuser',
        role: 'user',
        mfaEnabled: false,
        mfaSecret: null,
        mfaBackupCodes: [],
        paymentEnabled: false,
        isActive: true,
        createdAt: new Date(),
        updatedAt: new Date(),
    };

    beforeEach(() => {
        userService = new UserService();

        // Mock base class methods
        userService.findById = jest.fn().mockResolvedValue({
            success: true,
            data: mockUser,
        });
        userService.update = jest.fn().mockResolvedValue({
            success: true,
            data: { ...mockUser },
        });
        userService.findByEmail = jest.fn().mockResolvedValue(mockUser);
        userService.handleError = jest.fn().mockImplementation((error) => ({
            success: false,
            error: error.message,
        }));

        // Mock MFA utilities
        (mfaUtils.generateMfaSecret as jest.Mock).mockReturnValue({
            secret: 'test_secret',
            otpauth_url: 'otpauth://totp/Visual_DM:test@example.com?secret=test_secret',
            backup_codes: ['AAAA-BBBB', 'CCCC-DDDD'],
        });
        (mfaUtils.verifyToken as jest.Mock).mockReturnValue(true);
        (mfaUtils.verifyBackupCode as jest.Mock).mockReturnValue('AAAA-BBBB');

        // Mock auth utilities
        (authUtils.generateToken as jest.Mock).mockReturnValue('jwt_token');
    });

    afterEach(() => {
        jest.clearAllMocks();
    });

    describe('login', () => {
        it('should include MFA status in login response', async () => {
            // Mock user with MFA enabled
            userService.findByEmail = jest.fn().mockResolvedValue({
                ...mockUser,
                mfaEnabled: true,
            });

            const result = await userService.login('test@example.com', 'password123');

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('requiresMfa', true);
        });

        it('should require MFA for payment-enabled users', async () => {
            // Mock user with payment enabled
            userService.findByEmail = jest.fn().mockResolvedValue({
                ...mockUser,
                paymentEnabled: true,
                mfaEnabled: false,
            });

            const result = await userService.login('test@example.com', 'password123');

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('requiresMfa', true);
        });

        it('should not require MFA for regular users', async () => {
            const result = await userService.login('test@example.com', 'password123');

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('requiresMfa', false);
        });
    });

    describe('setupMfa', () => {
        it('should generate and save MFA secret for a user', async () => {
            const result = await userService.setupMfa('user1');

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('secret', 'test_secret');
            expect(result.data).toHaveProperty('otpauth_url');
            expect(result.data).toHaveProperty('backup_codes');

            // Check that update was called with correct data
            expect(userService.update).toHaveBeenCalledWith('user1', {
                mfaSecret: 'test_secret',
                mfaBackupCodes: ['AAAA-BBBB', 'CCCC-DDDD'],
            });
        });

        it('should handle user not found error', async () => {
            userService.findById = jest.fn().mockResolvedValue({
                success: false,
                error: 'User not found',
            });

            const result = await userService.setupMfa('nonexistent');

            expect(result.success).toBe(false);
            expect(result.error).toBe('User not found');
        });
    });

    describe('enableMfa', () => {
        it('should enable MFA after verifying the token', async () => {
            // Mock user with MFA secret already setup
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaSecret: 'test_secret',
                },
            });

            const result = await userService.enableMfa('user1', '123456');

            expect(result.success).toBe(true);
            expect(result.data).toBe(true);

            // Check that MFA was enabled
            expect(userService.update).toHaveBeenCalledWith('user1', { mfaEnabled: true });
        });

        it('should fail if MFA setup is not completed', async () => {
            const result = await userService.enableMfa('user1', '123456');

            expect(result.success).toBe(false);
            expect(result.error).toBe('MFA setup not completed');
        });

        it('should fail if token is invalid', async () => {
            // Mock user with MFA secret already setup
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaSecret: 'test_secret',
                },
            });

            // Mock token verification to fail
            (mfaUtils.verifyToken as jest.Mock).mockReturnValue(false);

            const result = await userService.enableMfa('user1', '123456');

            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid MFA token');
        });
    });

    describe('verifyMfa', () => {
        beforeEach(() => {
            // Mock user with MFA enabled
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaEnabled: true,
                    mfaSecret: 'test_secret',
                    mfaBackupCodes: ['AAAA-BBBB', 'CCCC-DDDD'],
                },
            });
        });

        it('should verify a valid token and return a new JWT token', async () => {
            const result = await userService.verifyMfa({
                userId: 'user1',
                token: '123456',
            });

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('token', 'jwt_token');

            // Check that generate token was called with MFA verified flag
            expect(authUtils.generateToken).toHaveBeenCalledWith(
                expect.objectContaining({ mfaVerified: true })
            );
        });

        it('should verify a valid backup code and remove it from available codes', async () => {
            const result = await userService.verifyMfa({
                userId: 'user1',
                token: 'AAAA-BBBB',
                isBackupCode: true,
            });

            expect(result.success).toBe(true);
            expect(result.data).toHaveProperty('token');

            // Check that the used backup code was removed
            expect(userService.update).toHaveBeenCalledWith('user1', {
                mfaBackupCodes: ['CCCC-DDDD'],
            });
        });

        it('should fail if MFA is not enabled for the user', async () => {
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: mockUser,
            });

            const result = await userService.verifyMfa({
                userId: 'user1',
                token: '123456',
            });

            expect(result.success).toBe(false);
            expect(result.error).toBe('MFA not enabled for this user');
        });

        it('should fail if the token is invalid', async () => {
            // Mock token verification to fail
            (mfaUtils.verifyToken as jest.Mock).mockReturnValue(false);

            const result = await userService.verifyMfa({
                userId: 'user1',
                token: '123456',
            });

            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid MFA token or backup code');
        });

        it('should fail if the backup code is invalid', async () => {
            // Mock backup code verification to fail
            (mfaUtils.verifyBackupCode as jest.Mock).mockReturnValue(null);

            const result = await userService.verifyMfa({
                userId: 'user1',
                token: 'XXXX-XXXX',
                isBackupCode: true,
            });

            expect(result.success).toBe(false);
            expect(result.error).toBe('Invalid MFA token or backup code');
        });
    });

    describe('disableMfa', () => {
        it('should disable MFA for a user', async () => {
            // Mock user with MFA enabled
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaEnabled: true,
                    mfaSecret: 'test_secret',
                    mfaBackupCodes: ['AAAA-BBBB', 'CCCC-DDDD'],
                },
            });

            const result = await userService.disableMfa('user1');

            expect(result.success).toBe(true);
            expect(result.data).toBe(true);

            // Check that MFA was properly disabled
            expect(userService.update).toHaveBeenCalledWith('user1', {
                mfaEnabled: false,
                mfaSecret: undefined,
                mfaBackupCodes: [],
            });
        });

        it('should not allow disabling MFA for payment-enabled users', async () => {
            // Mock user with payment enabled
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaEnabled: true,
                    paymentEnabled: true,
                },
            });

            const result = await userService.disableMfa('user1');

            expect(result.success).toBe(false);
            expect(result.error).toBe('Cannot disable MFA for users with payment enabled');
        });
    });

    describe('create', () => {
        it('should initialize MFA as disabled for new users', async () => {
            // Mock the create method of the parent class
            const mockCreate = jest.fn().mockResolvedValue({
                success: true,
                data: mockUser,
            });
            userService.create = mockCreate;

            await userService.create({
                email: 'test@example.com',
                password: 'password123',
            });

            expect(mockCreate).toHaveBeenCalledWith(
                expect.objectContaining({
                    mfaEnabled: false,
                    paymentEnabled: false,
                })
            );
        });

        it('should set MFA as required for payment-enabled users', async () => {
            // Mock the create method of the parent class
            const mockCreate = jest.fn().mockResolvedValue({
                success: true,
                data: mockUser,
            });
            userService.create = mockCreate;

            await userService.create({
                email: 'test@example.com',
                password: 'password123',
                paymentEnabled: true,
            });

            expect(mockCreate).toHaveBeenCalledWith(
                expect.objectContaining({
                    paymentEnabled: true,
                    mfaRequired: true,
                })
            );
        });
    });

    describe('update', () => {
        it('should require MFA before enabling payments', async () => {
            const result = await userService.update('user1', {
                paymentEnabled: true,
            });

            expect(result.success).toBe(false);
            expect(result.error).toBe('MFA must be enabled before enabling payments');
        });

        it('should allow enabling payments when MFA is enabled', async () => {
            // Mock user with MFA enabled
            userService.findById = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaEnabled: true,
                },
            });

            // Mock the update method of the parent class
            const mockUpdateSuper = jest.fn().mockResolvedValue({
                success: true,
                data: {
                    ...mockUser,
                    mfaEnabled: true,
                    paymentEnabled: true,
                },
            });
            jest.spyOn(Object.getPrototypeOf(UserService.prototype), 'update')
                .mockImplementation(mockUpdateSuper);

            const result = await userService.update('user1', {
                paymentEnabled: true,
            });

            expect(result.success).toBe(true);
        });
    });
}); 