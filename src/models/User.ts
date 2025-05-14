/**
 * User model definition
 */
export interface User {
    id: string;
    email: string;
    password: string;
    firstName?: string;
    lastName?: string;
    role: 'user' | 'admin';

    // MFA related fields
    mfaEnabled?: boolean;
    mfaSecret?: string;
    mfaBackupCodes?: string[];
    mfaVerified?: boolean;

    // Payment related fields
    paymentEnabled?: boolean;

    // Timestamps
    createdAt?: Date;
    updatedAt?: Date;
} 