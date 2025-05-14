import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';

export interface MfaSetupData {
    secret: string;
    otpauth_url: string;
    backup_codes: string[];
    qrcode?: string;
}

export interface VerifyMfaData {
    userId: string;
    token: string;
    isBackupCode?: boolean;
}

export interface VerifyMfaResponse {
    token: string;
}

const handleResponse = async (response: Response) => {
    if (!response.ok) {
        const error = await response.json();
        throw new Error(error.message || 'An error occurred');
    }
    return response.json();
};

export const useMfaApi = () => {
    const queryClient = useQueryClient();

    /**
     * Setup MFA for a user
     */
    const setupMfa = async (userId: string): Promise<MfaSetupData> => {
        const response = await fetch(`/api/users/${userId}/mfa/setup`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        return handleResponse(response);
    };

    /**
     * Enable MFA after verification
     */
    const enableMfa = async ({ userId, token }: { userId: string; token: string }): Promise<boolean> => {
        const response = await fetch(`/api/users/${userId}/mfa/enable`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            },
            body: JSON.stringify({ token })
        });
        return handleResponse(response);
    };

    /**
     * Verify MFA token during authentication
     */
    const verifyMfa = async (data: VerifyMfaData): Promise<VerifyMfaResponse> => {
        const response = await fetch(`/api/mfa/verify`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(data)
        });
        return handleResponse(response);
    };

    /**
     * Disable MFA for a user
     */
    const disableMfa = async (userId: string): Promise<boolean> => {
        const response = await fetch(`/api/users/${userId}/mfa/disable`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        return handleResponse(response);
    };

    /**
     * Get backup codes for MFA
     */
    const getBackupCodes = async (userId: string): Promise<string[]> => {
        const response = await fetch(`/api/users/${userId}/mfa/backup-codes`, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        return handleResponse(response);
    };

    /**
     * Regenerate backup codes for MFA
     */
    const regenerateBackupCodes = async (userId: string): Promise<string[]> => {
        const response = await fetch(`/api/users/${userId}/mfa/backup-codes/regenerate`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'Authorization': `Bearer ${localStorage.getItem('token')}`
            }
        });
        return handleResponse(response);
    };

    // React Query hooks
    const useSetupMfa = () =>
        useMutation({
            mutationFn: setupMfa,
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: ['user'] });
            },
        });

    const useEnableMfa = () =>
        useMutation({
            mutationFn: enableMfa,
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: ['user'] });
            },
        });

    const useVerifyMfa = () =>
        useMutation({
            mutationFn: verifyMfa,
        });

    const useDisableMfa = () =>
        useMutation({
            mutationFn: disableMfa,
            onSuccess: () => {
                queryClient.invalidateQueries({ queryKey: ['user'] });
            },
        });

    const useBackupCodes = (userId: string) =>
        useQuery({
            queryKey: ['mfa', 'backupCodes', userId],
            queryFn: () => getBackupCodes(userId),
            enabled: !!userId,
        });

    const useRegenerateBackupCodes = () =>
        useMutation({
            mutationFn: regenerateBackupCodes,
            onSuccess: (_, userId) => {
                queryClient.invalidateQueries({ queryKey: ['mfa', 'backupCodes', userId] });
            },
        });

    return {
        // Direct API methods
        setupMfa,
        enableMfa,
        verifyMfa,
        disableMfa,
        getBackupCodes,
        regenerateBackupCodes,

        // React Query hooks
        useSetupMfa,
        useEnableMfa,
        useVerifyMfa,
        useDisableMfa,
        useBackupCodes,
        useRegenerateBackupCodes,
    };
}; 