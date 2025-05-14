import * as speakeasy from 'speakeasy';
import {
    generateMfaSecret,
    generateBackupCodes,
    verifyToken,
    verifyBackupCode
} from '../mfa';

describe('MFA Utilities', () => {
    describe('generateMfaSecret', () => {
        it('should generate a valid secret for a user', () => {
            const result = generateMfaSecret('testuser');

            // Check structure of result
            expect(result).toHaveProperty('secret');
            expect(result).toHaveProperty('otpauth_url');
            expect(result).toHaveProperty('backup_codes');

            // Check that secret is a valid base32 string
            expect(typeof result.secret).toBe('string');
            expect(result.secret.length).toBeGreaterThan(16);

            // Check that otpauth URL contains username and issuer
            expect(result.otpauth_url).toContain('testuser');
            expect(result.otpauth_url).toContain('Visual_DM');

            // Check backup codes generation
            expect(Array.isArray(result.backup_codes)).toBe(true);
            expect(result.backup_codes.length).toBe(10);
        });

        it('should use custom issuer when provided', () => {
            const result = generateMfaSecret('testuser', 'CustomApp');
            expect(result.otpauth_url).toContain('CustomApp');
        });
    });

    describe('generateBackupCodes', () => {
        it('should generate the specified number of backup codes', () => {
            const codes = generateBackupCodes(5);
            expect(codes.length).toBe(5);
        });

        it('should generate 10 backup codes by default', () => {
            const codes = generateBackupCodes();
            expect(codes.length).toBe(10);
        });

        it('should generate backup codes in the XXXX-XXXX format', () => {
            const codes = generateBackupCodes(3);
            const regex = /^[A-F0-9]{4}-[A-F0-9]{4}$/;

            codes.forEach(code => {
                expect(code).toMatch(regex);
            });
        });

        it('should generate unique backup codes', () => {
            const codes = generateBackupCodes(20);
            const uniqueCodes = new Set(codes);
            expect(uniqueCodes.size).toBe(20);
        });
    });

    describe('verifyToken', () => {
        it('should validate a correct token', () => {
            // Generate a secret
            const secret = speakeasy.generateSecret({ length: 20 });

            // Generate a token using the same secret
            const token = speakeasy.totp({
                secret: secret.base32,
                encoding: 'base32',
            });

            // Verify the token
            const result = verifyToken(token, secret.base32);
            expect(result).toBe(true);
        });

        it('should reject an invalid token', () => {
            const secret = speakeasy.generateSecret({ length: 20 }).base32;
            const result = verifyToken('123456', secret);
            expect(result).toBe(false);
        });

        it('should allow a token with small time drift', () => {
            // Mock implementation since we can't easily test time drift in a unit test
            const mockVerify = jest.spyOn(speakeasy.totp, 'verify');
            mockVerify.mockReturnValue(true);

            expect(verifyToken('123456', 'testsecret')).toBe(true);

            // Check that window parameter was passed
            expect(mockVerify).toHaveBeenCalledWith(
                expect.objectContaining({ window: 1 })
            );

            mockVerify.mockRestore();
        });
    });

    describe('verifyBackupCode', () => {
        const validCodes = ['ABCD-1234', 'EFGH-5678', 'IJKL-9012'];

        it('should validate a matching backup code', () => {
            const result = verifyBackupCode('ABCD-1234', validCodes);
            expect(result).toBe('ABCD-1234');
        });

        it('should validate a matching backup code regardless of casing', () => {
            const result = verifyBackupCode('abcd-1234', validCodes);
            expect(result).toBe('ABCD-1234');
        });

        it('should validate a matching backup code without hyphen', () => {
            const result = verifyBackupCode('ABCD1234', validCodes);
            expect(result).toBe('ABCD-1234');
        });

        it('should validate a matching backup code with extra whitespace', () => {
            const result = verifyBackupCode(' ABCD-1234 ', validCodes);
            expect(result).toBe('ABCD-1234');
        });

        it('should reject an invalid backup code', () => {
            const result = verifyBackupCode('XXXX-9999', validCodes);
            expect(result).toBeNull();
        });
    });
}); 