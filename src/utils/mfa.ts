import * as speakeasy from 'speakeasy';
import * as qrcode from 'qrcode';
import * as crypto from 'crypto';

/**
 * Generate a new MFA secret for a user
 * @param username User's username for labeling the authenticator app
 * @param issuer Name of the application/service
 * @returns An object containing secret, URI for QR code, and backup codes
 */
export function generateMfaSecret(username: string, issuer: string = 'Visual_DM') {
    // Generate a secret
    const secret = speakeasy.generateSecret({
        length: 20,
        name: `${issuer}:${username}`,
        issuer: issuer
    });

    return {
        secret: secret.base32,
        otpauth_url: secret.otpauth_url,
        backup_codes: generateBackupCodes()
    };
}

/**
 * Generate backup codes for MFA recovery
 * @param count Number of backup codes to generate (default: 10)
 * @returns Array of unique backup codes
 */
export function generateBackupCodes(count: number = 10): string[] {
    const codes: string[] = [];

    for (let i = 0; i < count; i++) {
        const buffer = crypto.randomBytes(4);
        // Generate 8-character hexadecimal code
        const code = buffer.toString('hex').toUpperCase();
        // Format as XXXX-XXXX for readability
        codes.push(`${code.substring(0, 4)}-${code.substring(4, 8)}`);
    }

    return codes;
}

/**
 * Generate a QR code data URL for an OTP auth URL
 * @param otpauth_url The OTP auth URL to encode
 * @returns A data URL of the QR code
 */
export async function generateQrCode(otpauth_url: string): Promise<string> {
    try {
        return await qrcode.toDataURL(otpauth_url);
    } catch (error) {
        console.error('Error generating QR code:', error);
        throw new Error('Failed to generate QR code');
    }
}

/**
 * Verify a TOTP token against a user's secret
 * @param token The token provided by the user
 * @param secret The user's MFA secret
 * @returns Boolean indicating whether the token is valid
 */
export function verifyToken(token: string, secret: string): boolean {
    return speakeasy.totp.verify({
        secret: secret,
        encoding: 'base32',
        token: token,
        window: 1 // Allow a one-step time drift (30 seconds before/after)
    });
}

/**
 * Verify a backup code
 * @param providedCode The backup code provided by the user
 * @param validCodes Array of valid backup codes
 * @returns The matching backup code if valid, null otherwise
 */
export function verifyBackupCode(providedCode: string, validCodes: string[]): string | null {
    // Normalize the provided code
    const normalizedCode = providedCode.trim().toUpperCase();

    // Find the matching code
    const matchingCode = validCodes.find(code =>
        code === normalizedCode || code === normalizedCode.replace('-', ''));

    return matchingCode || null;
} 