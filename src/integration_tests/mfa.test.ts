import request from 'supertest';
import express from 'express';
import * as speakeasy from 'speakeasy';
import { UserService } from '../services/UserService';
import { setupTestApp } from './utils/setupTestApp';

describe('MFA Integration Tests', () => {
    let app: express.Application;
    let userService: UserService;
    let authToken: string;
    let userId: string;
    let mfaSecret: string;

    beforeAll(async () => {
        app = await setupTestApp();
        userService = new UserService();
    });

    beforeEach(async () => {
        // Create a test user
        const createUserResponse = await request(app)
            .post('/api/users')
            .send({
                email: 'mfa_test@example.com',
                password: 'SecurePassword12345',
                username: 'mfa_test_user',
            });

        userId = createUserResponse.body.id;

        // Login
        const loginResponse = await request(app)
            .post('/api/auth/login')
            .send({
                email: 'mfa_test@example.com',
                password: 'SecurePassword12345',
            });

        authToken = loginResponse.body.token;
    });

    afterEach(async () => {
        // Clean up test user
        await request(app)
            .delete(`/api/users/${userId}`)
            .set('Authorization', `Bearer ${authToken}`);
    });

    describe('MFA Setup Flow', () => {
        it('should successfully setup MFA for a user', async () => {
            // Setup MFA
            const setupResponse = await request(app)
                .post(`/api/users/${userId}/mfa/setup`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(setupResponse.body).toHaveProperty('secret');
            expect(setupResponse.body).toHaveProperty('otpauth_url');
            expect(setupResponse.body).toHaveProperty('backup_codes');
            expect(setupResponse.body).toHaveProperty('qrcode');

            mfaSecret = setupResponse.body.secret;

            // Generate a valid TOTP token using the secret
            const token = speakeasy.totp({
                secret: mfaSecret,
                encoding: 'base32',
            });

            // Enable MFA with valid token
            const enableResponse = await request(app)
                .post(`/api/users/${userId}/mfa/enable`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({ token })
                .expect(200);

            expect(enableResponse.body).toBe(true);

            // Verify user has MFA enabled
            const userResponse = await request(app)
                .get(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(userResponse.body.mfaEnabled).toBe(true);
        });

        it('should reject invalid TOTP token during MFA setup', async () => {
            // Setup MFA
            await request(app)
                .post(`/api/users/${userId}/mfa/setup`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            // Try to enable MFA with invalid token
            const enableResponse = await request(app)
                .post(`/api/users/${userId}/mfa/enable`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({ token: '123456' })
                .expect(400);

            expect(enableResponse.body).toHaveProperty('message', 'Invalid MFA token');

            // Verify user still has MFA disabled
            const userResponse = await request(app)
                .get(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(userResponse.body.mfaEnabled).toBe(false);
        });
    });

    describe('MFA Login Flow', () => {
        beforeEach(async () => {
            // Setup and enable MFA for the test user
            const setupResponse = await request(app)
                .post(`/api/users/${userId}/mfa/setup`)
                .set('Authorization', `Bearer ${authToken}`);

            mfaSecret = setupResponse.body.secret;

            // Generate a valid TOTP token
            const token = speakeasy.totp({
                secret: mfaSecret,
                encoding: 'base32',
            });

            // Enable MFA
            await request(app)
                .post(`/api/users/${userId}/mfa/enable`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({ token });
        });

        it('should require MFA verification after login for MFA-enabled users', async () => {
            // Login
            const loginResponse = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'mfa_test@example.com',
                    password: 'SecurePassword12345',
                })
                .expect(200);

            expect(loginResponse.body).toHaveProperty('requiresMfa', true);
            expect(loginResponse.body).toHaveProperty('token');

            // Token should not have MFA verified yet
            const protectedResponse = await request(app)
                .get('/api/protected-resource')
                .set('Authorization', `Bearer ${loginResponse.body.token}`)
                .expect(403);

            expect(protectedResponse.body).toHaveProperty('message', 'MFA verification required');

            // Generate a valid TOTP token
            const token = speakeasy.totp({
                secret: mfaSecret,
                encoding: 'base32',
            });

            // Verify MFA
            const verifyResponse = await request(app)
                .post('/api/mfa/verify')
                .send({
                    userId,
                    token,
                })
                .expect(200);

            expect(verifyResponse.body).toHaveProperty('token');

            // Access protected resource with MFA-verified token
            await request(app)
                .get('/api/protected-resource')
                .set('Authorization', `Bearer ${verifyResponse.body.token}`)
                .expect(200);
        });

        it('should accept valid backup codes for MFA verification', async () => {
            // Login
            const loginResponse = await request(app)
                .post('/api/auth/login')
                .send({
                    email: 'mfa_test@example.com',
                    password: 'SecurePassword12345',
                })
                .expect(200);

            // Get the user's backup codes
            const backupCodesResponse = await request(app)
                .get(`/api/users/${userId}/mfa/backup-codes`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            const backupCode = backupCodesResponse.body[0];

            // Verify MFA with backup code
            const verifyResponse = await request(app)
                .post('/api/mfa/verify')
                .send({
                    userId,
                    token: backupCode,
                    isBackupCode: true,
                })
                .expect(200);

            expect(verifyResponse.body).toHaveProperty('token');

            // Access protected resource with MFA-verified token
            await request(app)
                .get('/api/protected-resource')
                .set('Authorization', `Bearer ${verifyResponse.body.token}`)
                .expect(200);

            // Backup code should be removed from available codes
            const updatedBackupCodesResponse = await request(app)
                .get(`/api/users/${userId}/mfa/backup-codes`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(updatedBackupCodesResponse.body).not.toContain(backupCode);
        });
    });

    describe('Payment Access with MFA', () => {
        it('should block payment operations until MFA is verified', async () => {
            // Enable payment for user
            await request(app)
                .patch(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    mfaEnabled: true, // MFA must be enabled before payments
                    paymentEnabled: true,
                })
                .expect(200);

            // Access to payment-related endpoints should be blocked without MFA verification
            await request(app)
                .post('/api/payments/process')
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    amount: 100,
                    currency: 'USD',
                })
                .expect(403);

            // Generate a valid TOTP token
            const token = speakeasy.totp({
                secret: mfaSecret,
                encoding: 'base32',
            });

            // Verify MFA
            const verifyResponse = await request(app)
                .post('/api/mfa/verify')
                .send({
                    userId,
                    token,
                })
                .expect(200);

            // Access payment-related endpoint with MFA-verified token
            await request(app)
                .post('/api/payments/process')
                .set('Authorization', `Bearer ${verifyResponse.body.token}`)
                .send({
                    amount: 100,
                    currency: 'USD',
                })
                .expect(200);
        });
    });

    describe('MFA Management', () => {
        beforeEach(async () => {
            // Setup and enable MFA for the test user
            const setupResponse = await request(app)
                .post(`/api/users/${userId}/mfa/setup`)
                .set('Authorization', `Bearer ${authToken}`);

            mfaSecret = setupResponse.body.secret;

            // Generate a valid TOTP token
            const token = speakeasy.totp({
                secret: mfaSecret,
                encoding: 'base32',
            });

            // Enable MFA
            await request(app)
                .post(`/api/users/${userId}/mfa/enable`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({ token });
        });

        it('should allow regenerating backup codes', async () => {
            // Get original backup codes
            const originalCodesResponse = await request(app)
                .get(`/api/users/${userId}/mfa/backup-codes`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            const originalCodes = originalCodesResponse.body;

            // Regenerate backup codes
            const regenerateResponse = await request(app)
                .post(`/api/users/${userId}/mfa/backup-codes/regenerate`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            const newCodes = regenerateResponse.body;

            expect(Array.isArray(newCodes)).toBe(true);
            expect(newCodes.length).toBeGreaterThan(0);

            // New codes should be different from original codes
            const hasOverlap = newCodes.some(code => originalCodes.includes(code));
            expect(hasOverlap).toBe(false);
        });

        it('should prevent disabling MFA when payment is enabled', async () => {
            // Enable payment
            await request(app)
                .patch(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .send({
                    paymentEnabled: true,
                })
                .expect(200);

            // Try to disable MFA
            const disableResponse = await request(app)
                .post(`/api/users/${userId}/mfa/disable`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(400);

            expect(disableResponse.body).toHaveProperty('message', 'Cannot disable MFA for users with payment enabled');

            // Verify user still has MFA enabled
            const userResponse = await request(app)
                .get(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(userResponse.body.mfaEnabled).toBe(true);
        });

        it('should allow disabling MFA when payment is not enabled', async () => {
            // Disable MFA
            await request(app)
                .post(`/api/users/${userId}/mfa/disable`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            // Verify user no longer has MFA enabled
            const userResponse = await request(app)
                .get(`/api/users/${userId}`)
                .set('Authorization', `Bearer ${authToken}`)
                .expect(200);

            expect(userResponse.body.mfaEnabled).toBe(false);
            expect(userResponse.body.mfaSecret).toBeNull();
            expect(userResponse.body.mfaBackupCodes).toEqual([]);
        });
    });
}); 